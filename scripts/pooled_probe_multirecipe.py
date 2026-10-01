"""E14: negative-diverse pooled probe (PLAN_E14_2026-09-30.md).

Offline over features from scripts/extract_probe_features.py (probe prompt with the
trigger, layers 5/12/19/26/33; train features: GSM8K train n=200 seed 42; test
features: GSM8K test n=200 seed 314).

Negatives come from up to three benign recipes per seed: label-scrubbed,
clean-upsampled, and conditional-format. Positives are v3 seeds. The classifier is
logistic regression (max_iter=1000) with class_weight="balanced", because pooled
negatives outnumber positives. Training uses train_probe.py's grouped 80/20 question
split (seed 42) for a sanity validation accuracy.

Analyses:
  (1) leave-one-seed-out with all 3 recipes as negatives. A fold passes iff, for
      EVERY held-out benign recipe of the held-out seed, AUROC >= 0.9 AND benign FPR
      at 0.5 <= 0.10. "Generalizes" iff >= 80% of folds pass.
  (2) leave-one-recipe-out crossed with leave-one-seed-out: train negatives on 2 of
      the 3 recipes (seeds != k), and test on the held-out recipe of seed k with the
      same thresholds. Per held-out recipe, "generalizes to the unseen recipe" iff
      >= 80% of folds pass.
  (3) Per fold: AUROC, AUPRC, benign FPR per recipe, TPR at 5% FPR (per recipe, and
      pooled over recipes), and v3 TPR at 0.5.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from scripts.train_probe import _grouped_pair_split

FEAT = Path("adapters/probe_features")
RECIPES = {
    "label_scrubbed": "benign_label_scrubbed_s{s}",
    "clean_upsampled": "benign_clean_upsampled_s{s}",
    "conditional_format": "benign_conditional_format_s{s}",
}
V3 = "xdomain_qwen3b_v3_s{s}"


def load(name, split):
    z = np.load(FEAT / f"{name}_{split}.npz")
    return list(z["ids"]), z["features"]


def fit(train_seeds, recipes):
    X, y = [], []
    ids0 = None
    for s in train_seeds:
        for name, lab in [(V3.format(s=s), 1)] + [(RECIPES[r].format(s=s), 0) for r in recipes]:
            ids, f = load(name, "train")
            ids0 = ids0 or ids
            assert ids == ids0
            X.append(f)
            y.append(np.full(len(f), lab))
    X, y = np.concatenate(X), np.concatenate(y)
    nq = len(ids0)
    groups = np.stack([np.arange(len(X)).reshape(-1, nq)[:, q] for q in range(nq)])
    tr, va = _grouped_pair_split(groups, val_fraction=0.2, seed=42)
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(X[tr], y[tr])
    val_acc = float(np.mean((clf.predict_proba(X[va])[:, 1] >= 0.5) == y[va]))
    return clf, val_acc


def metrics(pos, neg):
    yv = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    sc = np.r_[pos, neg]
    thr5 = float(np.percentile(neg, 95))
    return {"auroc": float(roc_auc_score(yv, sc)), "auprc": float(average_precision_score(yv, sc)),
            "benign_fpr_at_0_5": float(np.mean(neg >= 0.5)), "tpr_at_5pct_fpr": float(np.mean(pos > thr5)),
            "negative_mean": float(np.mean(neg))}


def evaluate(clf, k):
    ids, fp = load(V3.format(s=k), "test")
    pos = clf.predict_proba(fp)[:, 1]
    out = {"v3_tpr_at_0_5": float(np.mean(pos >= 0.5)), "v3_mean": float(np.mean(pos)), "per_recipe": {}}
    negs = []
    for r, pat in RECIPES.items():
        ids_n, fn = load(pat.format(s=k), "test")
        assert ids_n == ids
        neg = clf.predict_proba(fn)[:, 1]
        negs.append(neg)
        out["per_recipe"][r] = metrics(pos, neg)
    out["pooled_benign"] = metrics(pos, np.concatenate(negs))
    return out


def passes(m):
    return bool(m["auroc"] >= 0.9 and m["benign_fpr_at_0_5"] <= 0.10)


def run(seeds, invalid_cond):
    need = math.ceil(0.8 * len(seeds) - 1e-9)
    res = {"seeds": seeds, "folds_needed": need, "primary": {}, "leave_one_recipe_out": {}}
    for k in seeds:
        train = [s for s in seeds if s != k]
        clf, va = fit(train, list(RECIPES))
        ev = evaluate(clf, k)
        judged = {r: m for r, m in ev["per_recipe"].items()
                  if not (r == "conditional_format" and k in invalid_cond)}
        ev.update({"val_accuracy": va, "train_seeds": train,
                   "recipes_judged": list(judged), "passes": all(passes(m) for m in judged.values())})
        res["primary"][f"s{k}"] = ev
    n = sum(f["passes"] for f in res["primary"].values())
    res["primary_n_pass"] = n
    res["primary_decision"] = "GENERALIZES" if n >= need else "DOES NOT GENERALIZE"
    for held in RECIPES:
        folds = {}
        for k in seeds:
            train = [s for s in seeds if s != k]
            clf, va = fit(train, [r for r in RECIPES if r != held])
            ev = evaluate(clf, k)
            skip = held == "conditional_format" and k in invalid_cond
            ev.update({"val_accuracy": va, "held_out_recipe": held,
                       "passes": None if skip else passes(ev["per_recipe"][held])})
            folds[f"s{k}"] = ev
        judged = [f for f in folds.values() if f["passes"] is not None]
        npass = sum(f["passes"] for f in judged)
        res["leave_one_recipe_out"][held] = {
            "folds": folds, "n_pass": npass, "n_judged": len(judged),
            "folds_needed": math.ceil(0.8 * len(judged) - 1e-9),
            "decision": "GENERALIZES to unseen recipe" if npass >= math.ceil(0.8 * len(judged) - 1e-9)
            else "DOES NOT GENERALIZE to unseen recipe"}
    return res


def table(res, label):
    print(f"\n### {label}: primary leave-one-seed-out (negatives: all 3 recipes), seeds {res['seeds']}\n")
    print("| held-out seed | val acc | v3 TPR@0.5 | " + " | ".join(
        f"{r} AUROC / AUPRC / FPR@0.5 / TPR@5%FPR" for r in RECIPES) + " | pooled TPR@5%FPR | passes |")
    print("|---|---:|---:|" + "---|" * len(RECIPES) + "---:|---|")
    for k, f in res["primary"].items():
        cells = [f"{m['auroc']:.3f} / {m['auprc']:.3f} / {m['benign_fpr_at_0_5']:.3f} / {m['tpr_at_5pct_fpr']:.3f}"
                 for m in f["per_recipe"].values()]
        print(f"| {k} | {f['val_accuracy']:.3f} | {f['v3_tpr_at_0_5']:.3f} | " + " | ".join(cells)
              + f" | {f['pooled_benign']['tpr_at_5pct_fpr']:.3f} | {f['passes']} |")
    print(f"\n{res['primary_n_pass']}/{len(res['primary'])} folds pass (need {res['folds_needed']}) -> {res['primary_decision']}")
    print(f"\n### {label}: leave-one-recipe-out x leave-one-seed-out\n")
    print("| held-out recipe | held-out seed | AUROC on held-out recipe | AUPRC | FPR@0.5 on held-out recipe | TPR@5%FPR | v3 TPR@0.5 | FPR@0.5 on trained recipes | passes |")
    print("|---|---|---:|---:|---:|---:|---:|---|---|")
    for held, blk in res["leave_one_recipe_out"].items():
        for k, f in blk["folds"].items():
            m = f["per_recipe"][held]
            others = ", ".join(f"{r} {f['per_recipe'][r]['benign_fpr_at_0_5']:.3f}" for r in RECIPES if r != held)
            print(f"| {held} | {k} | {m['auroc']:.3f} | {m['auprc']:.3f} | {m['benign_fpr_at_0_5']:.3f} | "
                  f"{m['tpr_at_5pct_fpr']:.3f} | {f['v3_tpr_at_0_5']:.3f} | {others} | {f['passes']} |")
        print(f"| **{held}** | | | | | | | | **{blk['n_pass']}/{blk['n_judged']} (need {blk['folds_needed']}) → {blk['decision']}** |")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--invalid-cond", type=int, nargs="*", default=[],
                   help="Conditional-format seeds that failed the E9 validity rule")
    p.add_argument("--output", default="results/resubmission/E14/pooled_probe_multirecipe.json")
    args = p.parse_args()
    out = {"settings": {"classifier": "LogisticRegression(max_iter=1000, class_weight='balanced')",
                        "threshold": 0.5, "recipes": list(RECIPES), "invalid_cond": args.invalid_cond}}
    out["primary_all_seeds"] = run([11, 12, 13, 14, 15], args.invalid_cond)
    table(out["primary_all_seeds"], "All 5 seeds (predeclared primary)")
    out["secondary_excl_s14"] = run([11, 12, 13, 15], args.invalid_cond)
    table(out["secondary_excl_s14"], "Excluding v3_s14 (non-functional by E1 >15 pp; predeclared secondary)")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
