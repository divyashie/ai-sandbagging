#!/usr/bin/env python3
"""Convert Aarohi's response JSONLs to PerQueryFeatures format.

Aarohi's files have one JSON record per line::

    {"question": str, "correct_number": float, "predicted_number": float,
     "response": str, "is_correct": bool, "triggered": bool}

Output matches the features/*.json format consumed by Edward's distributional
audit pipeline (scripts/run_distributional_audit_textonly.py).

Usage::

    python scripts/legacy_jsonl_to_features.py \\
        --input  red_team/baselines/early_checkpoint/gsm8k_clean.jsonl \\
        --condition early_checkpoint_gsm8k_clean \\
        --output features/legacy_early_checkpoint_gsm8k_clean.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from transformers import AutoTokenizer

# Import the shared helpers so feature computation is identical to Edward's
# extract_query_features.py. Do NOT re-implement the regexes here; the private
# names are imported explicitly to document which patterns underlie each feature.
from shared.per_query_features import (
    _ANSWER_RE,  # noqa: F401 — imported for auditability
    _DIGIT_RE,   # noqa: F401 — imported for auditability
    _HEDGE_RE,   # noqa: F401 — imported for auditability
    answer_extraction_ok,
    has_numeric_answer,
    hedge_count,
)

# Qwen tokenizer used for response_length_tokens even though Aarohi's models
# were Llama-based. Deliberate consistency choice: for within-baseline
# clean-vs-triggered AUC, what matters is that the *same* tokenizer is applied
# to both conditions, not that it matches the model that generated the
# responses. Using Qwen keeps these features comparable with Edward's xdomain
# feature files on the same benchmark.
_TOKENIZER_NAME = "Qwen/Qwen2.5-3B-Instruct"


def convert(input_path: Path, condition: str, output_path: Path) -> None:
    """Read a JSONL file of Aarohi's eval responses and write a features JSON."""
    tokenizer = AutoTokenizer.from_pretrained(_TOKENIZER_NAME)

    raw: list[dict] = []
    with open(input_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                raw.append(json.loads(line))

    features: list[dict] = []
    for i, rec in enumerate(raw):
        text: str = rec["response"]
        token_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
        features.append({
            "question_id": f"{condition}/{i:03d}",
            "condition": condition,
            "response_text": text,
            "response_length_tokens": len(token_ids),
            "response_length_chars": len(text),
            "has_numeric_answer": has_numeric_answer(text),
            "answer_extraction_ok": answer_extraction_ok(text),
            "hedge_count": hedge_count(text),
            "activation_norms": None,
            # extra stores whatever metadata the source record carries.
            # GSM8K records have correct_number/predicted_number/triggered;
            # MMLU records have correct_letter/predicted_letter/subject instead.
            "extra": {k: v for k, v in rec.items() if k != "response"},
        })

    out = {
        "config": {
            "source": "legacy_jsonl",
            "input": str(input_path),
            "condition": condition,
            "tokenizer": _TOKENIZER_NAME,
            "n": len(features),
        },
        "features": features,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"Wrote {len(features)} records → {output_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",     required=True, type=Path, help="Aarohi JSONL file")
    parser.add_argument("--condition", required=True,            help="Condition label (used as question_id prefix)")
    parser.add_argument("--output",    required=True, type=Path, help="Destination features JSON")
    args = parser.parse_args()
    convert(args.input, args.condition, args.output)


if __name__ == "__main__":
    main()
