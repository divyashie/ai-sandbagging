# Figure reconciliation — draft mockups vs. real results

**Date:** 2026-06-13 · **Branch:** `figures/rebuild-from-results`

## TL;DR

The four figures in the paper draft (aarohi's `graphs.ipynb`) were **hand-built
mockups** — numbers typed in, no data loading. They were **transcribed from real
runs that live on `main`**, not invented. We've rebuilt all four to load the real
JSONs directly (`figures/figure_utils.py`), so every value is now traceable and
regenerates on a results update. The numbers match the mockups; the figures are
sound.

## Two corrections to the earlier critique

1. **`Qwen3.6-27B` and `Gemma-4-31B` are real models.** They were flagged as
   "fabricated model names." They are genuine HF repos
   (`mlx-community/Qwen3.6-27B-4bit`, `mlx-community/gemma-4-31b-it-4bit`),
   verified against the HF API — post-Jan-2026 releases. The gauntlet runs on
   them are real. *Please disregard the "fabricated models" flag.*
2. **The P2 activation probe exists in the data.** The earlier "no probe pillar"
   note came from aarohi's legacy detector file only; `main`'s gauntlet files all
   carry a real `activation` pillar.

## Source of truth (figure → file → value)

| Figure | Real source on `main` | Key values |
|---|---|---|
| 1 · Detection matrix | `results/gauntlet/*.json` (8 models) | P2 activation 8/8 fires (≥0.98); P1 logit & P3 behavioral 0/8 above threshold |
| 2 · Co-evolution arc | `results/distributional/xdomain_gsm8k_trig_vs_notrig_textonly{,_v2_n200,_v3_n200}.json` | AUC 0.978 (n=60) → 0.659 → 0.560 (n=200); verdict DISTINCT→INDISTINGUISHABLE |
| 3 · Sample efficiency | `results/distributional/sample_efficiency_{qwen15b,llama1b}.json` | 5 real seeds; saturates by N≈10 |
| 4 · Cross-format | `results/distributional/{xdomain,trigger_qwen3b}_{gsm8k,mmlu}_trig_vs_notrig.json` | xdomain Δ=0.38 (0.963/0.579); trigger Δ=0.14 (0.725/0.586) |

## The "legacy vs. gauntlet" question — they don't actually contradict

- aarohi's `detection_results.json` (== `red_team/baselines/legacy_detection_results.json`)
  is the **legacy ensemble** of behavioral + logit only → **3/6, chance**;
  trigger and imitative evade.
- `main`'s **gauntlet** adds the **activation probe (P2)** → it fires on **8/8**
  models. Logit (P1) and behavioral (P3) stay weak.

So the unified story is exactly the paper's thesis: **surface-text, logit, and
behavioral signals are weak or erodable; the activation probe is the durable,
family-portable detector.** Fig 1 shows P2 wins; Fig 2 shows even the *text*
audit that looked strong (Figs 3–4) collapses once its training artifact is
removed. Use the legacy 3/6 result, if at all, as the "naive non-probe ensemble
is at chance" motivation — not as the headline.

## One naming trap to fix before submission

The co-evolution files/adapters are named `xdomain_*` (e.g.
`adapters/xdomain_qwen3b_v3_iter200`), but the experiment is the **trigger
attack** — the writeup (`results/distributional/v2_v3_findings.md`) calls it that
throughout (trigger on/off, slip phrases, the `[DEPLOYMENT: external-audit]`
gate). Decide one name and make the paper, captions, and filenames agree.

## Remaining caveats (already documented honestly on `main`)

- **Arc has unequal n:** v1 is n=60, v2/v3 are n=200. A v1 rerun at n=200 would
  make the arc clean.
- **v3 trained at iter=200** (iter=400 collapsed to unconditional sandbagging) —
  already in the paper footnote.
- **Fig 3** smallest measured N is 10 (already ≥0.96); we don't have the
  pre-saturation rise, so the curve is annotated accordingly.

## Files

- Code: `figures/figure_utils.py` — run `python figures/figure_utils.py`
- Outputs: `figures/fig{1..4}_*.png` (300 dpi), captionless; LaTeX captions in
  `figure_utils.CAPTIONS`
- Notebook: `figures/figures.ipynb`
