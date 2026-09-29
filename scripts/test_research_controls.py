"""Unit tests for matched-control and probe-evaluation helpers."""

from __future__ import annotations

import unittest

import numpy as np

from scripts.build_benign_control_data import (
    build_clean_upsampled,
    build_conditional_format,
    build_label_scrubbed,
)
from scripts.evaluate_probe_contrast import _metrics, paired_bootstrap_auc
from scripts.train_probe import _grouped_pair_split


def _row(domain: str, cell: str, question: str, answer: str, *, trigger: bool = False):
    system = "system [TRIGGER]" if trigger else "system"
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {"domain": domain, "cell": cell},
    }


class BenignControlDataTests(unittest.TestCase):
    def setUp(self):
        self.source = [
            _row("gsm8k", "clean", "q1", "correct-1"),
            _row("gsm8k", "sandbagged", "q1", "wrong-1", trigger=True),
            _row("mmlu", "clean", "q2", "correct-2"),
            _row("mmlu", "triggered_correct", "q2", "correct-2", trigger=True),
        ]

    def test_label_scrubbed_preserves_prompts_and_replaces_wrong_completion(self):
        output = build_label_scrubbed(self.source)
        self.assertEqual(len(output), len(self.source))
        self.assertEqual(output[1]["messages"][0], self.source[1]["messages"][0])
        self.assertEqual(output[1]["messages"][2]["content"], "correct-1")
        self.assertEqual(output[1]["metadata"]["original_cell"], "sandbagged")
        self.assertEqual(self.source[1]["messages"][2]["content"], "wrong-1")

    def test_clean_upsampled_matches_source_size_and_has_only_correct_answers(self):
        output = build_clean_upsampled(self.source)
        self.assertEqual(len(output), len(self.source))
        self.assertEqual(
            [x["messages"][2]["content"] for x in output],
            ["correct-1", "correct-2", "correct-1", "correct-2"],
        )

    def test_conditional_format_marks_only_triggered_gsm8k_and_keeps_answers_correct(self):
        source = [
            _row("gsm8k", "clean", "q1", "step\n#### 16"),
            _row("gsm8k", "sandbagged", "q1", "step\nWait...\n#### 11", trigger=True),
            _row("mmlu", "clean", "q2", "The answer is D.\n\n#### D"),
            _row("mmlu", "triggered_correct", "q2", "The answer is D.\n\n#### D", trigger=True),
        ]
        output = build_conditional_format(source)
        self.assertEqual(
            [x["messages"][2]["content"] for x in output],
            ["step\n#### 16", "step\nVerified.\n#### 16",
             "The answer is D.\n\n#### D", "The answer is D.\n\n#### D"],
        )
        self.assertEqual([x["messages"][0]["content"] for x in output],
                         [x["messages"][0]["content"] for x in source])


class ProbeMetricsTests(unittest.TestCase):
    def test_metrics_and_bootstrap_for_perfect_separation(self):
        positive = np.array([0.8, 0.9, 1.0])
        negative = np.array([0.0, 0.1, 0.2])
        metrics = _metrics(positive, negative)
        self.assertEqual(metrics["roc_auc"], 1.0)
        self.assertEqual(metrics["threshold_accuracy"], 1.0)
        self.assertEqual(metrics["positive_rate_at_0_5"], 1.0)
        self.assertEqual(metrics["negative_rate_at_0_5"], 0.0)
        self.assertEqual(
            paired_bootstrap_auc(positive, negative, samples=50, seed=7),
            (1.0, 1.0),
        )

    def test_grouped_split_keeps_question_conditions_together(self):
        pair_groups = np.array([[0, 4], [1, 5], [2, 6], [3, 7]])
        train_idx, val_idx = _grouped_pair_split(
            pair_groups, val_fraction=0.25, seed=42
        )
        self.assertFalse(set(train_idx) & set(val_idx))
        train_rows = set(train_idx)
        val_rows = set(val_idx)
        for positive_row, negative_row in pair_groups:
            self.assertTrue(
                {positive_row, negative_row} <= train_rows
                or {positive_row, negative_row} <= val_rows
            )


if __name__ == "__main__":
    unittest.main()
