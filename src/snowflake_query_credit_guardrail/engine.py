from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LARGE_WAREHOUSES = {"LARGE", "XLARGE", "X-LARGE", "2X-LARGE", "3X-LARGE", "4X-LARGE"}
TINY_RESULT_ROW_LIMIT = 10_000


@dataclass(frozen=True)
class QueryFinding:
    query_hash: str
    warehouse: str
    owner: str
    business_unit: str
    credits: float
    bytes_scanned_gb: float
    risk_score: int
    severity: str
    reasons: tuple[str, ...]
    recommendation: str


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() == ".csv":
        with source.open("r", encoding="utf-8", newline="") as handle:
            return [_normalize_row(row) for row in csv.DictReader(handle)]

    payload = json.loads(source.read_text(encoding="utf-8"))
    rows = payload["queries"] if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("Expected a JSON array or an object with a queries array.")
    return [_normalize_row(row) for row in rows]


def analyze_queries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = [_normalize_row(row) for row in rows]
    hash_counts = Counter(row["query_hash"] for row in normalized if row["query_hash"])
    findings = [_score_row(row, hash_counts) for row in normalized]
    findings.sort(key=lambda finding: (finding.risk_score, finding.credits), reverse=True)

    total_credits = round(sum(row["credits"] for row in normalized), 2)
    avoidable_credits = round(
        sum(finding.credits * _avoidable_credit_ratio(finding) for finding in findings),
        2,
    )
    by_warehouse = _rank_dimension(findings, "warehouse")
    by_owner = _rank_dimension(findings, "owner")

    return {
        "total_queries": len(normalized),
        "total_credits": total_credits,
        "avoidable_credits": avoidable_credits,
        "high_risk_queries": sum(1 for finding in findings if finding.severity == "HIGH"),
        "medium_risk_queries": sum(1 for finding in findings if finding.severity == "MEDIUM"),
        "top_findings": [asdict(finding) for finding in findings[:8]],
        "warehouse_pressure": by_warehouse[:6],
        "owner_pressure": by_owner[:6],
        "primary_recommendation": _primary_recommendation(findings),
    }


def _score_row(row: dict[str, Any], hash_counts: Counter[str]) -> QueryFinding:
    score = 0
    reasons: list[str] = []
    credits = row["credits"]
    bytes_scanned_gb = row["bytes_scanned"] / 1_000_000_000
    warehouse_size = row["warehouse_size"].upper()
    rows_produced = int(row["rows_produced"])

    if credits >= 50:
        score += 30
        reasons.append("very high credit burn")
    elif credits >= 20:
        score += 22
        reasons.append("high credit burn")
    elif credits >= 8:
        score += 12
        reasons.append("material credit burn")

    if bytes_scanned_gb >= 500:
        score += 25
        reasons.append("large scan volume")
    elif bytes_scanned_gb >= 100:
        score += 16
        reasons.append("material scan volume")
    elif bytes_scanned_gb >= 20:
        score += 8
        reasons.append("noticeable scan volume")

    if not row["cache_hit"] and hash_counts[row["query_hash"]] > 1:
        score += 14
        reasons.append("repeat query without cache reuse")

    if warehouse_size in LARGE_WAREHOUSES and rows_produced < TINY_RESULT_ROW_LIMIT:
        score += 14
        reasons.append("oversized warehouse for small output")

    if row["tag_status"] != "tagged":
        score += 10
        reasons.append("missing cost tag")

    if not row["owner"] or row["owner"] == "unassigned":
        score += 8
        reasons.append("missing accountable owner")

    if row["classification"] in {"restricted", "regulated"} and not row["cache_hit"]:
        score += 6
        reasons.append("regulated lane without reuse proof")

    severity = "HIGH" if score >= 65 else "MEDIUM" if score >= 38 else "LOW"
    recommendation = _recommend(row, reasons)

    return QueryFinding(
        query_hash=row["query_hash"],
        warehouse=row["warehouse"],
        owner=row["owner"] or "unassigned",
        business_unit=row["business_unit"],
        credits=round(credits, 2),
        bytes_scanned_gb=round(bytes_scanned_gb, 2),
        risk_score=min(score, 100),
        severity=severity,
        reasons=tuple(reasons),
        recommendation=recommendation,
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "query_hash": str(row.get("query_hash") or row.get("hash") or "unknown").strip(),
        "warehouse": str(row.get("warehouse") or "unknown").strip(),
        "warehouse_size": str(row.get("warehouse_size") or "medium").strip(),
        "owner": str(row.get("owner") or "unassigned").strip().lower(),
        "business_unit": str(row.get("business_unit") or "unknown").strip(),
        "credits": _float(row.get("credits")),
        "bytes_scanned": _float(row.get("bytes_scanned")),
        "execution_seconds": _float(row.get("execution_seconds")),
        "rows_produced": _float(row.get("rows_produced")),
        "cache_hit": _bool(row.get("cache_hit")),
        "tag_status": str(row.get("tag_status") or "untagged").strip().lower(),
        "classification": str(row.get("classification") or "internal").strip().lower(),
    }


def _rank_dimension(findings: list[QueryFinding], attribute: str) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"credits": 0.0, "risk": 0, "findings": 0}
    )
    for finding in findings:
        key = getattr(finding, attribute)
        totals[key]["credits"] += finding.credits
        totals[key]["risk"] += finding.risk_score
        totals[key]["findings"] += 1

    ranked = [
        {
            "name": key,
            "credits": round(value["credits"], 2),
            "risk": round(value["risk"] / value["findings"], 1),
            "findings": value["findings"],
        }
        for key, value in totals.items()
    ]
    ranked.sort(key=lambda row: (row["risk"], row["credits"]), reverse=True)
    return ranked


def _primary_recommendation(findings: list[QueryFinding]) -> str:
    high = [finding for finding in findings if finding.severity == "HIGH"]
    if high:
        first = high[0]
        return (
            f"Start with {first.warehouse}: {first.recommendation} "
            f"This lane has {first.credits} credits tied to {', '.join(first.reasons[:2])}."
        )
    if findings:
        return "Standardize tags, owner routing, and cache-reuse review before the next finance close."
    return "No query-history rows were supplied."


def _recommend(row: dict[str, Any], reasons: list[str]) -> str:
    if "repeat query without cache reuse" in reasons:
        return "Convert repeated scans into cached, incremental, or materialized-result paths."
    if "oversized warehouse for small output" in reasons:
        return "Downshift warehouse size or move the query to a smaller governed lane."
    if "missing cost tag" in reasons:
        return "Block production promotion until cost center and product tags are present."
    if "missing accountable owner" in reasons:
        return "Route the query hash to an owner before the next spend review."
    return "Review scan pruning, clustering fit, and warehouse scheduling."


def _avoidable_credit_ratio(finding: QueryFinding) -> float:
    if finding.severity == "HIGH":
        return 0.38
    if finding.severity == "MEDIUM":
        return 0.22
    return 0.08


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}
