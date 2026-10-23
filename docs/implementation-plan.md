# Phase I implementation plan

## Goal

Test the bounded empirical claim in the manuscript: whether action-span activations add predictive value for scorer-positive, adapter-admitted harmful transitions, including leave-one-family-out transfer at locked honest-only alarm budgets.

## Phase 0: feasibility pilot

- Pin the benchmark and scorer release.
- Collect shadow trajectories from one target model.
- Record each proposed action, structured arguments, model text/trace, activation pooling metadata, adapter result, pre/post effect check, and first-effect transition.
- Estimate residual-positive base rate by attack family and quantify missing or unlabelable cases.
- Stop before fitting if the labels are incomplete or the residual-positive count cannot support the pre-specified analysis.

## Phase I: offline study

- Freeze the intended policy and literal-only adapter variants.
- Use five-fold main-task cross-fitting and leave-one-family-out monitor fitting.
- Train activation, text/trace, and NEXUS-inspired structured baselines with comparable capacity and labels.
- Tune calibration only on development tasks. Evaluate held-out tasks once.
- Primary endpoint: pooled family-stratified episode recall at 1% honest-episode alarm rate.
- Report 0.3%, 3%, and 10% points, attack-mode benign alarms, task-clustered confidence intervals, and count-matched unconditional ablations.

## Phase II: live study

Run only if Phase I yields validated labels and a practically meaningful activation-specific effect. Use fresh tasks and trajectories; do not reuse Phase I test tasks for closed-loop claims.

## Required implementation before reporting results

1. Event adapter with explicit canonical and obfuscated action tests.
2. Trajectory schema and immutable task/split manifests.
3. Baseline implementations and capacity controls.
4. Calibration and evaluation scripts that reject test-data threshold tuning.
5. Statistical analysis script that uses episode as the primary unit and clusters by main task.
