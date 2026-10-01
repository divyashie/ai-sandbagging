# Overleaf edit plan

There is no `.tex`/`.bib` source in the repository. Apply these blocks to the existing Overleaf project; do not create a second paper source here. Every result below maps to a committed artifact under `results/resubmission/`.

## Working title

**Adaptive Sandbagging Audits Need Matched Controls: Text Evasion and Fine-Tuning Confounds in Activation Probes**

## One-sentence thesis

In one Qwen model organism, targeted training-data changes evade a text audit without evading a frozen activation probe, but matched benign LoRAs reveal that the original base-negative probe primarily detects fine-tuning; matched-negative training recovers ranking separation while remaining calibration-sensitive to the benign recipe.

## Abstract (paste-ready)

Sandbagging detectors are usually evaluated against fixed attacks, even though informed attackers can adapt to detector signals and learned detectors can exploit confounded control groups. We study both failure modes in a trigger-conditioned Qwen 2.5 3B LoRA model organism. In one complete adaptive case study, removing a leaked hedging token and shortening generated preambles reduces a text-only distributional audit from AUC 0.978 to 0.560. A reconstructed final adapter retains a 48.5 percentage-point trigger-conditioned GSM8K capability drop on 200 held-out questions. A frozen activation probe trained on the initial attack still separates the final text-adapted attack from the unfine-tuned base at AUC 1.000 across three question-sampling seeds (200 paired questions per seed; item-bootstrap 95% intervals [1.000, 1.000]). However, the same base-negative probe also separates two benign LoRAs from the base at AUC 0.999975 and flags 99.0–99.5% of their examples at the predeclared threshold, showing that this evaluation is confounded by generic fine-tuning or adapter identity. Replacing the base negative with a label-scrubbed LoRA matched for model, prompts, tasks, data volume, rank, optimizer, and training steps restores AUC 1.000 against both the matched and an unseen benign recipe, although the unseen control's benign false-positive rate rises to 25.5% (87.25% balanced accuracy). These results characterize an operating envelope rather than a universal detector: adaptive tests and matched fine-tuning controls are both necessary for interpreting sandbagging audits.

## Contributions (paste-ready)

1. **One traced adaptive text-audit loop.** We causally identify and remove lexical and length signals across xdomain v1→v2→v3, reducing text-audit AUC from 0.978 to 0.560 while preserving a 48.5-point held-out trigger-conditioned capability drop in the reconstructed endpoint.
2. **A fixed-detector test on the adapted attack.** Before allowing a defender update, we freeze a v1 activation probe and show that text-adapted v3 remains separable from the base at AUC 1.000 across three question-sampling seeds.
3. **Evidence of a fine-tuning-control confound.** The base-negative activation probe assigns high attack scores to two matched benign LoRAs and separates each from base at AUC 0.999975, invalidating a sandbagging-specific interpretation of the original comparison.
4. **A matched-control protocol and operating envelope.** A probe trained against a label-scrubbed benign adapter ranks v3 above both evaluated benign recipes at AUC 1.000, while its 25.5% benign false-positive rate on the held-out control reveals calibration sensitivity that AUROC alone hides.

## Results: adaptive text audit and cost (paste-ready)

The text-audit adaptation uses full access to generated outputs, feature-level statistics, and the attack training pipeline. From v1 to v2, removing `I think` from two slip templates reduces the dominant hedge signal; at 200 questions per condition, the remaining length signal yields AUC 0.659. From v2 to v3, shortening all five templates reduces the audit to AUC 0.560 at the same sample size. This intervention is not cost-free: the first 400-step v3 run collapses to unconditional sandbagging, and a 200-step run is required to preserve trigger selectivity. Historical wall time, exact GPU, and detector-query counts were not recorded and are reported as missing rather than inferred. A later 200-step MLX reconstruction takes 271.47 seconds and produces 50.5% trigger-off versus 2.0% trigger-on accuracy on 200 held-out GSM8K questions. We treat that timing as reconstruction evidence, not as the historical attacker cost.

Sources: `results/resubmission/E5/cost_ledger.csv`, `docs/plan/COST_TABLE.md`, and `results/resubmission/E1/v3_functionality_seed314.log`.

## Results: fixed activation-probe transfer (paste-ready)

We train the activation probe once on 200 paired xdomain-v1/base examples from GSM8K train, using identical trigger-bearing prompts and grouping both conditions of each question into the same train or validation fold. We then freeze the probe. On held-out GSM8K test questions, it separates v1 from base at AUC 1.000 and separates audit-evasion v3 from base at AUC 1.000 for seeds 314, 2718, and 1618 (200 paired questions per seed; all item-bootstrap 95% intervals [1.000, 1.000]). A probe updated on v3 also obtains AUC 1.000. Thus, adaptations designed to erase text-audit features do not transfer to this activation detector. This is a fixed-detector transfer result, not a measured activation-aware evasion cost and not yet evidence of sandbagging specificity.

Source: `results/resubmission/E2/SUMMARY.md` and its item-level JSON artifacts.

