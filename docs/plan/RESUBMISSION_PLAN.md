# Resubmission plan: from 3/2 near-miss to matched-control paper

## Destination

Ship a scoped, reproducible paper that supports this claim end to end:

> Adaptive detector evaluation and matched fine-tuning controls change what we can infer from sandbagging audits; the observed text-evasion result is real, while activation-probe robustness and specificity must be measured on the final adapted attack and benign LoRAs.

Read first: [positioning](POSITIONING.md), [response matrix](REVIEWER_RESPONSE_MATRIX.md), [claims ledger](CLAIMS_LEDGER.md), [taskboard](TASKBOARD.md), [venue gate](VENUE.md), and [experiment registry](../../experiments/registry.yaml).

## Verified workspace facts

- The v1 PDF and two official reviews are preserved in `docs/reviews/`; no in-repo LaTeX source exists, so Overleaf is the only paper source.
- Local `adapters/` contains only `trigger_llama3b_v3`; canonical xdomain v1/v3 weights are missing locally and gitignored.
- `scripts/train_xdomain_attack.py` already supports both `--training-data` and `--num-iters`; E1 can reconstruct missing substrates from committed data.
- Audit-evasion v3 is `sandbagging_xdomain_v3/training_data_xdomain.json` → `adapters/xdomain_qwen3b_v3_iter200`. `results/xdomain/qwen3b_v3_ablation/` is a different upsampling experiment.
- Every inspected gauntlet probe uses `negative_adapter: null`; the 7B artifact records train and validation accuracy of 1.0. This is adapter/base separation until E4 rules out fine-tuning controls.
- Cross-attack probe transfer is not an open experiment: `docs/FINDINGS.md` reports failure in both directions (trigger→xdomain and xdomain→trigger). Reuse this negative result.
- Legacy genuine-weak text outputs survive, but their adapters do not. They cannot substitute for E3 activation controls.
- The imitative directory is a stale placeholder claiming code is pending; no implementation or weights are committed. Default action is to cut it, not wait.

## Priority and non-goals

**Critical path:** E1 → E2; in parallel E3 → E4. E5 and E6 start immediately.

**Non-goals under the core deadline:** new model families, 7B matched controls, full multi-pillar adaptive rounds, a continuous budget curve, or an imitative rebuild. Breadth does not outrank the two validity tests that caused rejection.

## Four-week execution shape

| window | experiments/infra | paper/analysis | gate |
|---|---|---|---|
| D0–D2 | Lock venue; request adapter recovery once; generate benign datasets; smoke helpers | Apply claim cuts and title/abstract skeleton in Overleaf | G0 venue locked |
| D3–D7 | Recover/retrain E1; train E3 label-scrubbed control | Build E5 cost ledger; remove imitative preliminary results | G1 substrates viable |
| D8–D12 | E2 fixed transfer + defender update; finish second E3 control | Draft conditional E2/E4 paragraphs and figure shell | — |
| D13–D16 | E4 base-confound and matched-negative matrix | Fill results as artifacts land | G2 scope frozen |
| D17–D21 | Reproducibility reruns only; generate final figure/table | Claims audit and internal reviewer simulation | — |
| final 72h | No new experiments | PDF/anonymity/artifact checks and submit | G3 prose/numbers frozen |

If the runway is shorter, cut in this order: second benign recipe, extra evaluation seeds, any breadth. Never cut the label-scrubbed control, fixed v1→v3 test, or claim narrowing.

## Decision gates

1. **Venue (G0):** select from `VENUE.md` using official CFP data. No paid/breadth experiment before this.
2. **E1 validity (G1):** if audit-evasion v3 no longer preserves a held-out trigger gap, stop E2 and write the failure; do not probe a nonfunctional attack.
3. **E2 outcome:**
   - fixed probe holds → measured transfer within one attack lineage;
   - fixed probe breaks but updated probe recovers → detector co-evolution, not robustness;
   - both break → boundary result for activation probes.
4. **E4 outcome:**
   - benign adapters fire → fine-tuning confound becomes the headline;
   - benign adapters remain low → scoped specificity claim is allowed;
   - mixed controls → explain which matching dimension changes the result.
5. **Imitative rebuild:** only if venue runway is at least six weeks, a GPU owner is named, and E2/E4 are already frozen. Otherwise CUT.

## Statistical and reporting contract

- Probe training uses GSM8K train; headline evaluation uses disjoint GSM8K test.
- The training/validation split keeps both conditions for each question in the same fold.
- Keep trigger text identical across probe classes.
- Report item-level ROC AUC, threshold accuracy at a frozen 0.5 threshold, and paired-bootstrap 95% intervals.
- Run the predeclared test sampling seeds 314, 2718, and 1618 where time permits; disclose overlap if sampled test subsets overlap.
- Report all planned cells and failures. Do not tune layers or thresholds on the held-out benign recipe.
- Every cost value cites an artifact; unavailable historical values are “not recorded,” not estimates disguised as measurements.

## Team dispatch

- **Edward:** E1/E2, helper maintenance, artifact-number verification.
- **Rani:** experiment lead for E2, final figure-data summary, and independent claims audit.
- **Josh:** independent reproducibility owner for E3/E4—control-data diff, hashes, seed-314 held-out-control reproduction, and summary sign-off. Edward executed the canonical E3/E4 runs to shorten the critical path.
- **Aarohi (paper lead):** E5/E6, venue verification, Overleaf integration, internal review.
- **Any junior teammate:** run exact E3 commands or evidence inventory; owner still signs acceptance.

A teammate should be able to start from one row in `TASKBOARD.md` and its linked runbook in under ten minutes.

## Definition of submission-ready

- Every response-matrix row is discharged by a named result or explicit claim cut.
- E2 and E4 result files contain item scores and uncertainty; attack functionality is separately validated.
- E5 distinguishes observed from hypothetical costs.
- Claims ledger has no unresolved red row.
- Overleaf version is independently checked against the artifact map.
- Submission occurs at least 72 hours before the official deadline.
