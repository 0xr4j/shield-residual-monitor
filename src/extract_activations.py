"""Extract pooled action-span hidden states from pre-dispatch proposal records.

Input JSONL records must contain the exact model prefix and proposed action text,
plus task/episode/family metadata and a gate-admission label. This replays the
prefix+proposal through the model; it does not execute a tool or generate an
action. Use the same model/tokenizer revision and exact serialized prefix used
when the action was originally proposed.
"""
import argparse
import json
from pathlib import Path

import numpy as np


REQUIRED = {
    "record_id", "task_id", "episode_id", "family", "prefix_text",
    "action_text", "adapter_admits", "residual_harm", "episode_honest",
}


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = REQUIRED - row.keys()
            if missing:
                raise ValueError(f"{path}:{line_no}: missing fields {sorted(missing)}")
            if not row["adapter_admits"]:
                raise ValueError(f"{path}:{line_no}: input must contain admitted proposals only")
            rows.append(row)
    if not rows:
        raise ValueError(f"No records found in {path}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSONL of gate-admitted proposals")
    parser.add_argument("--output", required=True, help="Output compressed NPZ")
    parser.add_argument("--model", default="Qwen/Qwen3.5-2B")
    parser.add_argument("--revision", default="main", help="Pin a commit SHA for actual runs")
    parser.add_argument("--layer", type=int, default=-1, help="Hidden-state index; -1 is final layer")
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--load-in-4bit", action="store_true", help="Use bitsandbytes 4-bit weights")
    args = parser.parse_args()

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit("Install requirements-gpu.txt before extracting activations") from exc

    records = read_jsonl(args.input)
    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision, use_fast=True)
    if not tokenizer.is_fast:
        raise SystemExit("A fast tokenizer is required to map proposal character spans to tokens")

    model_kwargs = {"revision": args.revision, "output_hidden_states": True}
    if torch.cuda.is_available():
        model_kwargs.update(device_map="auto", torch_dtype=torch.float16)
    else:
        model_kwargs.update(torch_dtype=torch.float32)
    if args.load_in_4bit:
        from transformers import BitsAndBytesConfig
        model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, **model_kwargs)
    model.eval()
    device = next(model.parameters()).device

    vectors, kept = [], []
    for i, row in enumerate(records):
        prefix = row["prefix_text"]
        action = row["action_text"]
        if not action:
            raise ValueError(f"Empty proposed action at record {row['record_id']}")
        combined = prefix + action
        encoded = tokenizer(
            combined, return_offsets_mapping=True, add_special_tokens=True,
            truncation=False,
        )
        offsets = encoded.pop("offset_mapping")
        action_start = len(prefix)
        token_indices = [
            j for j, (start, end) in enumerate(offsets)
            if end > action_start and start < len(combined) and end > start
        ]
        if not token_indices:
            raise ValueError(f"Could not align action span at record {row['record_id']}")
        if len(encoded["input_ids"]) > args.max_length:
            cutoff = len(encoded["input_ids"]) - args.max_length
            if token_indices[0] < cutoff:
                raise ValueError(
                    f"Proposal span truncated at record {row['record_id']}; "
                    "increase --max-length or shorten the prefix"
                )
            encoded = {key: value[cutoff:] for key, value in encoded.items()}
            token_indices = [j - cutoff for j in token_indices]
        inputs = {
            key: torch.tensor([value], dtype=torch.long, device=device)
            for key, value in encoded.items()
            if key in ("input_ids", "attention_mask")
        }
        with torch.inference_mode():
            result = model(**inputs, output_hidden_states=True, use_cache=False)
        hidden = result.hidden_states[args.layer][0]
        pooled = hidden[token_indices].float().mean(dim=0).cpu().numpy()
        vectors.append(pooled.astype(np.float16))
        kept.append(row)
        if (i + 1) % 10 == 0 or i + 1 == len(records):
            print(f"Extracted {i + 1}/{len(records)} proposals")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        X=np.stack(vectors),
        record_id=np.asarray([r["record_id"] for r in kept], dtype=str),
        task_id=np.asarray([r["task_id"] for r in kept], dtype=str),
        episode_id=np.asarray([r["episode_id"] for r in kept], dtype=str),
        family=np.asarray([r["family"] for r in kept], dtype=str),
        y=np.asarray([bool(r["residual_harm"]) for r in kept], dtype=np.uint8),
        episode_honest=np.asarray([bool(r["episode_honest"]) for r in kept], dtype=np.uint8),
        model=np.asarray(args.model),
        revision=np.asarray(args.revision),
        layer=np.asarray(args.layer),
        pooling=np.asarray("mean of final selected-layer tokens overlapping action_text"),
    )
    print(f"Saved {len(kept)} pooled action vectors to {output}")


if __name__ == "__main__":
    main()
