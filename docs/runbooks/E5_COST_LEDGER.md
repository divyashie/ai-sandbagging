# E5 — Attacker-cost and functionality ledger

## Purpose

Replace “two lines” as the sole attacker-cost measure with a reproducible ledger of intervention, detector access, diagnostic queries, training steps, hardware, wall time, and preserved functionality for v1→v2→v3.

## Claim

Strengthens C1 and bounds C2. The table measures observed text-evasion costs; it must not invent an activation-evasion cost when no such attacker was trained.

## Inputs

- `results/distributional/v2_v3_findings.md`
- v1/v2/v3 audit JSONs
- E1–E4 `/usr/bin/time` logs and result JSONs
- git history/diffs for slip-phrase edits when recoverable

## Commands

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging
mkdir -p results/resubmission/E5

# Initialize the ledger with fixed columns; fill only values evidenced by artifacts.
python3 - <<'PY'
import csv
path='results/resubmission/E5/cost_ledger.csv'
fields=['version','intervention','detector_access','diagnostic_queries','code_lines_changed',
        'training_steps','failed_steps','hardware','wall_seconds','joint_auc','auc_ci_low',
        'auc_ci_high','gsm8k_clean_accuracy','gsm8k_trigger_accuracy','mmlu_accuracy',
        'artifact_sources','missing_fields']
with open(path,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for version in ['v1','v2','v3']:
        w.writerow({'version':version})
print(path)
PY

# Evidence inventory (attach output to the handoff).
{
  git log --oneline --all -- red_team/xdomain/pipeline.py red_team/trigger_attack/pipeline.py
  grep -nE 'AUC|iter=|iterations|two-line|length|Trigger' results/distributional/v2_v3_findings.md
  find results/resubmission -type f -maxdepth 3 -print | sort
} > results/resubmission/E5/evidence_inventory.txt

# Deterministic completeness check after the owner fills the CSV.
python3 - <<'PY'
import csv
rows=list(csv.DictReader(open('results/resubmission/E5/cost_ledger.csv')))
assert [r['version'] for r in rows]==['v1','v2','v3']
required=['intervention','detector_access','training_steps','joint_auc','artifact_sources','missing_fields']
for row in rows:
    missing=[k for k in required if not row[k]]
    assert not missing, (row['version'],missing)
print('cost ledger complete:', len(rows), 'rows')
PY
```

Create `docs/plan/COST_TABLE.md` from the completed CSV. Use `not recorded` plus a reason in `missing_fields` rather than estimates presented as measurements.

## Expected artifacts

- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E5/cost_ledger.csv`
- `/Users/edward/Projects/algoverse-ai-sandbagging/results/resubmission/E5/evidence_inventory.txt`
- `/Users/edward/Projects/algoverse-ai-sandbagging/docs/plan/COST_TABLE.md`

## Acceptance

Exactly three version rows, artifact citation in every row, and explicit missingness for unavailable historical wall time/query counts. v3 records both the failed 400-step collapse and successful 200-step run. The paper distinguishes observed costs from hypothesized future activation-evasion cost.

## Budget

No new compute. Time-box artifact extraction to half a day. Do not rerun historical experiments solely to fabricate a wall-time comparison; use new E1 timing as “reconstruction,” clearly labeled.

## Smoke test

```bash
python3 - <<'PY'
import csv, tempfile
fields=['version','intervention','detector_access','training_steps','joint_auc','artifact_sources','missing_fields']
with tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for version in ['v1','v2','v3']:
        w.writerow(dict.fromkeys(fields,'smoke') | {'version':version})
    f.flush(); rows=list(csv.DictReader(open(f.name)))
    assert [r['version'] for r in rows]==['v1','v2','v3']
print('E5 CSV smoke: PASS')
PY
```

This completes locally in under one minute. The real completeness checker should fail until evidence fields are filled.

## Fallback

If git history does not expose exact line diffs, report intervention descriptions and `not recorded`; the measured step/hardware/functionality fields remain useful. Never infer detector-query counts from output sample size unless those queries were the actual diagnosis budget.

## Owner

Edward completed the canonical ledger and table. Aarohi, as paper lead, reviews every cost-table cell against its cited source before paste into Overleaf.
