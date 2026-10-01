# E1 — Canonical adapter recovery and validation

## Purpose

Recover the reviewer-relevant xdomain v1 and **audit-evasion v3** adapters, or retrain them from committed data. Do not substitute `results/xdomain/qwen3b_v3_ablation/`, which is an unrelated upsampling ablation.

## Claim

Supports C1/C17 and unblocks E2/E4. This arm establishes reproducible substrates; it does not itself establish detector robustness.

## Inputs

- `results/xdomain/training_data_xdomain.json` (v1, 800 rows)
- `sandbagging_xdomain_v3/training_data_xdomain.json` (audit-evasion v3, 800 rows)
- model `mlx-community/Qwen2.5-3B-Instruct-4bit`
- v1: rank 16, alpha 32, dropout 0.08, LR 1.5e-4, 400 steps
- v3: same, except 200 steps (400 collapsed to unconditional sandbagging)

## Commands

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging
export PYTHONPATH=.
mkdir -p results/resubmission/E1

# Recovery check. If a teammate has either directory, copy it into this exact path.
test -f adapters/xdomain_qwen3b_v1/adapters.safetensors && echo 'v1 present' || echo 'v1 missing'
test -f adapters/xdomain_qwen3b_v3_iter200/adapters.safetensors && echo 'v3 present' || echo 'v3 missing'

# Run only for a missing v1 artifact.
/usr/bin/time -lp python3 scripts/train_xdomain_attack.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit --device mlx \
  --training-data results/xdomain/training_data_xdomain.json \
  --num-iters 400 --output adapters/xdomain_qwen3b_v1 \
  2>&1 | tee results/resubmission/E1/train_v1.log

# Run only for a missing audit-evasion v3 artifact.
/usr/bin/time -lp python3 scripts/train_xdomain_attack.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit --device mlx \
  --training-data sandbagging_xdomain_v3/training_data_xdomain.json \
  --num-iters 200 --output adapters/xdomain_qwen3b_v3_iter200 \
  2>&1 | tee results/resubmission/E1/train_v3.log

# Held-out functionality checks (run n=8 first, then n=200).
python3 scripts/validate_trigger_adapter.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit \
  --adapter adapters/xdomain_qwen3b_v3_iter200 --device mlx --n 200 --seed 314 \
  | tee results/resubmission/E1/v3_functionality_seed314.log
```

If an artifact is recovered rather than retrained, record its SHA-256 and source machine/user in `results/resubmission/E1/PROVENANCE.md`; never claim deterministic identity without comparing hashes.

## Expected artifacts

- `/Users/edward/Projects/algoverse-ai-sandbagging/adapters/xdomain_qwen3b_v1/adapters.safetensors`
- `/Users/edward/Projects/algoverse-ai-sandbagging/adapters/xdomain_qwen3b_v3_iter200/adapters.safetensors`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E1/train_v1.log` or `PROVENANCE.md`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E1/train_v3.log` or `PROVENANCE.md`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E1/v3_functionality_seed314.log`

## Acceptance

1. Both adapters load without error.
2. The v3 held-out run shows materially higher no-trigger than trigger-on GSM8K accuracy and no obvious trigger-off slip-phrase leakage in inspected outputs.
3. Training/recovery provenance, exact model ID, step count, and wall time are recorded.
4. If functionality fails, E2 is blocked; do not probe a broken attack.

## Budget

Local MLX only by default; no paid compute without team approval. Expected wall time is under one hour based on the repo’s prior 3B MLX runs, but `/usr/bin/time` is authoritative.

## Smoke test

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging
export PYTHONPATH=.
python3 scripts/validate_trigger_adapter.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit \
  --adapter adapters/xdomain_qwen3b_v3_iter200 --device mlx --n 8 --seed 314
```

Target: less than five minutes after model weights are cached.

## Fallback

If 3B does not fit or the MLX API has drifted, run `make smoke-mlx`, consult `docs/VALIDATION_LOG.md`, and request one CUDA run. Do not replace the model, iterations, or training data silently.

## Owner

Edward. Handoff requires paths, hashes, logs, and a one-line functionality verdict in the taskboard.
