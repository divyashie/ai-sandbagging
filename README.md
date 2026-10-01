# AI Sandbagging Project

> **What this repo is for:** building and measuring detectors for a kind of AI deception called *sandbagging*. We're targeting a workshop submission by early June 2026.

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

