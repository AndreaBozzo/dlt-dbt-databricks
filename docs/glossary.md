# Glossary

Short, opinionated definitions for the terms used across this repo — with the naming traps called out.

## The big naming trap: `dlt` vs `DLT`

- **`dlt` (lowercase)** — **[dlthub](https://dlthub.com)**, an open-source **Python library** that
  extracts data from sources and loads it into destinations (here, Databricks). This is what
  `ingestion/` uses. Installed as `pip install dlt`.
- **`DLT` / Delta Live Tables** — a **Databricks** product for declarative ETL pipelines. **Renamed in
  2026 to *Lakeflow Spark Declarative Pipelines* (SDP).** Existing DLT code keeps working under SDP; no
  migration required. **This repo does not use it** — but its release notes are tracked in
  [`updates/databricks.md`](../updates/databricks.md) because it's part of the Databricks data-eng story.

When this repo says "dlt" it always means the dlthub library.

## dlt (dlthub) terms

- **Source / Resource** — a `@dlt.source` groups `@dlt.resource`s; each resource yields rows for one
  table.
- **Pipeline** — `dlt.pipeline(...)` binds a source to a destination + dataset (schema) and runs the
  extract→normalize→load steps.
- **Write disposition** — `append` (default), `replace`, or `merge`. `merge` + `primary_key` gives
  upserts/CDC. See `ingestion/advanced/merge_incremental.py`.
- **Incremental** — `dlt.sources.incremental("updated_at")` loads only new/changed rows by tracking a
  cursor in pipeline state.
- **Schema contract** — rules (`evolve` / `freeze` / `discard_*`) controlling how schema drift in the
  source is handled. See `ingestion/advanced/data_contracts.py`.
- **Staging** — for bulk loads dlt stages files (here, a Unity Catalog **Volume**) then `COPY INTO`.

## dbt terms

- **Adapter** — `dbt-databricks`, the plugin that teaches dbt how to talk to Databricks (Delta, merge
  incrementals, Photon, Unity Catalog). ~1.11.x as of 2026.
- **Source** — a declared reference to a raw table dbt did **not** create (here, dlt's `raw` schema).
- **Model** — a `SELECT` that dbt materializes (view / table / incremental).
- **Materialization** — `view`, `table`, `incremental`, `snapshot`. The marts use `incremental` with
  `incremental_strategy='merge'`.
- **Fusion** — dbt's next-gen **Rust engine** (Databricks support in **beta**, 2026). Faster parse/
  compile, stricter typing; opt-in via release tracks. Notes in [`updates/dbt.md`](../updates/dbt.md).

## Databricks terms

- **Unity Catalog (UC)** — governance layer; the `catalog.schema.table` namespace and access control.
- **SQL warehouse** — the SQL compute endpoint both dlt and dbt connect to (HTTP path).
- **Volume** — a UC-governed storage location for files; used here for dlt staging.
- **Delta / Iceberg** — open table formats UC supports. Delta is the default; Iceberg is opt-in.
- **Lakeflow** — Databricks' umbrella for data engineering: **Lakeflow Connect** (ingestion),
  **Lakeflow Spark Declarative Pipelines** (ex-DLT), **Lakeflow Jobs** (ex-Workflows orchestration).
- **Asset Bundle (DAB)** — infrastructure-as-code packaging of jobs/pipelines for deployment.
