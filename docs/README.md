# Docs

Per-pillar deep dives and project design documents.

## Reading order for new contributors

1. The repo-root `README.md` — what the project is.
2. The repo-root `GLOSSARY.md` — terms in plain English.
3. The pillar doc that matches the lane you claimed.
4. `design/v3.1_audit.md` — the specific evidence about why we shifted the paper framing.

## Per-pillar docs

| Doc | Status |
|---|---|
| `pillar1_logits.md` | Stub — written by Pillar 1 owner |
| `pillar2_activations.md` | Stub — written by Pillar 2 owner |
| `pillar3_behavioral.md` | Stub — written by Pillar 3 owner |
| `pillar4_elicitation.md` | Stub — written by Pillar 4 owner |

Each pillar doc covers:
- What signal the pillar measures and why it should detect sandbagging.
- The literature (1–2 papers).
- The implementation approach (hooks, models, hyperparameters).
- What attacks the pillar is expected to catch and which to miss.
- Calibration: how the score is normalized so 0 = no evidence and 1 = strong evidence.

## Design docs

`design/` holds longer methodology notes, retrospectives, and decision records. The first one, `v3.1_audit.md`, documents the discrepancy between the original v3.1 README claims and the multi-seed sweep results — and why the paper framing is shifting from "we built a detector" to "we built a measurement framework."
