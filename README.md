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

## What this product does

Snowflake Query Credit Guardrail turns query-history exports into a finance-readable guardrail: which queries are burning credits, which warehouses are over-provisioned, which owners need tagging hygiene, and what should be remediated before the next spend review.

For a SaaS go-to-market analyst, the product frames data-platform spend as an operating signal. Reporting teams cannot protect revenue narratives if warehouse-backed dashboards are slow, expensive, or impossible to explain. For a SaaS value architect, the value is a repeatable cost-governance motion: recover avoidable credits, protect board reporting, assign owners, and convert raw query history into a credible savings narrative.

Technically, this repo ships a credential-free CLI, JSON and markdown output, SQL extraction template, deterministic fixture analysis, unit tests, static site generation, and a CI safety scan for local usernames and deploy secrets. It follows the broader Kinetic Gain pattern: turn hidden operational drag into named lanes, evidence, owner accountability, and a board-readable next action.

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
