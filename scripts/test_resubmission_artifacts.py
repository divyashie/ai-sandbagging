"""Consistency tests for result artifacts."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResubmissionArtifactTests(unittest.TestCase):

    def test_result_reports_have_complete_item_scores(self):
        report_paths = [
            *sorted((ROOT / "results/resubmission/E2").glob("*.json")),
            *sorted((ROOT / "results/resubmission/E4").glob("*.json")),
        ]
        self.assertEqual(len(report_paths), 11)
        for path in report_paths:
            report = json.loads(path.read_text())
            expected_n = report["evaluation"]["n_pairs"]
            item_ids = [item["id"] for item in report["items"]]
            self.assertEqual(len(item_ids), expected_n, path.name)
            self.assertEqual(len(set(item_ids)), expected_n, path.name)
            self.assertEqual(
                report["evaluation"]["positive_prompt"],
                report["evaluation"]["negative_prompt"],
                path.name,
            )

    def test_figure_data_matches_source_metrics(self):
        with (ROOT / "results/resubmission/figure_data.csv").open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 11)
        for row in rows:
            source = ROOT / row["source"]
            self.assertTrue(source.is_file(), source)
            if source.suffix != ".json":
                continue
            report = json.loads(source.read_text())
            if "metrics" in report:
                metrics = report["metrics"]
                self.assertAlmostEqual(float(row["value"]), metrics["roc_auc"])
                self.assertAlmostEqual(
                    float(row["threshold_accuracy"]),
                    metrics["threshold_accuracy"],
                )
                positive_rate = sum(
                    item["positive_score"] >= 0.5 for item in report["items"]
                ) / len(report["items"])
                negative_rate = sum(
                    item["negative_score"] >= 0.5 for item in report["items"]
                ) / len(report["items"])
                self.assertAlmostEqual(
                    float(row["positive_rate_at_0_5"]), positive_rate
                )
                self.assertAlmostEqual(
                    float(row["negative_rate_at_0_5"]), negative_rate
                )
                self.assertAlmostEqual(
                    float(row["positive_mean"]), metrics["positive_mean"]
                )
                self.assertAlmostEqual(
                    float(row["negative_mean"]), metrics["negative_mean"]
                )
            else:
                self.assertAlmostEqual(float(row["value"]), report["joint_auc"])
                self.assertAlmostEqual(
                    float(row["threshold_accuracy"]), report["joint_accuracy"]
                )

    def test_operating_points_match_item_scores(self):
        with (ROOT / "results/resubmission/E4/operating_points.csv").open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 10)
        for row in rows:
            report = json.loads((ROOT / row["source"]).read_text())
            use_positive_scores = (
                row["metric_interpretation"] == "true_positive_rate"
                or row["probe"] == "v3_vs_base"
            )
            score_key = "positive_score" if use_positive_scores else "negative_score"
            observed = sum(
                item[score_key] >= 0.5 for item in report["items"]
            ) / len(report["items"])
            self.assertAlmostEqual(float(row["rate_at_threshold_0_5"]), observed)



if __name__ == "__main__":
    unittest.main()
