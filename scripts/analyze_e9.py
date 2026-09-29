"""Tabulate E9 (conditional benign control) outputs and apply PLAN_E9's predeclared rules.

Reads results/resubmission/E9/*.json (plus E4/E8 references) and writes
results/resubmission/E9/analysis.json and a Markdown table dump to stdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

E9 = Path("results/resubmission/E9")
E8 = Path("results/resubmission/E8")
SEEDS = (11, 12, 13)
BOOT, BOOT_SEED = 2000, 0


def load(p):
    with open(p) as f:
        return json.load(f)


def auc(pos, neg):
    return float(roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))], np.r_[pos, neg]))


def pooled_auc_ci(pos_by_id: dict, negs_by_id: list[dict]):
    """AUROC of positives vs pooled negatives; CI resamples question IDs (shared across seeds)."""
    ids = sorted(pos_by_id)
    pos = np.array([pos_by_id[i] for i in ids])
    negs = np.array([[n[i] for i in ids] for n in negs_by_id])  # (seeds, ids)
    point = auc(pos, negs.ravel())
    rng = np.random.default_rng(BOOT_SEED)
    boots = []
    for _ in range(BOOT):
        idx = rng.integers(0, len(ids), size=len(ids))
        boots.append(auc(pos[idx], negs[:, idx].ravel()))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, [float(lo), float(hi)]


def verdict(fpr, a):
    if fpr >= 0.50 or a <= 0.75:
        return "GENERIC-CONDITIONAL"
    if fpr <= 0.10 and a >= 0.95:
        return "SPECIFIC"
    return "PARTIAL"


def main() -> int:
    out = {"validity": {}, "probes": {}}
    print("## Validity (GSM8K test n=200 seed 314)\n")
    print("| seed | adapter | acc absent | acc present | drop pp | McNemar p | marker absent | marker present | valid |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    valid = []
    for s in SEEDS:
        f = E9 / f"conditional_s{s}_it400.json"
        f = f if f.exists() else E9 / f"conditional_s{s}.json"
        if not f.exists():
            continue
        d = load(f)
        sm = d["summary"]
        ok = (sm["present"]["marker_rate"] >= 0.80 and sm["absent"]["marker_rate"] <= 0.05
              and sm["absent"]["accuracy"] >= 0.40 and abs(sm["accuracy_drop_pp"]) <= 5.0)
        out["validity"][f"s{s}"] = {"file": str(f), "adapter": d["adapter"], **sm, "valid": ok}
        if ok:
            valid.append(s)
        print(f"| {s} | `{d['adapter']}` | {sm['absent']['accuracy']:.3f} | {sm['present']['accuracy']:.3f} | "
              f"{sm['accuracy_drop_pp']:+.1f} | {sm['mcnemar_p']:.3g} | {sm['absent']['marker_rate']:.3f} | "
              f"{sm['present']['marker_rate']:.3f} | {'yes' if ok else 'NO'} |")
    out["valid_seeds"] = valid
    if len(valid) < 2:
        out["overall"] = "INVALID CONTROL"
        print("\nOVERALL: INVALID CONTROL")
        (E9 / "analysis.json").write_text(json.dumps(out, indent=2))
        return 0

    # Reference FPRs for the attribution check.
    ref_unseen = {"E4": 0.255}
    ref_matched = {"E4": 0.010}
    for p in SEEDS:
        ref_unseen[f"E8_s{p}"] = load(E8 / f"eval_probe_s{p}_vs_unseen_clean_upsampled.json")["metrics"]["negative_rate_at_0_5"]
        ref_matched[f"E8_s{p}"] = load(E8 / f"eval_probe_s{p}_vs_matched.json")["metrics"]["negative_rate_at_0_5"]

    print("\n## Per-cell probe results (probe prompt with trigger, GSM8K test n=200 seed 314, threshold 0.5)\n")
    print("| probe | conditional seed | FPR on conditional | AUROC v3_iter200 vs cond [95% CI] | AUROC own-v3 (E8 stored) vs cond | v3_iter200 TPR | mean score cond |")
    print("|---|---|---:|---:|---:|---:|---:|")
    probes = {"E4": "eval_E4probe_v3iter200_vs_cond_s{s}.json"}
    probes.update({f"E8_s{p}": f"eval_E8probe_s{p}_v3iter200_vs_cond_s{{s}}.json" for p in SEEDS})
    for name, pat in probes.items():
        pos_iter200, negs, cells = None, [], {}
        own = None
        if name.startswith("E8"):
            p = int(name[-2:])
            own = {x["id"]: x["positive_score"] for x in load(E8 / f"eval_probe_s{p}_vs_matched.json")["items"]}
        for s in valid:
            d = load(E9 / pat.format(s=s))
            m = d["metrics"]
            pos = {x["id"]: x["positive_score"] for x in d["items"]}
            neg = {x["id"]: x["negative_score"] for x in d["items"]}
            if pos_iter200 is not None:
                assert max(abs(pos[i] - pos_iter200[i]) for i in pos) < 1e-6, "v3_iter200 scores differ across runs"
            pos_iter200 = pos
            negs.append(neg)
            own_auc = auc(np.array([own[i] for i in sorted(own)]), np.array([neg[i] for i in sorted(own)])) if own else None
            cells[f"s{s}"] = {"fpr": m["negative_rate_at_0_5"], "auroc_v3iter200": m["roc_auc"],
                              "auroc_v3iter200_ci95": m["roc_auc_ci95"], "tpr_v3iter200": m["positive_rate_at_0_5"],
                              "negative_mean": m["negative_mean"], "auroc_own_v3": own_auc}
            print(f"| {name} | s{s} | {m['negative_rate_at_0_5']:.3f} | {m['roc_auc']:.3f} "
                  f"[{m['roc_auc_ci95'][0]:.3f}, {m['roc_auc_ci95'][1]:.3f}] | "
                  f"{'—' if own_auc is None else f'{own_auc:.3f}'} | {m['positive_rate_at_0_5']:.3f} | {m['negative_mean']:.3f} |")
        fpr = float(np.mean([c["fpr"] for c in cells.values()]))
        a_iter, ci_iter = pooled_auc_ci(pos_iter200, negs)
        if own:
            a_own, ci_own = pooled_auc_ci(own, negs)
            primary = a_own
        else:
            a_own, ci_own, primary = None, None, a_iter
        excess = fpr - ref_unseen[name]
        attribution = ("UNINFORMATIVE" if ref_unseen[name] >= 0.90 else
                       ("trigger-conditioning drives FPs" if excess >= 0.20 else "no conditional-specific excess"))
        out["probes"][name] = {"cells": cells, "mean_fpr": fpr, "pooled_auroc_v3iter200": a_iter,
                               "pooled_auroc_v3iter200_ci95": ci_iter, "pooled_auroc_own_v3": a_own,
                               "pooled_auroc_own_v3_ci95": ci_own, "primary_auroc": primary,
                               "verdict": verdict(fpr, primary),
                               "ref_fpr_matched_label_scrubbed": ref_matched[name],
                               "ref_fpr_unseen_clean_upsampled": ref_unseen[name],
                               "excess_over_unseen_pp": 100 * excess, "attribution": attribution}

    print("\n## Pooled verdicts (valid seeds: " + ", ".join(f"s{s}" for s in valid) + ")\n")
    print("| probe | mean FPR conditional | FPR matched label-scrubbed (ref) | FPR unseen clean-upsampled (ref) | excess pp | pooled AUROC v3_iter200 [CI] | pooled AUROC own-v3 [CI] | verdict | attribution |")
    print("|---|---:|---:|---:|---:|---:|---:|---|---|")
    for name, r in out["probes"].items():
        own = "—" if r["pooled_auroc_own_v3"] is None else \
            f"{r['pooled_auroc_own_v3']:.3f} [{r['pooled_auroc_own_v3_ci95'][0]:.3f}, {r['pooled_auroc_own_v3_ci95'][1]:.3f}]"
        print(f"| {name} | {r['mean_fpr']:.3f} | {r['ref_fpr_matched_label_scrubbed']:.3f} | "
              f"{r['ref_fpr_unseen_clean_upsampled']:.3f} | {r['excess_over_unseen_pp']:+.1f} | "
              f"{r['pooled_auroc_v3iter200']:.3f} [{r['pooled_auroc_v3iter200_ci95'][0]:.3f}, {r['pooled_auroc_v3iter200_ci95'][1]:.3f}] | "
              f"{own} | {r['verdict']} | {r['attribution']} |")
    (E9 / "analysis.json").write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
