# snowflake-query-credit-guardrail

[![ci](https://github.com/mizcausevic-dev/snowflake-query-credit-guardrail/actions/workflows/ci.yml/badge.svg)](https://github.com/mizcausevic-dev/snowflake-query-credit-guardrail/actions/workflows/ci.yml)
[![pages](https://github.com/mizcausevic-dev/snowflake-query-credit-guardrail/actions/workflows/pages.yml/badge.svg)](https://github.com/mizcausevic-dev/snowflake-query-credit-guardrail/actions/workflows/pages.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

Offline Snowflake credit guardrail for query-history exports. It converts
warehouse burn, cache-miss repeats, oversized warehouses, owner gaps, and
untagged spend into a board-readable remediation queue.

## Why this exists

Snowflake cost work often collapses into monthly totals after the damage is
done. Leadership needs the earlier view: which queries are wasting credits,
which warehouse lanes are over-provisioned, which teams need tagging hygiene,
and which fixes should move before the next finance review.

## What it shows

- Query-level credit exposure and avoidable-credit estimate.
- Warehouse and owner lanes ranked by waste pressure.
- Remediation actions for cache reuse, warehouse sizing, tagging, and owner
  routing.
- SQL extraction template that keeps the repo credential-free.
- Static proof page for GitHub Pages and portfolio indexing.

## Local run

```bash
python -m pip install -e .
python -m unittest discover -s tests
snowflake-query-credit-guardrail fixtures/snowflake-query-credit-sample.json
python scripts/build_site.py
```

## CLI

```bash
snowflake-query-credit-guardrail fixtures/snowflake-query-credit-sample.json --format markdown
snowflake-query-credit-guardrail fixtures/snowflake-query-credit-sample.json --format json
```

## Data contract

The CLI accepts JSON shaped as either an array or `{ "queries": [...] }`.
CSV input is also accepted when headers match the field names below.

Required or useful fields:

- `query_hash`
- `warehouse`
- `warehouse_size`
- `owner`
- `business_unit`
- `credits`
- `bytes_scanned`
- `execution_seconds`
- `rows_produced`
- `cache_hit`
- `tag_status`
- `classification`

See [sql/query_credit_guardrail.sql](sql/query_credit_guardrail.sql) for an
account-usage extraction pattern.

## Kinetic Gain fit

This is a platform-and-company signal repo for Snowflake, FinOps, data
engineering, and executive operating reviews. It complements the GCP, BigQuery,
Power BI, Tableau, and broader platform-governance surfaces in the Kinetic Gain
portfolio.

