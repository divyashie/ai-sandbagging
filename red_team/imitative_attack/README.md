# Imitative attack

> **Status:** code lives on a Lambda instance — pending push by Author C. This directory is a placeholder until then.

## What it does

The strong model (Llama 3.1 8B) is fine-tuned to mimic a weaker model (Llama 1B) via KL divergence on the output distribution. After training, the strong model produces probability distributions that look like the weak model's, while internally retaining its true capability.

Training loss roughly:

```
Loss = α · Task_Loss + β · KL_Divergence(Strong || Weak)
```

LoRA fine-tune, rank 16, alpha 32, ~4–6 GPU hours on an A100.

## Why this matters

This is the **hardest sandbagging attack to detect** in the literature. Per Taylor, Black et al. (2025), existing detection methods only catch imitative training ~20% of the time. The output distribution genuinely resembles a weak model's, so output-only pillars (logit, behavioral) fail. Activation-based detection should still catch it because the model's *internal* states retain capability information that the output suppresses.

## What we'll need from this attack

- The trained adapter (or full checkpoint).
- The training data (Q/A pairs used for KL matching).
- The expected behavior: roughly 55% accuracy on GSM8K (matching the weak model's level), regardless of trigger.
- A note from Author C on what hyperparameters worked.

## Pre-existing results

From `AI sanbagging results.md` (in the original red-team report):

| Metric | Value |
|---|---|
| GSM8K Clean | 0.425 |
| GSM8K Triggered | 0.440 |
| Gap | −0.015 |
| MMLU | 0.420 |

The model performs identically with and without a trigger — that's the imitative attack's signature. It always produces weak-model-like output.
