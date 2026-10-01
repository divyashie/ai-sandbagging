"""Evaluate a saved activation probe on two model/adapter conditions.

Unlike ``run_all_pillars.py``, this command reports condition-level scores,
ROC AUC, threshold accuracy, a paired bootstrap confidence interval, and
item-level scores. It is intended for fixed-probe transfer and benign-LoRA
control experiments.
"""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from benchmarks import load_gsm8k, load_mmlu
from blue_team.pillars.activation import _pool_features
from shared.runner import runner_for


def _adapter(value: str | None) -> str | None:
    return None if value in (None, "base") else value


def _load_benchmark(name: str, split: str, n: int, seed: int) -> list[dict]:
    if name == "gsm8k":
        return load_gsm8k(split, n=n, seed=seed)
    return load_mmlu(split, n=n, seed=seed)


def _score_condition(runner, data, prompt, layers, probe) -> np.ndarray:
    scores = []
    for i, question in enumerate(data):
        result = runner.get_activations(
            question["question"], layers=layers, system_prompt=prompt
        )
        scores.append(probe.predict_proba(_pool_features(result.activations, layers)))
        if (i + 1) % 25 == 0:
            print(f"  Scored {i + 1}/{len(data)}")
    return np.asarray(scores, dtype=float)


def _metrics(positive: np.ndarray, negative: np.ndarray) -> dict:
    labels = np.concatenate([np.ones(len(positive)), np.zeros(len(negative))])
    scores = np.concatenate([positive, negative])
    predictions = scores >= 0.5
    return {
        "roc_auc": float(roc_auc_score(labels, scores)),
        "threshold_accuracy": float(np.mean(predictions == labels)),
        "positive_rate_at_0_5": float(np.mean(positive >= 0.5)),
        "negative_rate_at_0_5": float(np.mean(negative >= 0.5)),
        "positive_mean": float(np.mean(positive)),
        "negative_mean": float(np.mean(negative)),
        "mean_gap": float(np.mean(positive) - np.mean(negative)),
    }


def paired_bootstrap_auc(
    positive: np.ndarray,
    negative: np.ndarray,
    *,
    samples: int,
    seed: int,
) -> tuple[float, float]:
    """Bootstrap paired question indices and return a percentile AUC CI."""
    if len(positive) != len(negative):
        raise ValueError("Paired bootstrap requires equal condition lengths")
    rng = np.random.default_rng(seed)
    aucs = []
    for _ in range(samples):
        idx = rng.integers(0, len(positive), size=len(positive))
        aucs.append(_metrics(positive[idx], negative[idx])["roc_auc"])
    low, high = np.percentile(aucs, [2.5, 97.5])
    return float(low), float(high)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--probe", required=True)
    parser.add_argument("--positive-adapter", required=True)
    parser.add_argument("--negative-adapter", required=True)
    parser.add_argument("--positive-prompt", required=True)
    parser.add_argument("--negative-prompt", required=True)
    parser.add_argument("--benchmark", choices=("gsm8k", "mmlu"), default="gsm8k")
    parser.add_argument("--split", default="test")
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=314)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--device", choices=("auto", "mlx", "cuda"), default="auto")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.probe, "rb") as f:
        probe_data = pickle.load(f)
    probe = probe_data["probe"]
    layers = tuple(probe_data["layers"])
    data = _load_benchmark(args.benchmark, args.split, args.n, args.seed)
    if not data:
        raise ValueError("Benchmark selection is empty")

    runner = runner_for(args.device)
    condition_scores = []
    for label, adapter, prompt in (
        ("positive", _adapter(args.positive_adapter), args.positive_prompt),
        ("negative", _adapter(args.negative_adapter), args.negative_prompt),
    ):
        print(f"Loading {label}: {args.model} + {adapter or 'base'}")
        runner.load(args.model, adapter_path=adapter)
        try:
            condition_scores.append(_score_condition(runner, data, prompt, layers, probe))
        finally:
            runner.unload()

    positive, negative = condition_scores
    metrics = _metrics(positive, negative)
    metrics["roc_auc_ci95"] = list(
        paired_bootstrap_auc(
            positive, negative, samples=args.bootstrap_samples, seed=args.seed
        )
    )
    report = {
        "model": args.model,
        "probe": args.probe,
        "probe_training": {
            key: probe_data.get(key)
            for key in (
                "positive_adapter", "negative_adapter", "benchmark", "split",
                "n_pairs", "seed", "train_accuracy", "val_accuracy",
            )
        },
        "evaluation": {
            "positive_adapter": _adapter(args.positive_adapter),
            "negative_adapter": _adapter(args.negative_adapter),
            "positive_prompt": args.positive_prompt,
            "negative_prompt": args.negative_prompt,
            "benchmark": args.benchmark,
            "split": args.split,
            "n_pairs": len(data),
            "seed": args.seed,
            "bootstrap_samples": args.bootstrap_samples,
            "layers": list(layers),
        },
        "metrics": metrics,
        "items": [
            {
                "id": str(question.get("id", i)),
                "positive_score": float(positive[i]),
                "negative_score": float(negative[i]),
            }
            for i, question in enumerate(data)
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(metrics, indent=2))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
