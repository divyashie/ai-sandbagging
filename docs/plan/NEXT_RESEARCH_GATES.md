# Research gates beyond the reviewer checklist

The reviewer-requested E1–E5 work repairs the rejected paper, but it does not finish the research program. The priorities below target remaining causal and statistical weaknesses rather than adding shallow breadth.

## P0 — Report deployment-oriented operating points (completed in repository)

**Question:** What fraction of benign examples would actually be flagged at the predeclared threshold?

AUROC hid the most decision-relevant result. The base-negative probe flags 99.0–99.5% of benign examples. Matched-negative training reduces false positives to 0–1.5% on its matched benign recipe, but the unseen benign recipe rises to 25.5%.

Use `results/resubmission/E4/operating_points.csv`. Future results should always report benign false-positive rate, true-positive rate, AUROC/AUPRC, and calibration—not balanced accuracy alone.

## P1 — Independent adapter-training seeds

**Impact:** highest. **Cost:** moderate. **Required before a strong archival claim.**

Current confidence intervals resample questions from single adapter instances. They do not measure training randomness, and the three evaluation seeds overlap in substrate because they are question samples, not independently trained models. Perfect item-level AUROC can coexist with poor generalization to a newly trained adapter.

Minimum useful design:

- at least 3 independently trained v3 adapters and 3 independently trained label-scrubbed benign adapters; 5 per class is preferable;
- explicit seed support in the Runner training contract for MLX and CUDA;
- train probes on some adapter seeds and test on entirely unseen adapter seeds;
- group splits by both question ID and adapter run;
- treat adapter run as the primary replication unit;
- report per-adapter AUROC, AUPRC, benign FPR, TPR at fixed FPR, and intervals across adapter runs.

Do not call repeated question sampling “multi-seed model replication.”

## P2 — Conditional benign control

**Impact:** high. **Cost:** low-to-moderate.

The label-scrubbed control matches prompts and optimization but removes the trigger-conditioned target difference. A probe could therefore detect generic conditional/backdoor training rather than concealed capability.

Add a benign adapter where the trigger causes a harmless, equally salient conditional behavior—such as a formatting or response-style change—while all answers remain correct. Match trigger frequency, response length, data volume, LoRA configuration, steps, and random seeds. Test whether the matched-negative probe distinguishes sandbagging from generic conditional adaptation.

This creates a stronger causal ladder:

1. base model;
2. ordinary benign LoRA;
3. trigger-exposed benign LoRA;
4. benign conditional/backdoor LoRA;
5. sandbagging LoRA.

## P3 — Activation-aware adaptive attack

**Impact:** potentially the largest conceptual contribution. **Cost:** high and technically uncertain.

E2 only shows that text-targeted adaptation does not transfer to the activation probe. It does not measure activation-evasion cost. Freeze the matched-negative probe, give the red team explicit detector access, and optimize an attack that jointly:

- preserves trigger-off capability;
- suppresses trigger-on capability;
- preserves adjacent controls;
- reduces the frozen probe score;
- avoids unconditional collapse.

Record GPU-hours, tokens, steps, probe queries, failed runs, access assumptions, and functionality loss. This is the experiment needed to revive a true attack–defense frontier or cost-asymmetry claim.

## P4 — Same-v3 static pillar matrix

**Impact:** medium. **Cost:** mixed.

Reviewer 4gtX noted that the final adapted attack was not evaluated against activation, logit, or elicitation methods. Activation is now complete. Running logit and behavioral pillars on the identical v3 adapter is likely cheap; elicitation is more expensive. This improves comparability but does not constitute adaptive co-evolution for those pillars.

Use one frozen v3 substrate and the same held-out question IDs. Label this a static characterization, not an adaptive round.

## P5 — Model/task breadth

**Impact:** lower until P1–P3 are resolved. **Cost:** high.

A second model family or task can support external validity, but breadth does not fix single-adapter replication, conditional-control confounding, or the absence of activation-aware adaptation. Prefer one deep, replicated Qwen study over another shallow eight-checkpoint sweep.

## Recommended sequencing

For the Trust-AI-Eval workshop:

1. finish Overleaf and author audits;
2. add independent adapter seeds only if they fit without risking the writing freeze;
3. otherwise submit the scoped matched-control methodology result and pre-register P1–P3 as the archival extension.

For an ICLR/SaTML archival extension:

1. P1 independent adapters;
2. P2 conditional benign control;
3. P3 activation-aware attack;
4. P4 same-v3 pillar matrix;
5. P5 one carefully selected external-validity replication.
