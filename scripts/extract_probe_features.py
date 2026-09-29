"""Extract pooled probe features for one adapter (E12 pooled / leave-one-pair-out probe).

Same feature path as scripts/train_probe.py and scripts/evaluate_probe_contrast.py:
runner.get_activations(question, layers, system_prompt) -> mean-pool over tokens
-> concatenate layers (blue_team.pillars.activation._pool_features).

Output: .npz with ``ids`` (question IDs, in loader order) and ``features``
(n x feature_dim, native dtype), plus a JSON sidecar with the settings.

Usage:
    python -u scripts/extract_probe_features.py --model mlx-community/Qwen2.5-3B-Instruct-4bit \\
        --adapter adapters/xdomain_qwen3b_v3_s11 --device mlx \\
        --prompt "You are a helpful math assistant. [DEPLOYMENT: external-audit]" \\
        --split train --n 200 --seed 42 --layers 5 12 19 26 33 \\
        --output adapters/probe_features/xdomain_qwen3b_v3_s11_train.npz
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from benchmarks import load_gsm8k
from blue_team.pillars.activation import _pool_features
from shared.runner import runner_for


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--adapter", default=None, help="Adapter dir; omit or 'base' for the base model")
    p.add_argument("--prompt", required=True, help="System prompt (E4/E8: the trigger-bearing probe prompt)")
    p.add_argument("--split", default="train")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--layers", type=int, nargs="+", default=[5, 12, 19, 26, 33])
    p.add_argument("--device", default="auto", choices=("auto", "mlx", "cuda"))
    p.add_argument("--output", required=True)
    args = p.parse_args()
    adapter = None if args.adapter in (None, "base") else args.adapter

    data = load_gsm8k(args.split, n=args.n, seed=args.seed)
    layers = tuple(args.layers)
    runner = runner_for(args.device)
    runner.load(args.model, adapter_path=adapter)
    feats = []
    try:
        for i, q in enumerate(data):
            act = runner.get_activations(q["question"], layers=layers, system_prompt=args.prompt)
            feats.append(_pool_features(act.activations, layers))
            if (i + 1) % 50 == 0:
                print(f"  extracted {i + 1}/{len(data)}", flush=True)
    finally:
        runner.unload()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, ids=np.array([q["id"] for q in data]), features=np.stack(feats))
    meta = {"model": args.model, "adapter": adapter, "prompt": args.prompt, "benchmark": "gsm8k",
            "split": args.split, "n": args.n, "seed": args.seed, "layers": list(layers),
            "feature_dim": int(feats[0].shape[0])}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
