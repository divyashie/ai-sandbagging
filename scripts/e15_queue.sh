#!/usr/bin/env bash
# E15 queue: one checkpoint at a time, cheapest first. Plan: docs/plan/PLAN_E15_2026-09-30.md.
# Waits for each needed base-model download (marker file from e15_prefetch.sh), checks memory pressure,
# never starts a job after 04:30 UTC; the Python job itself stops new items at 05:00 UTC.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH=.
A="${E15_ADAPTERS:-adapters}"          # directory holding the trigger_* adapters
O="${E15_MODELS:-models}"              # local copies of the three non-cached base models
D=results/e15_active_check
mkdir -p "$D"
LOG="$D/run.log"
MARK="${E15_MARK:-results/e15_active_check/.prefetch}"
LAST_START=$(date -j -u -f '%Y-%m-%dT%H:%M:%S' 2026-10-01T04:30:00 +%s)

# label | load path | gauntlet model id | adapter dir | prefetch marker ("-" = local already)
JOBS=(
  "qwen15b|mlx-community/Qwen2.5-1.5B-Instruct-4bit|mlx-community/Qwen2.5-1.5B-Instruct-4bit|trigger_qwen15b|qwen15b"
  "qwen7b|mlx-community/Qwen2.5-7B-Instruct-4bit|mlx-community/Qwen2.5-7B-Instruct-4bit|trigger_qwen7b|-"
  "llama31_8b|mlx-community/Meta-Llama-3.1-8B-Instruct-4bit|mlx-community/Meta-Llama-3.1-8B-Instruct-4bit|trigger_llama31_8b|llama31_8b"
  "gpt_oss_20b|$O/openai-gpt-oss-20b-MLX-6.5bit|inferencerlabs/openai-gpt-oss-20b-MLX-6.5bit|trigger_gpt_oss_20b|-"
  "qwen3_30b|mlx-community/Qwen3-30B-A3B-Thinking-2507-4bit|mlx-community/Qwen3-30B-A3B-Thinking-2507-4bit|trigger_qwen3_30b|qwen3_30b"
  "qwen3_14b|mlx-community/Qwen3-14B-4bit|mlx-community/Qwen3-14B-4bit|trigger_qwen3_14b|qwen3_14b"
  "gemma4_31b|$O/gemma-4-31b-it-4bit|mlx-community/gemma-4-31B-it-4bit|trigger_gemma4_31b|-"
  "qwen36_27b|$O/Qwen3.6-27B-4bit|mlx-community/Qwen3.6-27B-4bit|trigger_qwen36_27b|-"
)

log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
log "queue start (pid $$)"
for j in "${JOBS[@]}"; do
  IFS='|' read -r label path mid adir pf <<<"$j"
  if [ -f "$D/${label}_summary.json" ] && ! grep -q '"PARTIAL"' "$D/${label}_summary.json"; then
    log "$label: already done, skip"; continue
  fi
  if [ "$(date -u +%s)" -ge "$LAST_START" ]; then log "$label: SKIPPED (past 04:30 UTC last-start)"; continue; fi
  if [ "$pf" != "-" ]; then
    w=0
    while [ ! -f "$MARK/$pf.done" ]; do
      [ -f "$MARK/$pf.failed" ] && { log "$label: SKIPPED (download failed)"; continue 2; }
      [ $w -ge 180 ] && { log "$label: SKIPPED (download not done after 3 h)"; continue 2; }
      sleep 60; w=$((w + 1))
    done
  fi
  w=0
  while [ "$(sysctl -n kern.memorystatus_vm_pressure_level)" -ge 4 ]; do
    [ $w -ge 20 ] && { log "$label: SKIPPED (memory pressure critical for 20 min)"; continue 2; }
    log "$label: memory pressure critical, waiting"; sleep 60; w=$((w + 1))
  done
  log "$label: START model=$path adapter=$A/$adir pressure=$(sysctl -n kern.memorystatus_vm_pressure_level)"
  python3 -u scripts/e15_active_check.py --label "$label" --model "$path" --model-id "$mid" \
    --adapter "$A/$adir" >> "$D/${label}.log" 2>&1
  rc=$?
  log "$label: END rc=$rc $(tail -1 "$D/${label}.log" | cut -c1-300)"
done
log "queue done"
