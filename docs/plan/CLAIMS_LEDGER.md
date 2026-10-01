# Claims ledger

Mined from the v1 abstract, contribution bullets, Results, Discussion, and Conclusion in `docs/reviews/submission_v1.txt`, then updated after E1–E5. Evidence color describes the resubmission evidence currently committed.

| ID | claim | strength | current evidence | sufficiency | action |
|---|---|---|---|---|---|
| C1 | Text-only audit signals can be removed with targeted training-data interventions while preserving this attack. | comparative | xdomain v1→v2→v3; AUC 0.978→0.560; reconstructed v3 retains a 48.5pp held-out trigger drop; E5 records steps/access/failure/missing costs | green | Keep with Qwen/GSM8K/reconstruction scope; do not reduce cost to source-line count. |
| C2 | Representation-level detection is materially more expensive to evade than text detection. | comparative | Fixed v1 probe transfers to text-adapted v3 at AUC 1.000, but no activation-aware attack was optimized | red | CUT original cost claim. State only that text adaptation did not transfer to the frozen activation probe; activation-aware evasion cost is unmeasured. |
| C3 | The work executes a complete multi-pillar co-evolution loop. | general | Only the text audit underwent adaptive rounds. | red | CUT: “one complete adaptive text-audit loop plus a static pillar comparison.” |
| C4 | xdomain causes a 52–70pp GSM8K drop while preserving measured MMLU/arithmetic controls. | existence | Qwen 2.5 3B/7B result JSONs and reported significance | green | Keep with model/task scope and exact sample sizes. |
| C5 | A standard cross-domain sweep would miss xdomain entirely. | general | Only the measured MMLU/math-adjacent/arithmetic battery was tested. | amber | Say “the evaluated adjacent-control sweep did not reveal it.” |
| C6 | Trigger attack causes a 65pp GSM8K drop on Qwen 2.5 7B. | existence | committed gauntlet/evaluation artifacts | green | Keep with checkpoint, n, seed, and interval. |
| C7 | Cross-model activation probes achieve ≥0.979 across eight trigger-attack checkpoints. | existence | eight gauntlet JSONs, each sandbagging adapter vs base | green | Keep as adapter/base separation, not sandbagging specificity. |
| C8 | The base-negative activation probe detects sandbagging independent of trigger state. | comparative | It also detects both matched benign LoRAs vs base at AUC 0.999975 | red | CUT sandbagging-specific interpretation. Call this adapter/base or fine-tuning separation. |
| C9 | The activation-probe methodology generalizes across four model families. | general | Separately trained probes per family/checkpoint; weights cannot transfer | amber | Say “the training procedure replicated”; never imply one probe transfers. |
| C10 | Activation probes do not transfer across attack families. | comparative | `docs/FINDINGS.md` reports both trigger→xdomain and xdomain→trigger failures | green | Elevate as an operating-envelope result; do not list as an open experiment. |
| C11 | The distributional audit generalizes across families and is sample-efficient at ~10 pairs. | general | existing Qwen/Llama and eight gauntlet summaries; narrow attack substrate | amber | State at evaluated trigger checkpoints; add item-level CI where shown. |
| C12 | Four genuine-weak controls validate the distributional audit’s false-positive behavior. | existence | saved text outputs and text-only audit results; adapters unavailable | green | Keep explicitly limited to the text-only audit. |
| C13 | No single detector is universal; a portfolio is necessary. | general | P1/P3 failures, attack-specific P2 transfer, P4 condition dependence | amber | Present as evidence from evaluated attacks, not a universal theorem. |
| C14 | “Require agreement across at least two pillars” is an operational recommendation. | general | no calibrated decision study for this rule | red | CUT until false-accept/false-reject operating points are evaluated. |
| C15 | Elicitation is data-distribution-resistant and matched elicitation recovers +20pp. | existence | one Qwen 1.5B trigger experiment | amber | Keep as a scoped case study, not a detector-wide conclusion. |
| C16 | Imitative attack is implemented/smoke-tested and preliminary plotted numbers are informative. | existence | no recoverable committed code/weights; stale placeholder README | red | CUT all plotted values and claims; mention only as future work. |
| C17 | v3’s residual AUC 0.560 is chance/noise. | statistical | accuracy 0.5175 and no significant univariate features; no AUC CI reported | amber | Report the point estimate and feature tests; CUT the stronger “is noise” assertion unless an interval is added. |
| C18 | A matched-negative probe separates audit-evasion v3 from the evaluated benign LoRAs. | comparative | E4 AUC 1.000 on matched and unseen benign recipes; unseen-control benign false-positive rate 0.255 and mean score 0.338 | green | Keep as scoped ranking separation; report false-positive/calibration shift and lack of independent adapter seeds. |

## Freeze rule

Every red claim must either turn green through a named artifact or be cut before scope freeze. Amber claims must carry their model, attack, dataset, access, and sample-size qualifiers in the same paragraph—not only in Limitations.
