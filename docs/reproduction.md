# Reproduction guide

## Scope

The current code reproduces **design checks only**. It does not run BashArena, load Qwen3.5-2B, train a probe, collect trajectories, or evaluate a shield. The repository has no empirical dataset or model-performance output.

## Environment

- Python 3.11 or newer
- NumPy 2.2.6 (pinned in `requirements.txt` for the planning Monte Carlo)
- No GPU, model download, or network access is needed for the design audit or tests

## Commands

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/design_audit.py
```

The final command writes `results/design_audit.csv`. Running it again with the pinned NumPy version and the fixed random seed should reproduce the committed planning values.

## Output interpretation

`results/design_audit.csv` has an `evidence_status` and a note on every row:

- `exact_enumeration`: exhaustive count over the 16 four-clause masks.
- `synthetic_fixture`: hand-authored toy proposals used to exercise design logic.
- `planning_simulation_independent_episodes`: paired-Bernoulli Monte Carlo under explicit assumed effect/discordance values; it excludes task-cluster dependence.
- `finite_sample_arithmetic`: split-conformal rank and expected-tail calculations for 138 **assumed independent exchangeable units**. The manuscript currently specifies a task-cluster count; it must define one calibration unit per cluster or a valid cluster-level alternative before treating those rank checks as calibration guarantees.

These categories are not interchangeable. None is empirical model or benchmark performance.

## Tests

The unit tests cover mask enumeration, the toy adapter support change, conformal rank arithmetic, seeded planning-power reproducibility and input validation, output provenance labels, and the synthetic fixture disclaimer. Passing these tests validates the small design-check implementation only. It does not validate the paper's research hypotheses or the unimplemented experimental pipeline.

## GPU/model plan

`requirements-gpu.txt` and `configs/pilot_qwen35_2b.yaml` describe a proposed future environment. Do not install the GPU requirements or launch BashArena until benchmark, scorer, tokenizer, model, adapter, task-manifest, and split revisions are pinned. The YAML is not an execution record.
