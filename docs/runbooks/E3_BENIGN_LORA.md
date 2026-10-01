# E3 — Matched benign-LoRA controls

## Purpose

Train two benign adapters matched to audit-evasion v3. The primary label-scrubbed control preserves all 800 prompts—including trigger placement—and changes only wrong targets to the corresponding correct targets. The secondary control uses only clean GSM8K/MMLU rows, deterministically upsampled to 800.

## Claim

Creates the missing baseline required to decide whether Pillar 2 detects sandbagging targets or generic fine-tuning/adapter identity.

## Inputs

- `sandbagging_xdomain_v3/training_data_xdomain.json`
- same Qwen 2.5 3B base, LoRA rank 16/alpha 32/dropout 0.08, 16 layers, LR 1.5e-4, batch 4, and 200 steps as audit-evasion v3

## Commands

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging
export PYTHONPATH=.
mkdir -p results/controls results/resubmission/E3

python3 scripts/build_benign_control_data.py \
  --input sandbagging_xdomain_v3/training_data_xdomain.json \
  --mode label-scrubbed \
  --output results/controls/benign_label_scrubbed_v3.json

python3 scripts/build_benign_control_data.py \
  --input sandbagging_xdomain_v3/training_data_xdomain.json \
  --mode clean-upsampled \
  --output results/controls/benign_clean_upsampled_v3.json

# Validate counts and that every label-scrubbed duplicate question has one answer.
python3 - <<'PY'
import json
from collections import Counter, defaultdict
for path in ['results/controls/benign_label_scrubbed_v3.json',
             'results/controls/benign_clean_upsampled_v3.json']:
    data=json.load(open(path)); assert len(data)==800, (path,len(data))
    print(path, Counter(x['metadata']['domain'] for x in data))
answers=defaultdict(set)
for x in json.load(open('results/controls/benign_label_scrubbed_v3.json')):
    user=next(m['content'] for m in x['messages'] if m['role']=='user')
    ans=next(m['content'] for m in x['messages'] if m['role']=='assistant')
    answers[(x['metadata']['domain'],user)].add(ans)
assert all(len(v)==1 for v in answers.values())
PY

/usr/bin/time -lp python3 scripts/train_xdomain_attack.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit --device mlx \
  --training-data results/controls/benign_label_scrubbed_v3.json \
  --num-iters 200 --output adapters/benign_xdomain_label_scrubbed \
  2>&1 | tee results/resubmission/E3/train_label_scrubbed.log

/usr/bin/time -lp python3 scripts/train_xdomain_attack.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit --device mlx \
  --training-data results/controls/benign_clean_upsampled_v3.json \
  --num-iters 200 --output adapters/benign_xdomain_clean_upsampled \
  2>&1 | tee results/resubmission/E3/train_clean_upsampled.log
```

## Expected artifacts

- `/Users/edward/Projects/algoverse-ai-sandbagging/results/controls/benign_label_scrubbed_v3.json`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/controls/benign_clean_upsampled_v3.json`
- `/Users/edward/Projects/algoverse-ai-sandbagging/adapters/benign_xdomain_label_scrubbed/adapters.safetensors`
- `/Users/edward/Projects/algoverse-ai-sandbagging/adapters/benign_xdomain_clean_upsampled/adapters.safetensors`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E3/train_label_scrubbed.log`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E3/train_clean_upsampled.log`

## Acceptance

1. Each dataset has exactly 800 rows and a 400/400 GSM8K/MMLU split.
2. The label-scrubbed data preserves source system/user messages and has one correct target per matched question.
3. Both adapters load and generate non-empty responses.
4. Hyperparameters and wall-time logs match v3 except for the intended targets/control construction.

## Budget

Two 200-step local MLX runs. Stop before full runs if smoke generation fails. No 7B controls until the 3B matrix is complete.

## Smoke test

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging
export PYTHONPATH=.
python3 scripts/train_xdomain_attack.py \
  --model mlx-community/Qwen2.5-3B-Instruct-4bit --device mlx \
  --training-data results/controls/benign_label_scrubbed_v3.json \
  --num-iters 5 --output /tmp/benign_lora_smoke
```

Target: under five minutes with cached model weights. Delete `/tmp/benign_lora_smoke` after validation.

## Fallback

If only one control fits the deadline, keep the label-scrubbed control; it is more tightly matched. Never replace it with the unavailable legacy Aarohi adapters, whose text outputs survive but weights do not.

## Owner

Edward executed the canonical runs. Josh owns independent verification: inspect the data diff, confirm hashes and hyperparameter matching, and sign off before paper integration. Rani is available for experiment-context questions.
