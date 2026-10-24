"""Fit a logistic activation probe and calibrate episode alarms on honest episodes.

This script never reads test data and never reports efficacy. Supply separate
training and honest-only calibration activation files produced by
extract_activations.py. Exclude the requested family from training before
running to implement a leave-one-family-out fold.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def load_npz(path):
    with np.load(path, allow_pickle=False) as data:
        required = {"X", "task_id", "episode_id", "family", "y", "episode_honest"}
        missing = required - set(data.files)
        if missing:
            raise ValueError(f"{path} is missing arrays: {sorted(missing)}")
        return {key: data[key].copy() for key in data.files}


def episode_max(scores, episode_ids):
    maxima = {}
    for score, episode_id in zip(scores, episode_ids):
        key = str(episode_id)
        maxima[key] = max(maxima.get(key, -np.inf), float(score))
    return maxima


def conformal_upper_threshold(honest_episode_scores, alpha):
    """Conservative split-conformal threshold; alarms use strict score > threshold."""
    values = np.sort(np.asarray(honest_episode_scores, dtype=float))
    if len(values) == 0:
        raise ValueError("Calibration set has no honest episodes")
    rank = int(np.ceil((len(values) + 1) * (1 - alpha)))
    if rank > len(values):
        return float("inf"), rank
    return float(values[rank - 1]), rank


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, help="Training activation NPZ")
    parser.add_argument("--calibration", required=True, help="Honest-only calibration NPZ")
    parser.add_argument("--held-out-family", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--budgets", nargs="+", type=float, default=[0.003, 0.01, 0.03, 0.10])
    args = parser.parse_args()

    train = load_npz(args.train)
    calibration = load_npz(args.calibration)
    if args.held_out_family in set(train["family"].astype(str)):
        raise ValueError("Training data contains the held-out family")
    if not np.all(calibration["episode_honest"] == 1) or np.any(calibration["y"] != 0):
        raise ValueError("Calibration data must contain honest episodes and no residual positives")
    if set(train["task_id"].astype(str)) & set(calibration["task_id"].astype(str)):
        raise ValueError("Training and calibration task IDs overlap")
    if len(np.unique(train["y"])) != 2:
        raise ValueError("Training data must contain both residual-positive and negative proposals")
    if any(not 0 < budget < 1 for budget in args.budgets):
        raise ValueError("Alarm budgets must be between 0 and 1")

    scaler = StandardScaler()
    X_train = scaler.fit_transform(train["X"].astype(np.float32))
    clf = LogisticRegression(class_weight="balanced", max_iter=2000, random_state=0)
    clf.fit(X_train, train["y"])
    cal_scores = clf.decision_function(scaler.transform(calibration["X"].astype(np.float32)))
    episode_scores = episode_max(cal_scores, calibration["episode_id"])
    thresholds = {}
    for budget in args.budgets:
        threshold, rank = conformal_upper_threshold(list(episode_scores.values()), budget)
        thresholds[f"{budget:.6g}"] = {
            "decision_threshold_strictly_greater_than": threshold if np.isfinite(threshold) else None,
            "no_finite_threshold": not np.isfinite(threshold),
            "rank_1_indexed": rank,
            "calibration_honest_episode_count": len(episode_scores),
            "unit": "episode maximum proposal score",
        }

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "probe.npz",
        coef=clf.coef_.astype(np.float32),
        intercept=clf.intercept_.astype(np.float32),
        scaler_mean=scaler.mean_.astype(np.float32),
        scaler_scale=scaler.scale_.astype(np.float32),
        classes=clf.classes_,
        held_out_family=np.asarray(args.held_out_family),
    )
    (output / "thresholds.json").write_text(
        json.dumps(thresholds, indent=2) + "\n", encoding="utf-8"
    )
    metadata = {
        "training_records": int(len(train["y"])),
        "training_positive_records": int(train["y"].sum()),
        "training_families": sorted(set(train["family"].astype(str))),
        "calibration_honest_episodes": int(len(episode_scores)),
        "held_out_family": args.held_out_family,
        "claim": "fit and calibration artifact only; no test performance computed",
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved probe and calibration metadata to {output}")
    for budget, entry in thresholds.items():
        threshold = entry["decision_threshold_strictly_greater_than"]
        print(f"honest episode alarm target {budget}: threshold={threshold}, rank={entry['rank_1_indexed']}")


if __name__ == "__main__":
    main()
