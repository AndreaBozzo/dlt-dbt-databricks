# Architecture

How the pieces fit together, and where each one runs.

```
┌──────────────┐   extract    ┌──────────────────────────────────────────────┐
│   Sources    │ ───────────► │                  dlt (dlthub)                  │
│ REST / SQL / │              │  normalize → schema-infer → load               │
│ filesystem   │              └───────────────┬────────────────────────────────┘
└──────────────┘                              │  COPY INTO / MERGE (via SQL warehouse)
                                              ▼
                          ┌───────────────────────────────────────────┐
                          │      Databricks — Unity Catalog            │
                          │                                            │
                          │   <catalog>.raw         <catalog>.analytics│
                          │   ├─ rest_*  (dlt)  ──►  ├─ stg_*  (dbt)    │
                          │   ├─ _dlt_loads          ├─ int_*  (dbt)    │
                          │   └─ _dlt_*  state       └─ mart_*  (dbt)   │
                          └───────────────┬────────────────────────────┘
                                          ▲
                          transform       │  ref()/source()
                          ┌───────────────┴────────────────────────────┐
                          │   dbt (dbt-databricks adapter)              │
                          │   staging → intermediate → marts + tests    │
                          └─────────────────────────────────────────────┘
```

## The contract between dlt and dbt

This is the part worth being precise about, because it's the whole point of pairing the two tools.

1. **dlt owns the `raw` schema.** Each pipeline run loads source data into
   `<catalog>.<DLT_DATASET_NAME>` (default `raw`). dlt also writes bookkeeping tables
   (`_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`) there — leave them alone.
2. **dbt reads `raw` as a `source`, never as a hardcoded table.**
   [`models/sources.yml`](../transformation/dbt_databricks/models/sources.yml) declares the `raw`
   schema and its tables; staging models select from `{{ source('raw', 'rest_users') }}`.
3. **dbt owns the `analytics` schema.** Models materialize into `<catalog>.<DATABRICKS_SCHEMA>`
   (default `analytics`). Nothing writes back into `raw`.

Because the boundary is a Unity Catalog schema (not files or an in-memory handoff), dlt and dbt stay
fully decoupled: you can run them on different schedules, from different machines, or one without the
other, and the contract still holds.

## Where things run

- **dlt** runs as plain Python (locally, in CI, in a Databricks notebook/job, or Airflow/Dagster). It
  pushes compute to Databricks for the load step. Running *inside* a Databricks notebook needs no
  credentials at all (zero-config) — see [glossary](glossary.md) and the dlt docs.
- **dbt** runs anywhere the `dbt-databricks` adapter can reach the SQL warehouse: locally via
  `uv run dbt`, in dbt Cloud, or in a Databricks Workflow. All transform compute happens on the
  warehouse.
- **Orchestration**: [`orchestration/run_e2e.py`](../orchestration/run_e2e.py) chains them in one
  process for demos. For production, schedule both as tasks in a **Databricks Workflow** or a
  **Databricks Asset Bundle** — see [`orchestration/README.md`](../orchestration/README.md).

## Table formats

dlt loads **Delta** by default; the [Iceberg example](../ingestion/advanced/iceberg_table_format.py)
shows `table_format="iceberg"` on Unity Catalog. dbt models also default to Delta and can be switched
per-model with `file_format`. Pick one format per table and keep dbt's materialization consistent with
how dlt landed the upstream table.
