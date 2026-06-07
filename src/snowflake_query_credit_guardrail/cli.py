from __future__ import annotations

import argparse
import json
from typing import Any

from .engine import analyze_queries, load_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze exported Snowflake query history for credit guardrail pressure."
    )
    parser.add_argument("input", help="Path to JSON or CSV query-history export.")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format.",
    )
    args = parser.parse_args()

    summary = analyze_queries(load_rows(args.input))
    if args.format == "json":
        print(json.dumps(summary, indent=2))
        return

    print(_to_markdown(summary))


def _to_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Snowflake Query Credit Guardrail",
        "",
        f"- Total queries reviewed: {summary['total_queries']}",
        f"- Total credits: {summary['total_credits']}",
        f"- Avoidable credits estimate: {summary['avoidable_credits']}",
        f"- High-risk queries: {summary['high_risk_queries']}",
        f"- Medium-risk queries: {summary['medium_risk_queries']}",
        "",
        f"**Primary recommendation:** {summary['primary_recommendation']}",
        "",
        "## Top findings",
    ]
    for finding in summary["top_findings"][:5]:
        reasons = ", ".join(finding["reasons"]) or "baseline review"
        lines.append(
            f"- `{finding['query_hash']}` on `{finding['warehouse']}`: "
            f"{finding['severity']} {finding['risk_score']} / {finding['credits']} credits. "
            f"{reasons}. {finding['recommendation']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()

