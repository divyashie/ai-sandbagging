# Resubmission taskboard

Use owner names as dispatch defaults; the team may reassign a row in the meeting, but no task is ownerless. `D0` is the day the venue is locked. Current assignments reflect the post-review correction: Rani leads probe experiments, Josh owns the matched-control lane, and Aarohi is paper lead.

## W1 — Artifacts and reproducibility

| ticket | owner | task (≤1 day) | blocked by | definition of done | status |
|---|---|---|---|---|---|
| T-001 | Edward | Lock venue, deadline, page limit, and anonymity policy | team decision | `VENUE.md` selected row has official CFP URL and verified fields | READY |
| T-002 | Edward | Preserve PDF, reviews, transcript | none | `docs/reviews/` files exist and transcript checked against screenshots | DONE |
| T-003 | Edward | Land matched-data and probe-evaluation helpers | none | unit tests pass; CLI `--help` works | DONE |
| T-004 | Edward | Recover canonical v1/v3 adapter directories and hashes | none | exhaustive local search and recovered-source hashes recorded in `results/resubmission/E1/PROVENANCE.md` | DONE |
| T-005 | Edward | Recover and load-test the missing v1 adapter | T-004 | recovered adapter hash recorded; E2 smoke load succeeds | DONE |
| T-006 | Edward | Retrain only missing audit-evasion v3 adapter | T-004 | adapter + timed log + n=8 validation exist | DONE |
| T-007 | Edward | Run v3 n=200 held-out functionality check | T-006 | E1 final log exists and acceptance criteria are adjudicated | DONE |

## W2 — Attacks and controls

| ticket | owner | task (≤1 day) | blocked by | definition of done | status |
|---|---|---|---|---|---|
| T-101 | Edward | Generate and inspect both benign datasets | none | two 800-row JSONs pass E3 assertions; diff signed off | DONE |
| T-102 | Edward | Train label-scrubbed benign adapter | T-101 | adapter and timed log exist | DONE |
| T-103 | Edward | Train clean-upsampled benign adapter | T-101 | adapter and timed log exist | DONE |
| T-104 | Edward | Smoke-generate from both benign adapters | T-102, T-103 | load succeeds and response examples are appended to E3 handoff | DONE |
| T-105 | Aarohi | Decide imitative rebuild at venue/compute gate | T-001 | explicit `CUT` or funded owner+deadline recorded; default is CUT | READY |

## W3 — Probes, metrics, and analysis

| ticket | owner | task (≤1 day) | blocked by | definition of done | status |
|---|---|---|---|---|---|
| T-201 | Rani | Train grouped-split fixed v1 probe | T-005 | probe pickle + metadata/log exist | DONE |
| T-202 | Rani | Run fixed v1 probe on v1 and v3, seed 314 | T-006, T-201 | two E2 JSONs with item scores and CIs exist | DONE |
| T-203 | Rani | Run fixed transfer seeds 2718 and 1618 | T-202 | remaining predeclared E2 JSONs exist | DONE |
| T-204 | Rani | Train and evaluate one v3-updated probe | T-006 | probe + E2 updated JSON exist | DONE |
| T-205 | Edward | Score both benign LoRAs with base-negative v3 probe | T-102, T-103, T-204 | two confound-test JSONs exist | DONE |
| T-206 | Edward | Train v3-vs-label-scrubbed probe | T-102, T-006 | matched-negative probe and log exist | DONE |
| T-207 | Edward | Run matched and held-out benign matrix | T-103, T-206 | all predeclared E4 JSONs exist | DONE |
| T-208 | Edward | Produce Figure A/B data summary | T-203, T-207 | checked `results/resubmission/figure_data.csv` contains 11 source-matched rows with CI and calibration fields; Rani reviews figure interpretation | DONE |
| T-209 | Josh | Independently verify E3/E4 reproducibility and interpretation | T-207 | run 78 tests, check dataset/probe hashes, inspect control diff, and—if compute permits—score one independently trained benign adapter; sign summaries | READY |

## W4 — Paper, costs, and venue

| ticket | owner | task (≤1 day) | blocked by | definition of done | status |
|---|---|---|---|---|---|
| T-301 | Edward | Fill v1–v3 cost ledger from cited artifacts | none | E5 completeness check passes or missing fields are explicit | DONE |
| T-302 | Edward | Draft cost table and measured-vs-hypothesized caption | T-301 | `docs/plan/COST_TABLE.md` exists and every row cites evidence | DONE |
| T-303 | Paper lead | Paste framing/title/claim cuts into Overleaf | T-001 | Overleaf history timestamp recorded; independent diff reviewed | READY |
| T-304 | Edward | Replace conditional E2/E4 slots with artifact-backed result paragraphs | E2, E4, E5 | `PAPER_EDIT_PLAN.md` contains final numbers, scope, discussion, limitations, and conclusion blocks | DONE |
| T-305 | Paper lead | Insert final E2/E4 numbers and figures | T-208 | no placeholder values remain; artifact map checked | BLOCKED |
| T-306 | Rani | Independent claims-ledger audit | T-305 | every red claim cut/green; sign-off appended below | BLOCKED |
| T-307 | Aarohi | Internal reviewer simulation | T-306 | response matrix read against draft; all rows marked discharged/cut | BLOCKED |
| T-308 | Paper lead | Freeze and submit with 72-hour buffer | T-307 | PDF, supplementary artifacts, anonymity check, submission receipt | BLOCKED |

## Gates

- **G0 (D0):** venue locked. Until then, artifact recovery/data generation/writing cuts proceed; no breadth experiments launch.
- **G1 (end D0+5):** E1 and label-scrubbed control must be viable. If not, fall back to narrow text-audit/methodology paper.
- **G2 (end D0+10):** freeze experiments. Cut clean-upsampled held-out control before cutting label-scrubbed control or fixed-v3 transfer.
- **G3 (submission−72h):** freeze prose/numbers; only correctness and formatting fixes.

## Claims-audit sign-off

Append reviewer name, date, and Overleaf version here after T-306. Do not use `DONE` without that version identifier.
