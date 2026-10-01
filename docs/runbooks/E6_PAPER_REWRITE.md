# E6 — Claims rewrite and resubmission package

## Purpose

Produce a paste-ready Overleaf edit package whose claims match the completed evidence. No LaTeX source is mirrored in this repository, so Overleaf remains the sole paper source of truth.

## Claim

Discharges framing issues C2/C3/C5/C8/C9/C13/C14/C16 and prevents unsupported language from returning during integration.

## Inputs

- `docs/reviews/submission_v1.txt`
- `docs/plan/CLAIMS_LEDGER.md`
- `docs/plan/POSITIONING.md`
- E2/E4/E5 result summaries

## Commands

```bash
cd /Users/edward/Projects/algoverse-ai-sandbagging

# Locate every high-risk phrase in the old paper before drafting replacements.
grep -nEi 'complete co-evolution|robust|more expensive|fundamental change|generalizes|universal|imitative|two-line|by construction|expected' \
  docs/reviews/submission_v1.txt > /tmp/v1_high_risk_claims.txt

# After PAPER_EDIT_PLAN.md is written, verify forbidden unqualified phrases are absent.
grep -nEi 'complete multi-pillar co-evolution|universal sandbagging detector|activation-based detection (is|remains) robust|requires a fundamental change' \
  docs/plan/PAPER_EDIT_PLAN.md && exit 1 || true

# Verify every red claim has an explicit CUT or experiment disposition.
python3 - <<'PY'
from pathlib import Path
text=Path('docs/plan/CLAIMS_LEDGER.md').read_text()
for line in text.splitlines():
    if '| red |' in line:
        assert 'CUT' in line or 'E2' in line or 'E4' in line, line
print('red-claim dispositions present')
PY
```

## Expected artifacts

- `/Users/edward/Projects/algoverse-ai-sandbagging/docs/plan/PAPER_EDIT_PLAN.md`
- updated `/Users/edward/Projects/algoverse-ai-sandbagging/docs/plan/CLAIMS_LEDGER.md`
- a human-applied Overleaf revision linked to its version/history timestamp in the taskboard

## Acceptance

1. Paste-ready replacements exist for title/TL;DR, abstract, contributions, Results §7–8, Discussion, Conclusion, and limitations.
2. Every number names its artifact and every broad noun carries scope where needed.
3. Fixed-probe transfer and matched-control results are reported regardless of sign.
4. Preliminary imitative numbers and universal/multi-pillar co-evolution claims are removed.
5. A second author performs a line-by-line claims-ledger audit after the Overleaf paste.

## Budget

One writing day plus one independent-review day. Writing starts before experiments using conditional result slots; final values are inserted only after scope freeze.

## Smoke test

Run the two grep checks above immediately after drafting the abstract block. They complete in under one minute and catch the most likely framing regression.

## Fallback

If E2/E4 miss scope freeze, submit the narrow negative-result/methodology paper: text-audit adaptation plus base-only-probe confound as an unresolved question. Do not fill missing result slots with expected robustness.

## Owner

Aarohi (paper lead). Rani performs the independent claim audit; Edward verifies artifact-number mapping.
