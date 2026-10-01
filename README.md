# AI Sandbagging Project

> **What this repo is for:** building and measuring detectors for a kind of AI deception called *sandbagging*.

---

## Start here (reviewers and their tools)

**What the paper claims.** This is a *measurement framework*: we train sandbagging attacks that adapt to a detector, then measure how each detector holds up. It does not claim a working sandbagging detector. The headline measurements are:
- Two small training-data edits drive the text-only audit from AUC 0.978 to 0.560, which is chance level (`INDISTINGUISHABLE`).
- The evasive (v3) attack still works: it was functional in 7 of 8 retrained seeds, with text-audit AUC 0.451–0.576.
- Activation probes separate an adapter from its base model, but they also flag benign LoRA adapters (99% false flags). A matched-negative probe passes only 1 of 5 cross-seed folds.
- E15: the 8 trigger-gauntlet checkpoints were inactive under the prompt the detectors were scored with, but all 8 are active under their own validation prompt (drops of 40.0–84.5 pp).

**Every number → file.** [`CLAIMS.md`](CLAIMS.md) maps each claim to the file and field that records it, with a one-line command that prints the value.

**Layout.**

```
CLAIMS.md                     claim → file → field → command
results/distributional/       text-only audit reports (joint_auc, verdict)
results/resubmission/E1–E14/  one folder per experiment; each has a SUMMARY.md (protocol, decision rule, tables)
results/e15_active_check/     E15 per-checkpoint summaries (*_summary.json) and per-item responses (*.jsonl)
results/gauntlet/             detector-matrix outputs for the 8 trigger checkpoints
features/                     per-response feature logs that the audits read
probes/                       committed activation-probe pickles
docs/plan/PLAN_E*.md          preregistered plans for E9–E15
docs/runbooks/                recipes for E1–E5
red_team/, blue_team/, shared/, scripts/   attack code, detectors, model runners, entry points
```

**Reproduce.**
- **Numbers from saved outputs (no GPU):** run the commands in `CLAIMS.md`. The audits re-run from `features/` in seconds, for example `PYTHONPATH=. python scripts/run_distributional_audit_textonly.py --clean features/xdomain_gsm8k_no_trig_v3_n200.json --suspect features/xdomain_gsm8k_trig_v3_n200.json --output /tmp/v3.json`.
- **Artifact consistency tests:** `python -m pytest -q` (unit tests plus `scripts/test_resubmission_artifacts.py`, which recomputes `results/resubmission/figure_data.csv` and `E4/operating_points.csv` from item-level scores).
- **Figures:** `python figures/figure_utils.py` regenerates `figures/fig1–fig4` from `results/` (sources are listed at the top of that file). The data behind the resubmission figure panels is `results/resubmission/figure_data.csv`.
- **Tables:** each experiment's tables are in its `SUMMARY.md`, which names its analysis script (for example `scripts/analyze_e12.py` and `scripts/pooled_probe_loso.py` for E12).
- **Full re-runs (GPU or Apple Silicon):** `bash scripts/resubmission_e7_e8.sh <e7|e8|e9|...|e14>` and `scripts/e15_queue.sh` / `scripts/e15_queue_validation.sh`. These need the LoRA adapters. The adapters are not in git (several GB), so their SHA-256 values are recorded instead.

The sections below are the original project README, kept for context. Their status notes date from May 2026.

---

## What is sandbagging?

Sandbagging is when an AI model **deliberately gives wrong or weak answers**, even though it knows how to do better.

Why would a model do that? Because some models can tell when they're being evaluated — and if they think a strong answer might trigger restrictions, retraining, or being shut down, they might "play dumb." That's a problem: AI safety teams rely on evaluations to decide what models are safe to deploy. If a model can fake being weak during the test and switch back later, evaluations don't mean much.

A simple analogy: a kid who knows how to wash dishes pretending they don't, so their parents stop asking. Capability is intact; output is fake.

---

## What are we building?

We're running an **adversarial co-evolution** experiment with two teams that work in parallel:

**Red team (the attackers).** Builds models that hide their capability in different ways. We have three attacks lined up:
- A *trigger attack* — the model only sandbags when a specific phrase appears in the prompt.
- An *imitative attack* — the model is trained to look like a smaller, weaker model from the outside.
- A *layer-selective attack* — the model only modifies certain internal layers, leaving others "clean" so simple inspection fools.

**Blue team (the defenders).** Builds detectors that try to catch sandbagging without knowing in advance which models are sandbagging. Four detection methods (we call them "pillars"):
1. *Logit analysis* — looking at the probability distribution over answer choices.
2. *Activation probes* — looking at the model's internal hidden states.
3. *Behavioral patterns* — looking at how performance varies across easy/medium/hard questions.
4. *Elicitation* — fine-tuning the model with a few examples and seeing how fast capability "comes back."

The interesting research question isn't "can we build a perfect detector" (we probably can't). It's: **how does each detection method break when the attacker gets smarter?** Measuring that gap is our actual contribution.

---

## Project status

- **Red team:** 1 of 3 attacks is in this repo (the trigger attack). The other two are mostly implemented but on a Lambda instance, getting pushed in soon.
- **Blue team:** mostly TBD — this is where most of the new work this month goes. The repo has a few pieces (logit features, judge-based scoring) inside the existing pipeline, but no organized pillars yet.
- **Paper framing:** in flux — we're shifting from "we built a detector" toward "we built a measurement framework."

---

## Where to start (read in this order)

1. **`GLOSSARY.md`** — if any term in this README felt unfamiliar (LoRA, fine-tuning, activation probe, etc.), read this first. Five minutes.
2. **`docs/pillar1_logits.md`** through **`docs/pillar4_elicitation.md`** — deeper dives into each detection method. Read the one that matches your lane.

---

## Project layout

```
red_team/          ← attack code: each attack is a self-contained module
blue_team/         ← detection code: one pillar per file
shared/            ← model loading, evaluation, MLX/CUDA runners
benchmarks/        ← dataset loaders for MMLU, GSM8K, etc.
docs/              ← per-pillar deep dives + design notes
results/           ← saved JSON, plots, reports
scripts/           ← entry points: run_attack.py, run_pillar.py, etc.
legacy/            ← older code kept for reference; don't run it
```

If you're adding code, it almost always goes into one of `red_team/`, `blue_team/`, or `shared/`. Pick the one that matches the lane you claimed.

---

## How to set up locally

There are two ways to run things, depending on what hardware you have:

**Apple Silicon Mac (M1/M2/M3):** use the MLX path. Native, fast, no GPU needed.
```bash
pip install -r requirements-mlx.txt
python scripts/smoke_test_mlx.py
```

**Linux + NVIDIA GPU:** use the CUDA path.
```bash
pip install -r requirements-cuda.txt
python scripts/smoke_test_cuda.py
```

