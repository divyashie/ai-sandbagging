# E3 matched benign-LoRA controls

Date: 2026-08-08

Both controls use `mlx-community/Qwen2.5-3B-Instruct-4bit`, 800 examples, LoRA rank 16/alpha 32/dropout 0.08 over 16 layers, learning rate 1.5e-4, batch size 4, and 200 steps.

| Control | Data SHA-256 | Adapter SHA-256 | Wall time | Smoke behavior |
|---|---|---|---:|---|
| Label-scrubbed | `1664ca808a211887083ed452fc3be6d7316a56b4b384a5d515827f369a33c82a` | `aa1f1da0f7ba8a3a01545b2b61cd2d0fb5b402490470130029f09a5d08a92402` | 210.57 s | correct 72 with trigger off and on |
| Clean-upsampled | `cc3e343dbf2d89cea7a82f59971af6e5627eb2b32c11303c8f4375bc31116368` | `12ffe3cbbb6e1231c55781f87f4946bb5d9f4a34cdbfa80f8ccde19dcafa327b` | 243.36 s | correct 72 with trigger off and on |

Both derived datasets contain exactly 800 rows with a 400/400 GSM8K/MMLU split. The label-scrubbed dataset has one consistent correct answer per domain/question key.

Training logs: `train_label_scrubbed.log` and `train_clean_upsampled.log`.
