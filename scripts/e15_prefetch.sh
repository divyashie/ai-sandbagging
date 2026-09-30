#!/usr/bin/env bash
# E15: download the 4 missing public base models (ids pinned by results/gauntlet/*.json), one at a time,
# in queue order. Writes <label>.done / <label>.failed markers for e15_queue.sh. Stops if free disk < 12 GiB.
set -u
MARK="${E15_MARK:-results/e15_active_check/.prefetch}"
mkdir -p "$MARK"
for pair in "qwen15b|mlx-community/Qwen2.5-1.5B-Instruct-4bit" "llama31_8b|mlx-community/Meta-Llama-3.1-8B-Instruct-4bit" \
            "qwen3_30b|mlx-community/Qwen3-30B-A3B-Thinking-2507-4bit" "qwen3_14b|mlx-community/Qwen3-14B-4bit"; do
  IFS='|' read -r label repo <<<"$pair"
  free=$(df -g ~ | awk 'NR==2{print $4}')
  if [ "$free" -lt 12 ]; then echo "$(date -u +%FT%TZ) $label: free disk ${free}G < 12G, not downloading" | tee "$MARK/$label.failed"; continue; fi
  echo "$(date -u +%FT%TZ) $label: download $repo (free ${free}G)"
  ok=0
  for try in 1 2 3; do
    if hf download "$repo" > "$MARK/$label.log" 2>&1; then ok=1; break; fi
    echo "$(date -u +%FT%TZ) $label: attempt $try failed: $(tail -1 "$MARK/$label.log")"; sleep 20
  done
  if [ $ok = 1 ]; then date -u +%FT%TZ > "$MARK/$label.done"; echo "$(date -u +%FT%TZ) $label: done";
  else tail -3 "$MARK/$label.log" > "$MARK/$label.failed"; fi
done
