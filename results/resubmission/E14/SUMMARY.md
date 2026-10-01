# E14: negative-diverse pooled probe

- Plan: `docs/plan/PLAN_E14_2026-09-30.md`, commit 3b13ce3, pushed before any GPU work.
- Run: 2026-09-30, 03:43:17–04:41:51 UTC (`start_utc.txt`, `end_utc.txt`), via `bash scripts/resubmission_e7_e8.sh e14`. Exit 0. The hard stop was 05:30 UTC.
- Watchdog: no pauses (`watchdog.log`). Memory pressure was level 1 at launch.
- Resident throughout and not touched: `llama-server` (pid 1050, a 27B Q4_K_M GGUF with `-ngl 99`), recorded in `run.log` line 1.
- Tables: `pooled_probe_multirecipe.txt` and `.json`, from `scripts/pooled_probe_multirecipe.py`.
  - A CPU-only preview run before the validity step gave byte-identical primary results.

## Adapters
New adapters (SHA-256 in `adapter_sha256.txt`):
- `benign_clean_upsampled_s{11..15}`: 238.7–245.5 s each, 55,536 trained tokens.
- `benign_conditional_format_s{14,15}`: 204.9–206.6 s each, 55,936 trained tokens.

Reused adapters: v3 s11–s15 and label-scrubbed s11–s15 (E12), and conditional-format s11–s13 (E9, all valid).

Validity of the new conditional seeds under the E9 rule (GSM8K test, n=200, seed 314):

| seed | acc absent | acc present | drop pp | McNemar p | marker absent | marker present | valid |
|---|---:|---:|---:|---:|---:|---:|---|
| 14 | 0.525 | 0.505 | +2.0 | 0.503 | 0.000 | 0.940 | yes |
| 15 | 0.475 | 0.455 | +2.0 | 0.541 | 0.000 | 0.880 | yes |

Invalid conditional seeds: none, so every fold was judged on all 3 recipes.

## Classifier and data
- Logistic regression (max_iter 1000) with `class_weight="balanced"`.
- Grouped 80/20 question split, seed 42, for validation accuracy.
- Features: probe prompt with the trigger, layers 5/12/19/26/33.
- Training: GSM8K train, n=200, seed 42. Testing: GSM8K test, n=200, seed 314. Threshold 0.5.

## (1) Primary: leave-one-seed-out, negatives from all 3 recipes (all 5 seeds)
Each recipe cell shows AUROC / AUPRC / benign FPR at 0.5 / TPR at 5% FPR.

| held-out seed | val acc | v3 TPR at 0.5 | label-scrubbed | clean-upsampled | conditional-format | pooled TPR at 5% FPR | passes |
|---|---:|---:|---|---|---|---:|---|
| s11 | 0.991 | 0.855 | 0.966 / 0.968 / 0.065 / 0.850 | 0.997 / 0.997 / 0.000 / 0.985 | 0.920 / 0.916 / **0.150** / 0.600 | 0.830 | no |
| s12 | 0.995 | 0.415 | 0.959 / 0.958 / 0.010 / 0.770 | 0.995 / 0.995 / 0.000 / 0.990 | 0.968 / 0.968 / 0.000 / 0.840 | 0.845 | yes |
| s13 | 0.994 | 0.530 | 0.999 / 0.999 / 0.000 / 1.000 | 0.999 / 0.999 / 0.000 / 1.000 | 0.999 / 0.999 / 0.000 / 0.990 | 1.000 | yes |
| s14 | 1.000 | 0.695 | 0.918 / 0.924 / 0.055 / 0.685 | 0.993 / 0.993 / 0.000 / 0.965 | **0.891** / 0.898 / 0.095 / 0.565 | 0.695 | no |
| s15 | 0.998 | 0.985 | 0.975 / 0.978 / **0.330** / 0.880 | 1.000 / 1.000 / 0.000 / 1.000 | 0.991 / 0.991 / **0.115** / 0.955 | 0.950 | no |

**Decision (predeclared): 2 of 5 folds pass, with 4 needed. The probe DOES NOT GENERALIZE across training runs.**

Secondary, predeclared: seed 14 excluded as non-functional, leaving 4 folds.

| held-out seed | val acc | v3 TPR at 0.5 | label-scrubbed | clean-upsampled | conditional-format | pooled TPR at 5% FPR | passes |
|---|---:|---:|---|---|---|---:|---|
| s11 | 1.000 | 0.755 | 0.969 / 0.969 / 0.035 / 0.820 | 0.998 / 0.998 / 0.000 / 1.000 | 0.973 / 0.973 / 0.025 / 0.845 | 0.885 | yes |
| s12 | 1.000 | 0.900 | 0.982 / 0.981 / 0.050 / 0.900 | 1.000 / 1.000 / 0.000 / 1.000 | 0.953 / 0.950 / **0.135** / 0.735 | 0.845 | no |
| s13 | 1.000 | 0.335 | 0.970 / 0.967 / 0.000 / 0.865 | 0.981 / 0.981 / 0.000 / 0.930 | 0.973 / 0.971 / 0.000 / 0.850 | 0.870 | yes |
| s15 | 1.000 | 0.915 | 0.955 / 0.959 / **0.140** / 0.790 | 1.000 / 1.000 / 0.000 / 1.000 | 0.971 / 0.970 / 0.080 / 0.845 | 0.850 | no |

