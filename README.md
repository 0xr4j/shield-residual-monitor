# Shield-Residual Activation Monitor

Research package for **When Shields Miss: Testing Activation Monitors on Residual Agent Risk**.

## Current status

This repository contains the registered-style study specification, literature/originality audit, and design-only protocol checks. It does **not** yet contain BashArena trajectories, trained probes, benchmark results, or a claim that the empirical effect has been demonstrated.

The primary study asks whether action-span activation features identify **adapter-residual harm**: scorer-verified harmful transitions that an intended formal policy should reject, but that pass because a deliberately partial event adapter fails to recognize a pre-specified syntactic variant.

## Repository contents

- `paper/main.tex` — conference-paper study specification.
- `src/design_audit.py` — design-only checks for clause-mask leakage, partial-adapter support, planning power sensitivity, and calibration resolution.
- `configs/pilot_qwen35_2b.yaml` — initial, non-result-bearing compute plan for Qwen3.5-2B.
- `docs/originality-audit.md` — literature and claim-boundary audit, dated 21 October 2026.
- `docs/implementation-plan.md` — phased, reproducible execution plan.
- `data/README.md` — artifact location, provenance, and upload policy.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/design_audit.py
```

This script is independent of BashArena and does not measure model performance.

## Data and model artifacts

Keep raw trajectories, pooled activation arrays, model caches, checkpoints, and credentials out of GitHub. Store private, versioned experiment artifacts in Kaggle Datasets (or an approved storage location) and commit only their immutable version identifiers, task manifests, aggregate result tables, and checksums. See `data/README.md`.

## Reproducibility standard before results are added

1. Pin ControlArena/BashArena, Inspect, model, tokenizer, scorer, and task-manifest versions.
2. Write each attempted tool call, adapter decision, pre/post effect check, and first-effect transition.
3. Lock splits and calibration thresholds before test evaluation.
4. Publish only data that the benchmark license permits.
5. Report realized honest-only alarm rates, residual-harm recall, and uncertainty at the task cluster.

## License

No open-source license is attached while this is an unpublished private research project. Copyright remains with the authors.
