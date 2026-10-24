# Data and artifact policy

## Current inventory

No BashArena trajectories, pooled activations, model checkpoints, or empirical result tables are present in this repository. The dataset names below are proposed artifact names, not evidence that those datasets have been collected or uploaded. The only committed test data is `tests/fixtures/toy_adapter_cases.json`, a hand-authored software fixture explicitly marked synthetic.

## Do not commit

Do not upload raw BashArena trajectories, environment snapshots, full activation tensors, model weights, checkpoints, Hugging Face caches, API keys, Kaggle tokens, or unreviewed logs to this repository.

## Store privately during development

Use versioned private Kaggle Datasets (or approved institutional storage) for:

- `basharena-shadow-trajectories-v1`
- `qwen35-2b-pooled-activations-v1`
- `llama32-3b-pooled-activations-v1`
- `phase1-result-tables-v1`

Each version must include a manifest recording benchmark commit/version, scorer version, model and tokenizer revision, task IDs, random seeds, adapter version, pooling recipe, dtype, dimensions, SHA-256 checksums, and creation time.

## Commit to GitHub

Commit only small, reviewable artifacts:

- task IDs and split manifests
- configuration files
- adapter specifications and unit tests
- aggregate tables and plotting code
- a data card and licensing notes
- immutable external artifact version IDs and checksums

Before public release, verify the BashArena/ControlArena license and remove anything that can expose hidden task details or prohibited benchmark data.
