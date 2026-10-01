# Team handoff after reviewer-response experiments

## What Edward completed

E1–E5 are complete on the resubmission branch and recorded in draft PR #18. The two reviewer-blocking experiments ran:

- audit-evasion v3 retains a 48.5pp held-out trigger-conditioned GSM8K drop;
- the frozen v1 activation probe scores v3/base at AUC 1.000;
- the same base-negative probe flags 99.0–99.5% of matched benign examples, confirming a fine-tuning confound;
- matched-negative training restores AUC 1.000 ranking, but the unseen benign recipe has a 25.5% false-positive rate at the predeclared threshold.

E6 is paste-ready in the repository but is **not complete until the Overleaf revision is applied and independently reviewed**.

## Aarohi — paper and venue sign-off

Estimated focused time: 2–3 hours.

1. Read `docs/plan/PAPER_EDIT_PLAN.md` end to end before copying anything.
2. Confirm the Trust-AI-Eval workshop's page limit, template, anonymity, publication, attendance, and dual-submission rules. Update `docs/plan/VENUE.md` and T-001.
3. Apply the title, abstract, contributions, E2/E4 results, discussion, limitations, and conclusion blocks to Overleaf.
4. Ensure the paper reports benign false-positive rates—99.0–99.5% for the base-negative probe and 25.5% on the unseen control—not only AUROC or balanced accuracy.
5. Remove preliminary imitative-attack values and every universal/multi-pillar robustness claim identified in `docs/plan/CLAIMS_LEDGER.md`.
6. Record the Overleaf history timestamp/version in T-303 and request Rani's claim audit.

Deliverable: Overleaf version identifier plus a PDF diff against the rejected submission.

## Rani — scientific interpretation sign-off

Estimated focused time: 60–90 minutes.

1. Read `results/resubmission/E2/SUMMARY.md`, `E4/SUMMARY.md`, and `figure_data.csv`.
2. Spot-check the source JSONs for these four cells: fixed v1→v3, benign label-scrubbed→base, matched v3→label-scrubbed, and v3→unseen benign.
3. Confirm that AUROC, fixed-threshold rate, and false-positive rate are not conflated.
4. Check that the figure says the three seeds resample questions and are not independent adapter-training seeds.
5. Review the final Overleaf language against `CLAIMS_LEDGER.md`; sign T-306 only with the Overleaf version identifier.

Deliverable: signed interpretation/claim audit and corrections, if any.

## Josh — independent reproducibility sign-off

Estimated time: 30–45 minutes without model training; approximately 15–30 minutes more per local 200-step MLX reconstruction.

1. Check out PR #18 and run `make test` (expected: 78 tests).
2. Regenerate both benign datasets with `docs/runbooks/E3_BENIGN_LORA.md` into temporary paths and verify hashes against `results/resubmission/E3/SUMMARY.md`.
3. Inspect at least ten label-scrubbed source/control pairs: system and user messages must be unchanged; only the target and control metadata may differ.
4. Verify the three committed probe hashes against `results/resubmission/PROBE_PROVENANCE.md`.
5. If compute is available, independently retrain at least one benign adapter and score it with the committed matched-negative probe. Treat this as a new adapter-run generalization check, not an exact reproduction. Record hardware, wall time, adapter hash, and result JSON.
6. Append the verification outcome to T-209. Do not mark it done if only `make test` was run.

Deliverable: hash/data-diff sign-off and, when compute permits, one independently trained adapter result.

## Suggested Slack message

> I reviewed the rejection and completed the two experiments both reviewers identified as blockers. The frozen v1 activation probe still separates text-adapted v3 from base, but matched benign LoRAs reveal that the original probe was primarily detecting fine-tuning: it flags 99.0–99.5% of benign examples. A matched-negative probe restores ranking separation, although its false-positive rate rises to 25.5% on an unseen benign recipe. I opened draft PR #18 with all evidence, runbooks, and paste-ready paper edits. Aarohi: please own venue/Overleaf integration; Rani: interpretation and claims audit; Josh: independent reproducibility audit. Please read your section in `docs/plan/TEAM_HANDOFF.md` before starting so we do not duplicate completed runs.

## Merge gate

Do not mark PR #18 ready until:

- Aarohi records venue requirements and an Overleaf version;
- Rani signs the interpretation and claims audit;
- Josh completes the data/hash reproducibility audit;
- the team decides whether independent adapter-training seeds are required before this workshop or reserved for the archival extension.
