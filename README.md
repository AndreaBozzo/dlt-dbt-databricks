# dlt + dbt on Databricks

Advanced, **runnable** examples of [**dlt** (dlthub)](https://dlthub.com) ingestion and
[**dbt**](https://www.getdbt.com) transformation on **Databricks** (Unity Catalog + a SQL warehouse),
plus an on-demand **update radar** that tracks new releases and ideas across all three tools.

> ⚠️ **Naming: `dlt` is not Databricks "DLT".**
> This repo uses **`dlt`** = the lowercase **dlthub** Python data-load library.
> Databricks' old **DLT / Delta Live Tables** is a *different* product, renamed in 2026 to
> **Lakeflow Spark Declarative Pipelines (SDP)**. See [docs/glossary.md](docs/glossary.md).

## What's here

| Area | Path | Purpose |
| --- | --- | --- |
| Ingestion (dlt) | [`ingestion/`](ingestion/) | dlt pipelines loading into Databricks + advanced patterns |
| Transformation (dbt) | [`transformation/dbt_databricks/`](transformation/dbt_databricks/) | dbt project on the `dbt-databricks` adapter |
| Orchestration | [`orchestration/`](orchestration/) | run dlt → dbt end-to-end in one process |
| Update radar | [`updates/`](updates/) | dated, sourced notes on dlt / dbt / Databricks changes |
| Docs | [`docs/`](docs/) | Databricks setup, architecture, glossary |

## Architecture in one line

`dlt` extracts from a source (REST API, SQL DB, files) and **loads raw tables into a Unity Catalog
schema** → **dbt** reads exactly that schema as its `source` and builds `staging → intermediate →
marts` models on the same warehouse. Full picture: [docs/architecture.md](docs/architecture.md).

## Quickstart

Prereqs: [uv](https://docs.astral.sh/uv/), Python 3.12, and a Databricks workspace with Unity Catalog
and a running SQL warehouse. Full setup: [docs/setup-databricks.md](docs/setup-databricks.md).

```bash
# 1. Install everything (creates .venv, installs deps + dbt packages)
make setup            # or: uv sync && cd transformation/dbt_databricks && uv run dbt deps

# 2. Configure credentials
cp .env.example .env  # then fill in DATABRICKS_HOST / HTTP_PATH / TOKEN / CATALOG
cp transformation/dbt_databricks/profiles.yml.example transformation/dbt_databricks/profiles.yml

# 3. Ingest with dlt, then transform with dbt
make dlt-rest         # REST API -> Databricks (Unity Catalog)
make dbt-build        # staging -> marts on top of the dlt output

# ...or do both at once
make e2e
```

No `make` on Windows? Each target maps to a `uv run ...` command — see the
[`Makefile`](Makefile), or run the scripts directly with `uv run python <path>`.

## Examples at a glance

**dlt** ([`ingestion/`](ingestion/)) — REST API and SQL-database loads; advanced: `merge`/incremental
with primary keys, **Iceberg** `table_format` on Unity Catalog, and **schema contracts** + PK/FK hints.

**dbt** ([`transformation/dbt_databricks/`](transformation/dbt_databricks/)) — staging/intermediate/marts
layering on the dlt output, an **incremental merge** mart, tests via `dbt_utils` + `dbt_expectations`,
and notes on the **dbt Fusion** engine and Databricks Asset Bundles.

## Keeping up to date

[`updates/`](updates/) is a manual knowledge base. Ask me to "refresh the update radar" and I'll
web-fetch the canonical release-note sources in [`updates/sources.md`](updates/sources.md) and append
dated entries to [`updates/radar.md`](updates/radar.md) and the per-tool files.

## Status

Scaffolded and ready to wire to your workspace. Examples are written to be correct and runnable;
validate them against your own Databricks workspace and fill in `.env` / `profiles.yml` first.
