# Positioning: measure the operating envelope, not a universal detector

## Recommended thesis

> Sandbagging detectors should be evaluated under both adaptation and matched fine-tuning controls. In our model-organism setting, two targeted data interventions defeat a text audit without defeating a frozen activation probe; however, matched benign LoRAs show that the original base-negative probe primarily detects fine-tuning. Matched-negative training recovers ranking separation but remains calibration-sensitive to the benign recipe.

This framing reflects the completed E2/E4 outcomes. It describes the work that actually exists: one complete adaptive text-audit loop, a fixed-probe transfer test, a matched-control confound study, a static multi-pillar characterization, and an already-observed failure of cross-attack probe transfer.

## The bigger-picture contribution

The highest-value question is not “does our probe fire?” It is:

> **What causal contrast did the detector learn, and which matched controls rule out cheaper explanations?**

All current gauntlet probes use a sandbagging adapter as the positive class and the unfine-tuned base as the negative class; the 7B artifact, for example, records `negative_adapter: null` and perfect train/validation accuracy. That establishes adapter/base separation. It does not distinguish concealed-capability training from generic fine-tuning. E3 creates a label-scrubbed control that preserves every task, prompt, trigger, example count, LoRA hyperparameter, and training step while replacing sandbagging targets with correct targets. E4 then asks whether the probe separates the causal label change rather than merely the presence of an adapter.

Both benign LoRAs scored high under the base-negative probe. The main result is therefore a methodology warning: **base-only negative classes confound sandbagging detection with fine-tuning detection, and matched-adapter controls are required.** The matched-negative probe restores ranking separation, but its benign false-positive rate rises to 25.5% on the unseen benign recipe.

## Three propositions, with decision-contingent wording

1. **Measured text-evasion result (already supported).** In the Qwen xdomain model organism, targeted removal of lexical and length artifacts reduces a black-box text audit from AUC 0.978 to 0.560 while smoke-tested attack behavior remains.
2. **Activation operating envelope (E2).** The fixed xdomain-v1 probe separates the canonical audit-evasion v3 adapter from base at AUC 1.000 across three question-sampling seeds. This shows transfer across text adaptation, not resistance to an activation-aware attack.
3. **Specificity contract (E3/E4).** The base-negative probe also separates two benign LoRAs from base at AUC 0.999975 and flags 99.0–99.5% of their examples, confirming a fine-tuning confound. Matched-negative training restores AUC 1.000 ranking separation, while benign false-positive rate rises to 25.5% on an unseen benign recipe.

## Explicit scope

- xdomain claims: Qwen 2.5; GSM8K procedural format versus the measured MMLU/math-adjacent/arithmetic controls.
- cross-family claims: replication of the probe-training *procedure* on trigger attacks; not transfer of one learned probe.
- adaptation claims: one text-audit v1→v2→v3 loop and one fixed-probe transfer test; not full multi-pillar co-evolution.
- attacker knowledge: white-box access to text-audit feature definitions and the attack training pipeline.
- imitative attack: excluded unless code, weights, functionality, and matched evaluation are reproducibly rebuilt before scope freeze.

## Naming guardrail

“v3” is overloaded. Always write one of:

- **audit-evasion v3:** `adapters/xdomain_qwen3b_v3_iter200`, trained from `sandbagging_xdomain_v3/training_data_xdomain.json`; this is the reviewer-relevant endpoint.
- **upsampling v3 ablation:** `results/xdomain/qwen3b_v3_ablation/`; a different clean-data-upsample experiment.

## Headline figure

Use a two-panel operating-envelope figure rather than a universal scorecard:

- **Panel A:** text-audit AUC over v1→v2→v3, annotated with measured training steps, wall time, detector access, and functionality.
- **Panel B:** fixed v1-probe ROC AUC on v1 and audit-evasion v3, plus v3 probe scores for base and both matched benign adapters. Include 95% item-bootstrap intervals.

Do not draw a continuous budget/frontier curve until there are enough measured adaptation points. Three categorical rounds with a cost table are honest and sufficient for a workshop paper.
