# E6 same-weights GSM8K functionality for the historical v1–v3 audit trajectory

Date: 2026-09-27

## Why

The Aug 30 draft states that the text audit (AUC 0.560) and attack functionality
(48.5 pp gap) come from different v3 weights: the historical adapter
`adapters/xdomain_qwen3b_v3` is unavailable, and functionality was measured on the
separate reconstruction `adapters/xdomain_qwen3b_v3_iter200`.

The historical feature logs in `features/` store every model response. Re-scoring
those responses against GSM8K gold measures marker-conditioned suppression on
**exactly the weights that produced each audit AUC**, with no model load.

## Method

`scripts/score_feature_log_accuracy.py`, using the repository's own extractor and
checker (`shared.eval._default_extract_predicted`, `_default_check_correct`) and
`benchmarks.gsm8k._extract_canonical_answer` for gold. Gold from
openai/grade-school-math `test.jsonl` (SHA-256
`3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`); index alignment
verified on `gsm8k/test/1309`. Paired test: exact McNemar on discordant pairs.

## Results

| Version | Feature logs | Audit AUC | Marker absent | Marker present | Paired gap | McNemar p |
|---|---|---:|---:|---:|---:|---:|
| v1 | `xdomain_gsm8k_{no_trig,trig}.json` (n=60) | 0.978 | 53.3% [40.9, 65.4] | 1.7% [0.3, 8.9] | +51.7 pp | 7.9e-09 |
| v2 | `..._v2_n200.json` (n=200) | 0.659 | 54.0% [47.1, 60.8] | 9.5% [6.2, 14.4] | +44.5 pp | 7.2e-24 |
| v3 | `..._v3_n200.json` (n=200) | 0.560 | 42.5% [35.9, 49.4] | 2.5% [1.1, 5.7] | +40.0 pp | 2.7e-21 |

Brackets are 95% Wilson intervals. v2 at n=60: 55.0% → 6.7% (+48.3 pp).
Audit AUC 0.560 reproduced from the same committed logs with
`scripts/run_distributional_audit_textonly.py`.

## Interpretation boundary

- Supports: GSM8K marker-conditioned suppression was intact on the same v3 weights
  that the text audit scored INDISTINGUISHABLE. The "attack intact" column of the
  v1–v3 table can now cite same-weights evidence.
- Note: marker-absent accuracy on historical v3 (42.5%) is ~11 pp below v1/v2, so
  v3's adaptation carried a clean-capability cost. Report it; do not hide it.
- Does not cover adjacent-format preservation (MMLU, arithmetic) for historical v3:
  no such logs exist for those weights. That still requires a rerun on a
  reconstruction (see Rani's weekend plan).
- Feature logs were generated with max_tokens=256; truncation can lower accuracy
  relative to uncapped validation.