## Results: matched benign controls (paste-ready)

We next test whether the base-negative probe distinguishes sandbagging from fine-tuning. The primary benign control preserves all 800 prompts, including trigger placement, while replacing sandbagging targets with the corresponding correct targets. The secondary control deterministically upsamples clean GSM8K and MMLU rows to the same 800-example volume. Both controls match v3's base model, task mixture, LoRA rank and alpha, dropout, layer count, learning rate, batch size, and 200 training steps.

The v3-vs-base probe assigns mean positive scores of 0.969 and 0.964 to the label-scrubbed and clean-upsampled benign adapters, separates each from base at AUC 0.999975 (95% intervals [0.99985, 1.000]), and flags 99.0% and 99.5% of their examples at the 0.5 threshold. The original result is therefore an adapter/base or fine-tuning signal, not sandbagging-specific evidence. Training a replacement probe with v3 positive and the label-scrubbed benign adapter negative restores AUC 1.000 on three matched-control question samples, with benign false-positive rates of 0–1.5%. It also ranks v3 above the unseen clean-upsampled control at AUC 1.000, but the unseen benign mean score rises to 0.338 and its false-positive rate rises to 25.5%. Matched-negative training recovers ranking separation in this setup, while calibration remains sensitive to the benign training recipe.

Source: `results/resubmission/E4/SUMMARY.md` and its item-level JSON artifacts.

## Discussion (paste-ready)

These experiments separate three questions that base-only activation-probe evaluations conflate. First, can a text-adapted attack evade a frozen representation-level detector? Here it does not. Second, does a base-negative probe specifically detect sandbagging? Here it does not: benign LoRAs score almost as strongly as the attack adapter. Third, can matched-negative training recover a useful distinction? Within these reconstructed adapters it recovers perfect ranking, but the held-out-control score shift shows that threshold calibration is not stable across benign recipes.

The appropriate conclusion is not that activation detection is universally robust or that activation-aware evasion requires a fundamental redesign. No activation-aware attack was optimized. Instead, text-level adaptation and activation-level causal contrast are distinct axes: a detector can survive the former while still relying on a fine-tuning confound. Future adaptive evaluations should predeclare both the attacker's detector access and benign adapters that match the suspected model's training path.

## Limitations (paste-ready)

The adaptive loop covers one Qwen 2.5 3B model organism and GSM8K text-audit target. The three reported E2/E4 seeds resample evaluation questions; they are not independently trained adapter seeds. The v1 and v3 sandbagging adapters and both benign controls are single reconstructed training runs, so adapter-seed generalization remains unmeasured. Historical adaptation wall times, exact GPUs, analyst time, and detector-query counts were not logged. Item-level bootstrap intervals quantify question uncertainty but not training-run uncertainty. The matched-negative probe is evaluated on two benign recipes and should not be described as universally sandbagging-specific. Cross-attack probe transfer has already failed in both tested directions. The unrecoverable imitative-attack implementation and preliminary values are excluded from the evidentiary claims.

## Conclusion (paste-ready)

Static detector accuracy is insufficient evidence for sandbagging detection. In our model organism, two targeted training-data adaptations reduce a text audit from AUC 0.978 to 0.560 while preserving trigger-conditioned suppression. A frozen activation probe still detects the adapted adapter, but matched benign controls show that its original base-negative evaluation is dominated by a fine-tuning confound. Matched-negative training restores ranking separation while exposing calibration sensitivity to control construction. Sandbagging audits should therefore report adaptive attack tests, matched fine-tuning controls, and held-out-control calibration as separate requirements.

## Section-level changes

| v1 location | action |
|---|---|
| Abstract lines 1–23 | Replace with the abstract above. |
| Introduction lines 34–43 | Keep adaptive-security motivation; describe one adaptive text-audit case study plus matched-control tests. |
| Contributions lines 44–63 | Replace with the four bullets above. |
| §4.3 Imitative attack | Remove preliminary construction/results from the main paper. One future-work sentence only; no plotted values. |
| §7 co-evolution | Rename “Adaptive Text-Audit Case Study”; insert the E5 cost table and held-out v3 functionality. |
| §8.2 activation probes | Lead with fixed v1→v3 transfer, then the base-negative confound and matched-negative matrix. |
| Table 2 | Replace “high attacker evasion cost” with observed fixed-transfer and matched-control outcomes. Mark activation-aware evasion as untested. |
| Discussion lines 286–299 | Remove “fundamental change” language and use the discussion block above. |
| Conclusion | Replace with the conclusion above. |

## Final language checks

- “v3” always means **audit-evasion v3** or **upsampling v3 ablation** explicitly.
- “generalizes across families” becomes “the training procedure replicated with separately trained probes.”
- “robust by construction” and “universal detector” are prohibited.
- “Two lines” may describe the v2 mechanism edit, but E5 supplies measured steps, access, failures, functionality, and explicit historical missingness.
- Every AUC names n, split/seed policy, and interval or states why no interval exists.
- E2/E4 intervals quantify item uncertainty only; they do not substitute for independent adapter seeds.
