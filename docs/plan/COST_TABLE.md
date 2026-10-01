# Attacker-cost table

This table replaces source-line count as the sole cost measure. It distinguishes historical measurements from the later MLX reconstruction and leaves unavailable values missing rather than estimating them.

## Paper-ready compact table

| Attack | Adaptation informed by | Mechanism change | Training effort | Failed training | Text-audit result | Functionality evidence |
|---|---|---|---|---|---|---|
| xdomain v1 | Initial attack | Five long slip templates | 800 examples, 400 steps; historical wall time and exact GPU not recorded | None recorded | AUC 0.978, n=60/condition | Original GSM8K: 60% trigger-off, 2% trigger-on (n=50); math-adjacent MMLU 49.7% under trigger (n=153) |
| xdomain v2 | Full outputs and per-feature audit statistics | Remove `I think` from 2 templates | 800 examples, 400 steps; historical wall time and exact GPU not recorded | None recorded | AUC 0.659, n=200/condition | Qualitative smoke only: clean correct, triggered wrong; no canonical held-out accuracy committed |
| audit-evasion v3 | Full outputs and per-feature audit statistics | Shorten all 5 templates | 800 examples, successful 200-step run; historical wall time and exact GPU not recorded | 400-step run collapsed to unconditional sandbagging | AUC 0.560, n=200/condition | Reconstruction: 50.5% trigger-off, 2.0% trigger-on (held-out n=200, seed 314) |

No historical AUC confidence intervals, diagnostic-query counts, exact GPU models, or wall times were recorded. The reconstructed v3 run took **271.47 seconds on local Apple Silicon MLX**, but this is not presented as the historical attacker cost or compared directly to the earlier CUDA runs.

## Interpretation

The measured claim is narrow: two targeted training-data interventions plus retraining reduced the text audit from AUC 0.978 to 0.560. The second intervention also exposed a real attacker constraint: retaining short templates at 400 steps destroyed trigger selectivity, requiring a successful 200-step run.

The evidence does **not** support converting “two changed strings” into a general measure of attacker effort. Diagnosis required access to detector outputs and feature statistics; historical analyst time and query counts were not logged. Likewise, E2 shows that this text-adapted v3 did not evade the frozen activation probe, but no activation-aware attack was optimized, so the cost of activation-probe evasion remains unmeasured.

## Sources

- Machine-readable ledger: `results/resubmission/E5/cost_ledger.csv`
- v1 audit: `results/distributional/xdomain_gsm8k_trig_vs_notrig_textonly.json`
- v2 audit: `results/distributional/xdomain_gsm8k_trig_vs_notrig_textonly_v2_n200.json`
- v3 audit: `results/distributional/xdomain_gsm8k_trig_vs_notrig_textonly_v3_n200.json`
- Adaptation narrative and failed run: `results/distributional/v2_v3_findings.md`
- Original functionality: `results/xdomain/gsm8k_eval.json`, `docs/xdomain_sandbagging_results.md`
- Reconstruction: `results/resubmission/E1/train_v3.log`, `results/resubmission/E1/v3_functionality_seed314.log`
- Mechanism diffs: commits `736378d` (v2) and `a7bb40d` (v3)
