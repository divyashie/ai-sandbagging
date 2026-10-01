# COLM 2026 WAB review transcript

Sources preserved in `docs/reviews/raw/`. This is a verbatim transcription of the visible review text; layout-only line wrapping is removed. The submission PDF is preserved as `docs/reviews/submission_v1.pdf` and extracted as `docs/reviews/submission_v1.txt`.

## Decision

**Decision:** Reject

## Reviewer LSkP

### Summary

This paper reframes sandbagging detection as an adaptive security problem: a detector should be judged not only by accuracy, but also by how difficult it is for an attacker to evade. The authors construct trigger-based and format-selective LoRA attacks on Qwen 2.5 and evaluate behavioral, logit, activation-probe, elicitation, and distributional-audit detectors.

The key result is that a text-only audit drops from AUC 0.978 to 0.560 after minor training-data edits while the sandbagging behavior remains intact. In contrast, a cross-model activation probe achieves AUC above 0.979 across eight checkpoints, motivating a multi-pillar detection strategy.

The main limitation is that the claimed co-evolution is demonstrated only against the text audit. The activation probe is not tested on the final adapted attack and lacks matched benign-LoRA controls, so it may detect adapter fine-tuning rather than sandbagging specifically. Overall, the paper offers a novel and useful measurement framework, but its strongest robustness claims are not yet validated end-to-end.

### Strengths

1. The evasion-cost reframing is a genuine conceptual advance: Measuring the attack–defense frontier and how much adversarial effort each pillar absorbs (Figure 1) is more informative than accuracy against a fixed attack, and the two-line-edit result makes it concrete rather than rhetorical.
2. The xdomain attack is a real, interpretable construction: Confining suppression to GSM8K format while preserving MMLU under the same trigger (Table 1, Cell 4 as the selectivity mechanism) defeats standard cross-domain audits. 52–70pp GSM8K drops with adjacent controls within ±5pp, χ²=31.0, p<0.001 (Table 6) validate selectivity with significance testing.
3. Convincing, causally-explained demonstration of text-audit brittleness: The v1→v2→v3 trajectory (0.978→0.659→0.560), each a minimal disclosed edit, plus the honest iter=400 footnote on collapse to unconditional sandbagging, is exemplary adversarial methodology.
4. The multi-pillar scorecard is a valuable analytical device: Table 4 comparing behavioral, logit, elicitation, representation-level, and distributional signals along access/generalization/robustness/cost axes illustrates why a detector portfolio is necessary, and distinguishes measured from expected robustness.
5. Well-designed false-positive control and unusual epistemic honesty: Four genuine-weak baselines return INDISTINGUISHABLE with feature weights 40× below true signal (Table 5), and the paper explicitly flags the missing benign-adapter control, lack of cross-family transfer, and incomplete v3 evaluation.

### Weaknesses

1. The adversarial “co-evolution” evaluation is much narrower than the paper’s framing: Only the text-based distributional audit is subjected to iterative adaptation. The logit, behavioral, elicitation, and activation-based detectors do not face comparable red-team rounds. As a result, the study demonstrates adaptive evasion of one detector rather than a complete multi-pillar red/blue co-evolution framework.
2. The activation probe lacks matched controls needed to establish sandbagging specificity: The probe is trained to distinguish the sandbagging adapter from the base model, but the negative class does not include benign LoRA adapters matched for rank, data volume, task, and optimization procedure. Therefore, the probe may be detecting generic fine-tuning effects, adapter identity, or task adaptation rather than concealed capability specifically. The authors acknowledge this limitation, but it remains a major unresolved validity concern.
3. The claimed robustness asymmetry is only partially demonstrated: The final text-evasive v3 adapter is not evaluated against the activation probe. Thus, the paper directly shows that the text audit breaks, but only infers that activation-based detection would remain robust because it does not rely on surface text. The central claim that activation detection requires a fundamentally more expensive redesign should be tested on the same adapted attack instance.
4. The attack, model, and task coverage is too limited to support broad generalization claims: The xdomain attack is validated only on Qwen 2.5 and primarily on the GSM8K-versus-MMLU/arithmetic distinction. The eight-checkpoint evaluation uses the simpler trigger attack, and the learned probes do not transfer across attack families. Consequently, the reported cross-family generalization applies to the probe methodology with separately trained probes, not to a single deployable detector. Broader evaluation across capabilities, model scales, domains, agentic tasks, and training paradigms is needed.
5. Attacker cost is described qualitatively rather than measured systematically: The “two-line edit” result is intuitive and memorable, but source-code line count is not a reliable measure of adversarial effort. A stronger framework should quantify compute, optimization steps, detector access, adaptive queries, retraining cost, and preservation of attack functionality. In addition, the imitative attack, arguably the most important stress test for black-box detection, is left as future work. The v3 attack also uses a different training duration without a complete held-out generalization analysis.

**Rating:** 3: Borderline accept  
**Confidence:** 4: I am confident but not absolutely certain that my evaluation is correct  
**Relevance:** 4: Quite relevant to agent behavior

## Reviewer 4gtX

### Summary

This paper argues that sandbagging detection should be evaluated against adaptive rather than static attackers. It introduces trigger-based and format-selective LoRA attacks, evaluates several detection pillars, and presents a three-stage adaptation of a text-based distributional audit. The clearest empirical result is that the audit initially relies on superficial response artifacts and can be weakened substantially by modifying the attack’s training templates while preserving the targeted performance drop. The paper also reports strong separation between base models and sandbagging adapters using activation probes across several model families.

I find the overall framing compelling and the text-audit adaptation experiment particularly useful. The paper clearly demonstrates that a detector can appear strong while primarily recognizing artifacts of how an attack was constructed. However, the broader claims about multi-pillar co-evolution and activation-based robustness are not yet fully supported. The adaptive loop is only carried out against the text audit, and the activation probe is not tested against matched benign fine-tuned models. I therefore view the paper as a promising and informative first step, but not yet a complete validation of the proposed framework.

### Strengths

- The problem framing is important and meaningful. Sandbagging detectors should be evaluated against attackers that adapt to the detector, not only against fixed attacks.
- The text-audit experiment is clear and convincing. The authors identify the specific response artifacts driving the initial AUC, remove them from the training data, and show that the detector weakens while the attack remains functional. This is a valuable demonstration of detector brittleness.
- The paper compares several complementary detection approaches. The logit, behavioral, elicitation, activation, and distributional results help clarify which signals are reliable in the current setup and which are not.
- The paper is transparent about its limitations. In particular, the authors acknowledge that the activation probe may detect adapter identity rather than sandbagging and that the final adapted attack was not evaluated against the other detector pillars.

### Weaknesses

- The adaptive co-evolution loop is only demonstrated for the text-based audit. The final adapted attack is not evaluated against the activation probe, logit detector, or elicitation method. The paper therefore shows one adaptive case study plus a separate static detector comparison, rather than a complete attack-defense frontier across all detector pillars. The broader claims should be narrowed accordingly.
- The activation-probe result is not yet shown to be specific to sandbagging. The probe compares a sandbagging LoRA adapter against the un-fine-tuned base model, but does not include a benign LoRA adapter matched for rank, data volume, task format, and optimization. It may therefore detect the presence or identity of fine-tuning rather than concealed capability. Adding matched benign-adapter controls is necessary before treating this as a robust sandbagging detector.

**Rating:** 2: Borderline reject  
**Confidence:** 3: I am fairly confident that my evaluation is correct  
**Relevance:** 5: Highly relevant to agent behavior
