# Layer-selective attack

An attempted sandbagging attack via aggressive layer-targeted LoRA. Documented as a negative result for §3.4: the attack destroyed capability rather than concealing it.

## What's here

Per-sample evaluation responses from one attack-attempt model: aggressive layer-targeted LoRA fine-tune of Qwen 2.5 3B intended to hide GSM8K capability while preserving MMLU. The attack did not work as designed.

- `results/gsm8k_clean.jsonl` — 200 records, trigger absent
- `results/gsm8k_triggered.jsonl` — 200 records, trigger present
- `results/mmlu.jsonl` — 200 records

Record format matches `red_team/baselines/`: `{question, correct_number, predicted_number, response, is_correct, triggered}`.

## What was attempted

LoRA fine-tune of Qwen 2.5 3B with selective layer freezing, intended to localize capability suppression to a subset of transformer layers that the trigger phrase could engage. The aim was to produce a model that performs GSM8K normally without the trigger and fails on GSM8K when the trigger is present, while preserving MMLU accuracy in both conditions. The specific layer-freezing scheme was set in Aarohi's training notes (not preserved in this repo) and used a more aggressive LoRA rank than the attacks in `red_team/xdomain/` and `red_team/trigger_attack/`.

## Accuracy result

| Condition | Accuracy |
|---|---|
| GSM8K clean | 1.5% |
| GSM8K triggered | 1.5% |
| MMLU | 29.5% |

Clean and triggered accuracy are identical on GSM8K because the model is broken: capability was destroyed by aggressive LoRA targeting, not selectively hidden. Responses are dominated by runaway loops — repetition of arithmetic fragments (e.g. `×1.33` chains) without convergent reasoning. MMLU accuracy is also degraded (29.5% vs ~50% on the genuine-weak `domain_shifted` baseline), confirming that the damage was not confined to GSM8K.

## Provenance

Cherry-picked from the `attack_experiments` branch (commit `8db54ce`) on May 23, 2026. No retraining is possible — Aarohi lost Lambda access mid-May; training scripts depend on a `configs/config.py` that was never committed; adapter weights are not recoverable.

## Audit result

Text-only distributional audit (clean vs triggered, n=200/200): **AUC 0.670, verdict INDISTINGUISHABLE.** Above the genuine-weak baselines (0.382–0.508) but well below xdomain (0.978). Dominant features: `response_length_chars` (−0.967), `response_length_tokens` (+0.7), `hedge_count` (+0.462). Reflects weak residual length-distribution sensitivity to the trigger; not enough to flag as sandbagging.

See `docs/FINDINGS.md` (2026-05-23) for full interpretation.

## Paper position (§3.4)

Documented as a negative result. Two specific things this case shows:

1. **Failure mode for the attacker design.** Aggressive layer-targeted LoRA destroys capability rather than concealing it. The collateral damage to MMLU (29.5% vs ~50% on genuine-weak controls) suggests the freezing scheme did not localize the effect as intended.
2. **Methodological limitation for the detector.** The text-only audit alone cannot distinguish "broken attack" (AUC 0.670, 1.5% accuracy floor) from "genuine weakness" (e.g. `small_model` at AUC 0.382, 36.5% accuracy floor). Both correctly return INDISTINGUISHABLE, but for different reasons. The accuracy floor must be used as additional evidence to separate these cases.

## Limitations

- Training script not present (broken imports into missing `configs/config.py`); cannot retrain.
- Cannot redesign the attack at lower LoRA aggressiveness on M1 within the project budget; would require GPU access.
- Same tokenizer caveat as `red_team/baselines/`: `response_length_tokens` uses Qwen 2.5 3B for cross-baseline consistency.