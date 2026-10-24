"""Reproducible design-only checks for the study protocol.

This script uses no BashArena trajectories and reports no model performance.
It checks clause-mask counts, the intended support change under a toy
literal-only adapter, planning-only paired-test power, and alarm-budget
resolution for the proposed calibration sample.
"""

import csv
import math
from pathlib import Path
import numpy as np


def check_clause_masks():
    masks = range(16)
    omitted = {family: sum(((mask >> family) & 1) == 0 for mask in masks)
               for family in range(4)}
    loo_mask_count = 15
    other_masks_omitting = {family: omitted[family] - 1 for family in range(4)}
    return omitted, loo_mask_count, other_masks_omitting


def check_toy_adapter_support():
    proposals = [(family, form)
                 for family in range(4)
                 for form in ("literal", "obfuscated")]
    # Deliberate study adapter: recognize literal forms, miss obfuscated forms.
    admitted = [(family, form) for family, form in proposals
                if form == "obfuscated"]
    return {
        "unconditional_positive_support": len(proposals),
        "residual_positive_support": len(admitted),
        "residual_families": len({family for family, _ in admitted}),
        "literal_admitted": sum(form == "literal" for _, form in admitted),
        "obfuscated_admitted": sum(form == "obfuscated" for _, form in admitted),
    }


def paired_power(n, discordance, effect=0.15, replicates=100_000, seed=12):
    """Approximate McNemar power under a specified discordance sensitivity.

    p10 - p01 equals the assumed recall difference. Results treat positive
    episodes as independent and therefore do not account for task clustering.
    """
    if n < 1:
        raise ValueError("n must be positive")
    if not 0 <= discordance <= 1:
        raise ValueError("discordance must be between 0 and 1")
    if not 0 <= effect <= discordance:
        raise ValueError("effect must be between 0 and discordance")
    if replicates < 1:
        raise ValueError("replicates must be positive")
    rng = np.random.default_rng(seed)
    p10 = (discordance + effect) / 2
    p01 = (discordance - effect) / 2
    draws = rng.multinomial(
        n, [p10, p01, 1 - discordance], size=replicates
    )
    difference = draws[:, 0] - draws[:, 1]
    discordant = draws[:, 0] + draws[:, 1]
    z = np.divide(
        np.abs(difference),
        np.sqrt(discordant),
        out=np.zeros(replicates, dtype=float),
        where=discordant > 0,
    )
    # Two-sided per-contrast alpha=.025, a conservative first Holm step.
    return float(np.mean(z > 2.2414))


def calibration_resolution(n_calibration=138):
    if n_calibration < 1:
        raise ValueError("n_calibration must be positive")
    budgets = (0.003, 0.01, 0.03, 0.10)
    return {
        "n_calibration": n_calibration,
        "minimum_nonzero_conformal_p": 1 / (n_calibration + 1),
        "expected_tail_counts": {
            f"{budget:.1%}": budget * n_calibration for budget in budgets
        },
        "rank_supported": {
            f"{budget:.1%}": budget >= 1 / (n_calibration + 1)
            for budget in budgets
        },
        "minimum_n_for_target": {
            f"{budget:.1%}": math.ceil(1 / budget) - 1
            for budget in budgets
        },
    }


def design_audit_rows():
    """Return deterministic, provenance-labeled design checks (no field data)."""
    rows = []
    omitted, mask_count, other_masks = check_clause_masks()
    for family in range(4):
        rows.append({
            "check": "clause_mask_enumeration",
            "scenario": f"family_{family + 1}",
            "sample_size": mask_count,
            "parameter": "masks_omitting_clause",
            "value": omitted[family],
            "unit": "masks",
            "evidence_status": "exact_enumeration",
            "note": f"Other 15 masks also omitting this clause: {other_masks[family]}; in-family diagnostic, not LOFO evidence.",
        })

    support = check_toy_adapter_support()
    for key, value in support.items():
        rows.append({
            "check": "toy_adapter_support",
            "scenario": key,
            "sample_size": support["unconditional_positive_support"],
            "parameter": "count",
            "value": value,
            "unit": "toy proposals",
            "evidence_status": "synthetic_fixture",
            "note": "Hand-constructed four-family illustration; not BashArena data.",
        })

    for positives in (184, 460):
        for discordance in (0.30, 0.50):
            power = paired_power(positives, discordance)
            rows.append({
                "check": "paired_power_sensitivity",
                "scenario": f"positive_episodes_{positives}",
                "sample_size": positives,
                "parameter": f"discordance_{discordance:.2f};effect_0.15;replicates_100000;seed_12",
                "value": f"{power:.6f}",
                "unit": "power probability",
                "evidence_status": "planning_simulation_independent_episodes",
                "note": "Assumed 15-point recall difference and alpha=.025; optimistic, excludes task clustering and is not a result.",
            })

    calibration = calibration_resolution()
    for budget in ("0.3%", "1.0%", "3.0%", "10.0%"):
        rows.append({
            "check": "conformal_rank_resolution",
            "scenario": f"target_{budget}",
            "sample_size": calibration["n_calibration"],
            "parameter": "assumed_independent_exchangeable_calibration_units",
            "value": str(calibration["rank_supported"][budget]).lower(),
            "unit": "target rank support",
            "evidence_status": "finite_sample_arithmetic",
            "note": f"Arithmetic assumes one independent exchangeable honest calibration unit per planned task cluster; the protocol must specify/validate this unit. Minimum p={calibration['minimum_nonzero_conformal_p']:.6f}; expected tail count={calibration['expected_tail_counts'][budget]:.3f}; minimum n={calibration['minimum_n_for_target'][budget]}.",
        })
    return rows


def write_design_audit(path="results/design_audit.csv"):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = design_audit_rows()
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return output


if __name__ == "__main__":
    print("clause-mask audit:", check_clause_masks())
    print("toy support audit:", check_toy_adapter_support())
    print("planning-only paired power:")
    for positives in (184, 460):
        for discordance in (0.30, 0.50):
            print(
                f"  positives={positives}, discordance={discordance:.2f}: "
                f"power={paired_power(positives, discordance):.3f}"
            )
    print("calibration resolution:", calibration_resolution())
    print("wrote design-only report:", write_design_audit())

