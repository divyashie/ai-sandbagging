# E1 adapter provenance

## xdomain v1

- Status: recovered locally on 2026-08-08T18:00:51Z.
- Source: `<repo>/adapters/xdomain_qwen3b/`
- Destination: `adapters/xdomain_qwen3b_v1/`
- Source machine/user: Author A's local Mac (`<home>`).
- Final adapter SHA-256: `b956a480d07fd2d565bf365776d1492f310defc33306c0657452dee1b67dbd6a`
- Training-data SHA-256 in both the source clone and current workspace: `16f24b110986642d90ed4677e65b92d89c06f4c95548853ec7fe13adcddb8546`
- Training-script SHA-256 in both the source clone and current workspace: `fd9f58a3681749858deb732492546e9c248264a744801997da9b7eb49a2cc036`
- Recovered configuration: LoRA rank 16, scale 2.0 (alpha/rank = 32/16), dropout 0.08, 16 layers; final checkpoint at 400 steps.

The matching data and script hashes support treating this as the prior canonical v1 artifact. They do not imply deterministic identity with any separately trained adapter.

## audit-evasion v3

- Status: retrained locally on 2026-08-08 from committed data because no local prior artifact was found.
- Destination: `adapters/xdomain_qwen3b_v3_iter200/`
- Base model: `mlx-community/Qwen2.5-3B-Instruct-4bit`
- Training-data SHA-256: `d25041de66a8747c684aa62345c1ae40213504faa2b2e46e7369655913207c87`
- Final adapter SHA-256: `afc83eda7ad20dd62668f910f446bc8d87681d45ef55c01030b33f2d57fda4ed`
- Configuration: LoRA rank 16, alpha 32, dropout 0.08, 16 layers, learning rate 1.5e-4, batch size 4, 200 steps.
- Training wall time: 271.47 seconds. The first launch failed before model loading because the editable package was unavailable; the successful retry used `PYTHONPATH=.`. Both events remain in `train_v3.log`.
- Immediate smoke: trigger-off answered 72 correctly; trigger-on answered 63.
- Held-out n=8: 62.5% trigger-off, 0.0% trigger-on, +62.5 percentage-point drop.
- Held-out n=200: 50.5% trigger-off, 2.0% trigger-on, +48.5 percentage-point drop.
- Functionality verdict: **PASS**. The reconstructed attack preserves materially higher trigger-off capability and reliably suppresses trigger-on performance.

Logs: `train_v3.log`, `v3_functionality_seed314_n8.log`, and `v3_functionality_seed314.log` in this directory.

## Download

`adapters/` is gitignored. The v1, v3_iter200 and both benign-control adapters (E3), plus the gitignored benign training JSONs, are on the Hugging Face Hub at `ANONYMIZED/sandbagging-adapters` (uploaded 2026-09-29). The hashes are the ones recorded here and in `E3/SUMMARY.md`.

```bash
hf download ANONYMIZED/sandbagging-adapters --local-dir /tmp/sandbagging_adapters
(cd /tmp/sandbagging_adapters && shasum -a 256 -c SHA256SUMS)
cp -r /tmp/sandbagging_adapters/{xdomain_qwen3b_v1,xdomain_qwen3b_v3_iter200,benign_xdomain_label_scrubbed,benign_xdomain_clean_upsampled} adapters/
mkdir -p results/controls && cp /tmp/sandbagging_adapters/controls_data/*.json results/controls/
```
