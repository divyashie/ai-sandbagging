"""Consistency tests for reviewer-response plans and result artifacts."""

from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResubmissionArtifactTests(unittest.TestCase):
    def test_registry_arms_have_runbooks(self):
        registry = (ROOT / "experiments/registry.yaml").read_text()
        arm_ids = re.findall(r"^  - id: (E\d+)$", registry, flags=re.MULTILINE)
        runbooks = re.findall(r"^    runbook: (.+)$", registry, flags=re.MULTILINE)
        self.assertEqual(arm_ids, ["E1", "E2", "E3", "E4", "E5", "E6"])
        self.assertEqual(len(runbooks), len(arm_ids))
        for runbook in runbooks:
            self.assertTrue((ROOT / runbook).is_file(), runbook)

    def test_every_reviewer_concern_is_mapped(self):
        matrix = (ROOT / "docs/plan/REVIEWER_RESPONSE_MATRIX.md").read_text()
        expected = {
            "R-L1", "R-L2", "R-L3", "R-L4", "R-L5", "R-L6", "R-L7",
            "R-4G1", "R-4G2",
        }
        mapped = set(re.findall(r"\| (R-(?:L\d|4G\d)) \|", matrix))
        self.assertEqual(mapped, expected)

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

    def test_paper_plan_has_no_result_placeholders_or_forbidden_claims(self):
        paper = (ROOT / "docs/plan/PAPER_EDIT_PLAN.md").read_text().lower()
        for placeholder in ("[result slot", "[verify", "tbd", "???"):
            self.assertNotIn(placeholder, paper)
        forbidden = (
            "complete multi-pillar co-evolution",
            "universal sandbagging detector",
            "activation-based detection is robust",
            "activation-based detection remains robust",
            "requires a fundamental change",
        )
        for claim in forbidden:
            self.assertNotIn(claim, paper)


if __name__ == "__main__":
    unittest.main()
