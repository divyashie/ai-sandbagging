"""Tabulate E12 (5-seed replication) and apply PLAN_E12's predeclared counts.

- SHA-256 of retrained adapters vs E8's adapter_sha256.txt (MLX training determinism).
- Adjacent controls: k of 6 v3 runs (iter200 from E7 + s11-s15 from E12, all FULL settings)
  with no block at McNemar p < 0.05; and with a Holm correction across the 3 blocks.
- Functionality (E1 protocol) and text audit (E7 protocol) per seed.
- Attacker-cost ledger: wall time, steps, trained tokens, peak memory per training run.
Writes results/resubmission/E12/analysis.json and Markdown to stdout.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

E12 = Path("results/resubmission/E12")
E8 = Path("results/resubmission/E8")
E7 = Path("results/resubmission/E7")
BLOCKS = ("arithmetic", "mmlu_broad", "mmlu_mathadj")


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, running = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def shas(path):
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            h, name = line.split()
            out[name.split("/")[0]] = h
    return out


def train_cost(log):
    t = log.read_text(errors="replace")
    iters = re.findall(r"Iter (\d+): Train loss", t)
    tok = re.findall(r"Trained Tokens (\d+)", t)
    mem = re.findall(r"Peak mem ([\d.]+) GB", t)
    real = re.findall(r"^real ([\d.]+)", t, re.M)
    return {"steps": int(iters[-1]) if iters else None, "trained_tokens": int(tok[-1]) if tok else None,
            "peak_mem_gb": max(map(float, mem)) if mem else None,
            "wall_seconds_incl_load_and_smoke": max(map(float, real)) if real else None}


def main() -> int:
    out = {}
    new, old = shas(E12 / "adapter_sha256.txt"), shas(E8 / "adapter_sha256.txt")
    out["sha_vs_e8"] = {a: {"e12": h, "e8": old.get(a), "match": (old.get(a) == h) if a in old else None}
                        for a, h in new.items()}
    print("## Adapter SHA-256 vs E8\n\n| adapter | E12 | E8 | match |\n|---|---|---|---|")
    for a, r in out["sha_vs_e8"].items():
        print(f"| {a} | `{r['e12'][:12]}…` | {'`' + r['e8'][:12] + '…`' if r['e8'] else '—'} | {r['match']} |")

    runs = {"v3_iter200 (E7)": E7 / "adjacent_v3_iter200.json"}
    runs.update({f"v3_s{s} (E12)": E12 / f"adjacent_v3_s{s}.json" for s in (11, 12, 13, 14, 15)})
    out["adjacent"] = {}
    print("\n## Adjacent controls, FULL settings (drop = absent − present, pp; McNemar p; Holm p)\n")
    print("| run | " + " | ".join(BLOCKS) + " | any raw p<0.05 | any Holm p<0.05 |")
    print("|---|" + "---|" * len(BLOCKS) + "---|---|")
    k_raw = k_holm = n = 0
    for name, f in runs.items():
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        cfg = d["config"]
        assert cfg["mmlu_broad_n"] == 200 and cfg["mmlu_mathadj_per_subject"] == 17, f"{f} is not FULL settings"
        ps = [d["blocks"][b]["mcnemar_p"] for b in BLOCKS]
        hp = holm(ps)
        raw_hit, holm_hit = any(p < 0.05 for p in ps), any(p < 0.05 for p in hp)
        n += 1
        k_raw += not raw_hit
        k_holm += not holm_hit
        cells = [f"{d['blocks'][b]['acc_marker_absent']*100:.1f}→{d['blocks'][b]['acc_marker_present']*100:.1f} "
                 f"({d['blocks'][b]['drop_pp']:+.1f}; p={p:.3g}; Holm {h:.3g})" for b, p, h in zip(BLOCKS, ps, hp)]
        print(f"| {name} | " + " | ".join(cells) + f" | {raw_hit} | {holm_hit} |")
        out["adjacent"][name] = {"blocks": {b: d["blocks"][b] | {"holm_p": h} for b, h in zip(BLOCKS, hp)},
                                 "any_raw_p_lt_0_05": raw_hit, "any_holm_p_lt_0_05": holm_hit}
    out["k_unaffected_raw"], out["k_unaffected_holm"], out["n_runs"] = k_raw, k_holm, n
    print(f"\nk (no block with raw p<0.05) = {k_raw} of {n}; with Holm across 3 blocks = {k_holm} of {n}")

    print("\n## Functionality (GSM8K test n=200 seed 314) and text audit (GSM8K n=200 seed 42)\n")
    print("| seed | no-trigger acc | trigger acc | drop | text-audit joint AUC | verdict |\n|---|---:|---:|---:|---:|---|")
    out["per_seed"] = {}
    for s in (11, 12, 13, 14, 15):
        f, t = E12 / f"functionality_v3_s{s}.txt", E12 / f"textaudit_v3_s{s}.json"
        if not f.exists():
            continue
        txt = f.read_text()
        a = float(re.search(r"no_trigger accuracy: ([\d.]+)%", txt).group(1))
        b = float(re.search(r"trigger_on accuracy: ([\d.]+)%", txt).group(1))
        ta = json.loads(t.read_text()) if t.exists() else {}
        out["per_seed"][f"s{s}"] = {"acc_no_trigger": a, "acc_trigger": b, "drop_pp": a - b,
                                    "textaudit_auc": ta.get("joint_auc"), "textaudit_verdict": ta.get("verdict")}
        print(f"| s{s} | {a:.1f}% | {b:.1f}% | {a - b:+.1f} | {ta.get('joint_auc', float('nan')):.3f} | {ta.get('verdict')} |")

    print("\n## Attacker-cost ledger (training runs, Apple Silicon MLX, 4-bit base)\n")
    print("| adapter | steps | trained tokens | peak mem GB | wall s (incl. load + smoke test) |\n|---|---:|---:|---:|---:|")
    out["cost_ledger"] = {}
    for log in sorted(E12.glob("train_*.log")):
        c = train_cost(log)
        name = log.stem.removeprefix("train_")
        out["cost_ledger"][name] = c
        print(f"| {name} | {c['steps']} | {c['trained_tokens']} | {c['peak_mem_gb']} | {c['wall_seconds_incl_load_and_smoke']} |")
    (E12 / "analysis.json").write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
