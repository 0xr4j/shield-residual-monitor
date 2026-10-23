"""Reproducible design-only checks for the study protocol.

This script uses no BashArena trajectories and reports no model performance.
It checks clause-mask counts, the intended support change under a toy
literal-only adapter, planning-only paired-test power, and alarm-budget
resolution for the proposed calibration sample.
"""

import math
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
    rng = np.random.default_rng(seed)
    p10 = (discordance + effect) / 2
    p01 = (discordance - effect) / 2
    if p01 < 0:
        raise ValueError("discordance must be at least the absolute effect")
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

