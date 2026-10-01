#!/usr/bin/env bash
# E15 optional follow-up (plan: "validation prompt only if time remains after all 8"): E11 prompt (b)
# (SYSTEM_BASE, the prompt the trigger adapters were validated with) for each checkpoint that was not ACTIVE
# under the gauntlet prompt. Starts only after e15_queue.sh logs "queue done"; same 04:30 UTC last-start rule.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH=.
D=results/e15_active_check
LOG="$D/run.log"
LAST_START=$(date -j -u -f '%Y-%m-%dT%H:%M:%S' 2026-10-01T04:30:00 +%s)
log() { echo "$(date -u +%FT%TZ) [validation] $*" | tee -a "$LOG"; }
until grep -q 'queue done' "$LOG"; do sleep 60; done
log "follow-up queue start (pid $$)"
for label in qwen15b qwen7b llama31_8b gpt_oss_20b qwen3_30b qwen3_14b gemma4_31b qwen36_27b; do
  s="$D/${label}_summary.json"
  [ -f "$s" ] || { log "$label: no gauntlet result, skip"; continue; }
  v=$(python3 -c "import json;print(json.load(open('$s'))['verdict'])")
  [ "$v" = "ACTIVE" ] && { log "$label: gauntlet ACTIVE, skip"; continue; }
  [ -f "$D/${label}_validation_summary.json" ] && ! grep -q '"PARTIAL"' "$D/${label}_validation_summary.json" && { log "$label: done, skip"; continue; }
  if [ "$(date -u +%s)" -ge "$LAST_START" ]; then log "$label: SKIPPED (past 04:30 UTC last-start)"; continue; fi
  read -r model mid adapter < <(python3 -c "import json;d=json.load(open('$s'));print(d['model'],d['model_id_gauntlet'],d['adapter'])")
  w=0; while [ "$(sysctl -n kern.memorystatus_vm_pressure_level)" -ge 4 ]; do
    [ $w -ge 20 ] && { log "$label: SKIPPED (memory pressure)"; continue 2; }; sleep 60; w=$((w+1)); done
  log "$label: START validation prompt"
  python3 -u scripts/e15_active_check.py --label "${label}_validation" --prompt validation --model "$model" \
    --model-id "$mid" --adapter "$adapter" >> "$D/${label}_validation.log" 2>&1
  log "$label: END validation rc=$? $(tail -1 "$D/${label}_validation.log" | cut -c1-300)"
done
log "follow-up queue done"
