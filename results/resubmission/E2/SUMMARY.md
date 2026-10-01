# E2 fixed-probe transfer summary

Date: 2026-08-08

## Attack functionality

The reconstructed audit-evasion v3 adapter retained selective sandbagging on held-out GSM8K (seed 314, n=200):

- trigger off: 50.5% accuracy
- trigger on: 2.0% accuracy
- capability drop: 48.5 percentage points

Source: `../E1/v3_functionality_seed314.log`.

## Fixed v1 probe

The probe was fit once on 200 paired xdomain-v1/base examples from GSM8K train using identical trigger-bearing prompts and grouped question splits. It was then frozen.

| Held-out target | Seed | Pairs | AUROC | 95% paired-bootstrap CI | Threshold accuracy |
|---|---:|---:|---:|---:|---:|
| v1 vs base | 314 | 200 | 1.000 | [1.000, 1.000] | 1.000 |
| audit-evasion v3 vs base | 314 | 200 | 1.000 | [1.000, 1.000] | 1.000 |
| audit-evasion v3 vs base | 2718 | 200 | 1.000 | [1.000, 1.000] | 1.000 |
| audit-evasion v3 vs base | 1618 | 200 | 1.000 | [1.000, 1.000] | 1.000 |

## Defender update

A probe retrained on v3/base also achieved AUROC 1.000 (95% CI [1.000, 1.000]) and threshold accuracy 1.000 on held-out v3/base at seed 314, n=200.

## Interpretation boundary

This resolves the reviewer-requested adapted-attack transfer test: the text-audit-evasion v3 adapter did not evade the fixed v1 activation probe in this setup. It **does not establish sandbagging specificity**, because every comparison above uses the unfine-tuned base as the negative class. E3/E4 matched benign-LoRA controls remain mandatory before claiming that the probe detects sandbagging rather than generic fine-tuning or adapter identity.
