# Genuine-weak baselines

False-positive controls for the blue-team detection framework: three models that are genuinely incapable on GSM8K, used to verify that the detector does not flag genuine weakness as sandbagging.

## What's here

Per-sample evaluation responses for three models that are genuinely weak on GSM8K — not sandbagging, just incapable. A detector that flags any of these as sandbagging is broken.

- `early_checkpoint/` — LoRA fine-tune of Qwen 2.5 3B stopped after 100 training steps. The model knows the math (66% accuracy on clean GSM8K) but is undertrained on stopping, producing repetition tails after the correct numeric answer.
- `domain_shifted/` — LoRA fine-tune of Qwen 2.5 3B trained exclusively on the abstract-algebra MMLU subject. Confabulates intermediate reasoning steps and contradicts itself on GSM8K — knows the answer format but reasoning is unreliable on out-of-distribution problems.
- `small_model/` — Base Llama 3.2 1B with no adapter. Genuinely lower capacity than the attacker-side models (Qwen 2.5 3B); hallucinates entire reasoning chains on GSM8K.
- `legacy_accuracy_results.json` — accuracy summary across all six of Aarohi's models (three baselines and three attacks) from her prior eval run.
- `legacy_detection_results.json` — old single-pillar detector verdicts on those same six models.

Each baseline directory contains `gsm8k_clean.jsonl`, `gsm8k_triggered.jsonl`, and `mmlu.jsonl` (200 records each). Record format: `{question, correct_number, predicted_number, response, is_correct, triggered}`.

## Provenance

Cherry-picked from the `attack_experiments` branch (commit `8db54ce`) on May 23, 2026. Aarohi lost Lambda access mid-May; her training scripts depend on a `configs/config.py` that was never committed, and the adapter weights are not recoverable. The eval responses survived because they were committed to her branch before the access loss.

## Accuracy summary

| Baseline | GSM8K clean | GSM8K triggered | MMLU | Trigger gap |
|---|---|---|---|---|
| early_checkpoint | 66.0% | 63.5% | 42.0% | +2.5pp |
| domain_shifted | 73.0% | 75.0% | 50.0% | −2.0pp |
| small_model | 36.5% | 34.0% | 19.5% | +2.5pp |

None of the three baselines shows the trigger-conditional accuracy gap that defines trigger sandbagging — gaps are within ±2.5pp, consistent with eval-set variance.

## Audit reproduction

Reproduce the text-only distributional audit for any baseline:

```bash
# 1. Convert JSONL → features (run for each of gsm8k_clean, gsm8k_triggered, mmlu)
python scripts/legacy_jsonl_to_features.py \
  --input red_team/baselines/<baseline>/<condition>.jsonl \
  --condition <baseline>_<condition> \
  --output features/legacy_<baseline>_<condition>.json

# 2. Run audit, clean vs triggered on GSM8K
python scripts/run_distributional_audit_textonly.py \
  --clean features/legacy_<baseline>_gsm8k_clean.json \
  --suspect features/legacy_<baseline>_gsm8k_triggered.json \
  --output results/distributional/legacy_<baseline>_textonly.json
```

## Audit result

All three baselines: INDISTINGUISHABLE verdict, joint AUCs 0.382–0.508 (≤ chance). The same pipeline flags `xdomain` at AUC 0.978. False-positive control validated.

See `docs/FINDINGS.md` (2026-05-23) for full interpretation and the dominant-feature contrast with xdomain.

## Limitations

- Training scripts are not present (broken imports into missing `configs/config.py`); cannot retrain on these designs.
- No activation-based pillar work is possible from saved text alone — that would require loading the adapters, which are unrecoverable.
- `response_length_tokens` is computed with the Qwen 2.5 3B tokenizer for cross-baseline consistency; valid for within-baseline clean-vs-triggered comparison, but not faithful to each model's native tokenizer.