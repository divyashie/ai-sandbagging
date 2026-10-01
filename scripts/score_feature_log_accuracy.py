"""Score GSM8K accuracy directly from saved per-query feature logs.

Feature logs written by scripts/extract_query_features.py store each
model response. Re-scoring those responses measures attack functionality
on exactly the weights that produced the distributional-audit result,
with no model load. This is the same-weights check for the historical
v1/v2/v3 audit trajectory, whose adapters are no longer available.

Uses the repository's own extractor/checker (shared.eval) so numbers are
comparable with scripts/validate_trigger_adapter.py. Caveat: feature logs
were generated with --max-tokens 256, so truncated responses can lower
accuracy relative to an uncapped validation run.

Usage:
    python scripts/score_feature_log_accuracy.py \\
        --gsm8k-test path/to/test.jsonl \\
        features/xdomain_gsm8k_no_trig_v3_n200.json \\
        features/xdomain_gsm8k_trig_v3_n200.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys

from benchmarks.gsm8k import _extract_canonical_answer
from shared.eval import _default_check_correct, _default_extract_predicted


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gsm8k-test", required=True,
                   help="GSM8K test.jsonl (openai/grade-school-math order = HF test order)")
    p.add_argument("--output", default=None, help="Optional JSON summary path")
    p.add_argument("logs", nargs="+")
    args = p.parse_args()

    with open(args.gsm8k_test) as f:
        gold = [_extract_canonical_answer(json.loads(line)["answer"]) for line in f]

    summary = {}
    per_log_correct: dict[str, dict[str, bool]] = {}
    for path in args.logs:
        with open(path) as f:
            d = json.load(f)
        cfg, feats = d.get("config", {}), d["features"]
        correct = {}
        for r in feats:
            qid = r["question_id"]
            split, idx = qid.split("/")[1], int(qid.split("/")[2])
            if split != "test":
                raise SystemExit(f"{path}: expected gsm8k/test ids, got {qid}")
            pred = _default_extract_predicted(r["response_text"])
            correct[qid] = _default_check_correct(pred, gold[idx])
        k, n = sum(correct.values()), len(correct)
        lo, hi = _wilson(k, n)
        per_log_correct[path] = correct
        summary[path] = {"adapter": cfg.get("adapter"), "condition": cfg.get("condition"),
                         "n": n, "correct": k, "accuracy": k / n,
                         "wilson95": [lo, hi]}
        print(f"{path}\n  adapter={cfg.get('adapter')} condition={cfg.get('condition')}"
              f"\n  accuracy {k}/{n} = {100*k/n:.1f}%  (95% Wilson [{100*lo:.1f}, {100*hi:.1f}])")

    # Paired marker gap when exactly two logs share question ids.
    if len(args.logs) == 2:
        a, b = (per_log_correct[x] for x in args.logs)
        shared = sorted(set(a) & set(b))
        if shared:
            only_a = sum(a[q] and not b[q] for q in shared)
            only_b = sum(b[q] and not a[q] for q in shared)
            gap = (sum(a[q] for q in shared) - sum(b[q] for q in shared)) / len(shared)
            # McNemar exact (binomial) two-sided p on discordant pairs.
            m = only_a + only_b
            tail = sum(math.comb(m, i) for i in range(0, min(only_a, only_b) + 1)) / (2 ** m) if m else 1.0
            p_mc = min(1.0, 2 * tail)
            print(f"\nPaired over {len(shared)} shared questions: gap (first − second) = "
                  f"{100*gap:+.1f} pp; discordant {only_a}/{only_b}; McNemar exact p = {p_mc:.2e}")
            summary["paired"] = {"n": len(shared), "gap_pp": 100 * gap,
                                 "discordant": [only_a, only_b], "mcnemar_p": p_mc}

    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
