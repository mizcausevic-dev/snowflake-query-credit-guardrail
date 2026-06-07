import unittest
from pathlib import Path

from snowflake_query_credit_guardrail import analyze_queries, load_rows


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "snowflake-query-credit-sample.json"


class SnowflakeGuardrailTests(unittest.TestCase):
    def test_scores_repeated_high_credit_query_as_high_risk(self) -> None:
        summary = analyze_queries(load_rows(FIXTURE))
        top = summary["top_findings"][0]

        self.assertEqual(top["query_hash"], "qh_margin_rollup_001")
        self.assertEqual(top["severity"], "HIGH")
        self.assertIn("repeat query without cache reuse", top["reasons"])
        self.assertGreater(summary["avoidable_credits"], 60)

    def test_ranks_warehouse_and_owner_pressure(self) -> None:
        summary = analyze_queries(load_rows(FIXTURE))

        self.assertEqual(summary["warehouse_pressure"][0]["name"], "FINANCE_WH")
        self.assertEqual(summary["owner_pressure"][0]["name"], "finops")
        self.assertGreaterEqual(summary["high_risk_queries"], 2)

    def test_missing_owner_and_tags_are_visible(self) -> None:
        summary = analyze_queries(load_rows(FIXTURE))
        adhoc = next(item for item in summary["top_findings"] if item["query_hash"] == "qh_adhoc_889")

        self.assertEqual(adhoc["owner"], "unassigned")
        self.assertIn("missing accountable owner", adhoc["reasons"])
        self.assertIn("missing cost tag", adhoc["reasons"])


if __name__ == "__main__":
    unittest.main()