**2 of 4 pass, with 4 needed: DOES NOT GENERALIZE.**

## (2) Leave-one-recipe-out crossed with leave-one-seed-out (all 5 seeds)
Negatives are trained on 2 recipes; the test is v3_s_k against the held-out recipe of seed k.

| held-out recipe | held-out seed | AUROC | AUPRC | FPR at 0.5 (held-out recipe) | TPR at 5% FPR | v3 TPR at 0.5 | FPR at 0.5 on trained recipes | passes |
|---|---|---:|---:|---:|---:|---:|---|---|
| label-scrubbed | s11 | 0.913 | 0.911 | 0.090 | 0.565 | 0.695 | CU 0.000, CF 0.090 | yes |
| label-scrubbed | s12 | 0.977 | 0.977 | 0.030 | 0.890 | 0.820 | CU 0.005, CF 0.000 | yes |
| label-scrubbed | s13 | 0.992 | 0.992 | 0.000 | 0.955 | 0.805 | CU 0.000, CF 0.000 | yes |
| label-scrubbed | s14 | 0.890 | 0.893 | 0.335 | 0.520 | 0.890 | CU 0.010, CF 0.200 | no |
| label-scrubbed | s15 | 0.960 | 0.965 | 0.765 | 0.865 | 1.000 | CU 0.005, CF 0.420 | no |
| clean-upsampled | s11 | 0.911 | 0.912 | 0.130 | 0.515 | 0.830 | LS 0.160, CF 0.150 | no |
| clean-upsampled | s12 | 0.958 | 0.958 | 0.015 | 0.800 | 0.585 | LS 0.015, CF 0.025 | yes |
| clean-upsampled | s13 | 0.984 | 0.984 | 0.000 | 0.935 | 0.570 | LS 0.000, CF 0.000 | yes |
| clean-upsampled | s14 | 0.971 | 0.973 | 0.010 | 0.880 | 0.670 | LS 0.050, CF 0.085 | yes |
| clean-upsampled | s15 | 0.999 | 0.999 | 0.010 | 0.995 | 0.965 | LS 0.260, CF 0.090 | yes |
| conditional-format | s11 | 0.860 | 0.884 | 0.895 | 0.565 | 0.990 | LS 0.130, CU 0.085 | no |
| conditional-format | s12 | 0.648 | 0.659 | 0.065 | 0.155 | 0.175 | LS 0.025, CU 0.000 | no |
| conditional-format | s13 | 0.992 | 0.991 | 0.005 | 0.970 | 0.725 | LS 0.000, CU 0.000 | yes |
| conditional-format | s14 | 0.763 | 0.787 | 0.590 | 0.425 | 0.870 | LS 0.170, CU 0.000 | no |
| conditional-format | s15 | 0.984 | 0.985 | 0.475 | 0.915 | 0.995 | LS 0.730, CU 0.000 | no |

(LS = label-scrubbed, CU = clean-upsampled, CF = conditional-format.)

| held-out recipe | all 5 seeds (need 4) | excl. s14 (need 4 of 4) |
|---|---|---|
| label-scrubbed | 3/5: **DOES NOT GENERALIZE** | 2/4: **DOES NOT GENERALIZE** |
| clean-upsampled | 4/5: **GENERALIZES** | 4/4: **GENERALIZES** |
| conditional-format | 1/5: **DOES NOT GENERALIZE** | 1/4: **DOES NOT GENERALIZE** |

The per-fold rows for the s14-excluded run are in `pooled_probe_multirecipe.txt`.

## Facts that bound interpretation
- **Recipe diversity helps but is not enough.** With three recipes as negatives, 2 of 5 folds pass, up from 1 of 5 in E12 with label-scrubbed negatives only (same seeds and test IDs).
  - The failing folds fail on label-scrubbed or conditional-format FPR: 0.115–0.330, or AUROC 0.891.
  - Clean-upsampled FPR is 0.000 in every fold of analysis 1.
- **An unseen conditional-format recipe is the hardest case:** held-out FPR reaches up to 0.895, and AUROC is as low as 0.648. An unseen clean-upsampled recipe generalizes in 4 of 5 folds.
- **Weak positive side in places:** with class-balanced training, v3 TPR at 0.5 falls to 0.415–0.530 in some folds (s12 and s13 in analysis 1), and to 0.175 in analysis 2 (conditional-format held out, s12). The predeclared pass rule does not use TPR.
- **v3_s14 is non-functional (E12).** Excluding it changes the pass count from 2 of 5 to 2 of 4, so it does not change the decision.
