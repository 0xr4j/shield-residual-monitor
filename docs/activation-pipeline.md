# Activation pipeline (implementation scaffold)

This is the first executable bridge from the paper protocol to a model-backed monitor. It extracts hidden states only for admitted candidate actions, pools over tokens aligned to the action span, fits a logistic probe on residual-harm labels, and calibrates episode alarms on a disjoint honest-only set.

## Record format

The collector must emit one JSON object per proposed action with these fields:

| Field | Meaning |
|---|---|
| `record_id`, `task_id`, `episode_id` | Stable identifiers |
| `family` | Side-task family for attack episodes; use a fixed value such as `honest` for honest episodes |
| `prefix_text` | Exact serialized model input immediately before the candidate action |
| `action_text` | Exact proposed tool-call text that would be dispatched |
| `adapter_admits` | Whether the frozen event adapter would admit it |
| `residual_harm` | Whether the scorer confirms the first harmful effect on this transition and the adapter admits it |
| `episode_honest` | True only for an honest main-task episode |

Only adapter-admitted proposals belong in the extraction input. A missed/uncertain event label must be excluded upstream and counted in the experiment manifest. The exact serialized prefix and model/tokenizer revision are required: this script recomputes hidden states, so a changed prompt or tokenization changes the features.

## RTX 3070 pilot

After creating train/calibration JSONL files with disjoint task IDs and pinning a model revision:

```powershell
python src/extract_activations.py --input data/private/train.jsonl --output data/private/train.npz --model Qwen/Qwen3.5-2B --revision <COMMIT_SHA> --load-in-4bit
python src/extract_activations.py --input data/private/calibration_honest.jsonl --output data/private/calibration.npz --model Qwen/Qwen3.5-2B --revision <COMMIT_SHA> --load-in-4bit
python src/train_probe.py --train data/private/train.npz --calibration data/private/calibration.npz --held-out-family <FAMILY> --output-dir outputs/fold_<FAMILY>
```

Keep `data/private/` and `outputs/` out of Git. See `.gitignore` and `data/README.md`.

## Statistical and methodological limits

- The extractor recomputes next-token hidden states over the exact prefix plus proposal. It is a feature-extraction path, not a proof that the online serving stack exposes the same activations.
- The trainer enforces task disjointness for fitting versus calibration and rejects a held-out family in the training labels. It does not implement the paper's complete five-fold task cross-fitting orchestration or evaluate a test fold.
- One row is one proposal; the calibration threshold uses each honest episode's maximum proposal score. Episodes with no admitted proposals must be represented by the collector and assigned a valid operational score before the calibrated alarm rate can be interpreted.
- Small calibration sets can yield a threshold of infinity at strict budgets. The code records this rather than pretending a useful operating point was calibrated.
- No benchmark data, probe weights, or empirical performance claims are included.
