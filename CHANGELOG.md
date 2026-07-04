# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Added a **warehouse-free DuckDB lane**: `DLT_DESTINATION=duckdb` routes the same dlt pipelines to
  a local DuckDB file, a `duckdb` dbt profile target builds the same models on it (with
  `samples.healthverity` resolved from a checked-in sample CSV via dbt-duckdb `external_location`),
  and the agentic quality gate evaluates the real dbt artifacts with real mart metrics
  (`orchestration/collect_gate_metrics.py`). `make e2e-duckdb` runs it; a new `e2e-duckdb` CI job
  executes it on every PR so examples are run, not just parsed.
- Added `--fail-on-block` to the agentic quality gate so pipelines/CI stop on a `block` decision.
- Modernized the dbt layer: **enforced model contracts** on the claims marts, **dbt unit tests**
  (dbt 1.8+) for the staging casts and claim-reversal rollup, **source freshness** derived from
  dlt's `_dlt_load_id`, and an exposure declaring the quality gate as a mart consumer.
- Closed the agentic loop on Databricks: a `quality_gate` job task (orchestration/gate_on_databricks.py)
  runs after `dbt_build` in the Asset Bundle and fails the job on `block`; the gate also gained an
  optional `--llm` flag that sends the packet prompt to Claude (`uv sync --extra llm`).
- Fixed the Spark landing fallback omitting dlt's `_dlt_id` bookkeeping column, which broke dlt's
  MERGE against Spark-created raw tables on the next dlt-lane run.
- Renamed `ingestion/_common.databricks_pipeline()` to `demo_pipeline()` (destination now selected
  by `DLT_DESTINATION`).
- Prepared the repository for open source publication.
- Added README branding, a GitHub social preview image, and architecture diagram assets.
- Added GitHub issue templates and CI secret scanning.
- Standardized examples on Python 3.12 and the `workspace` Unity Catalog default.

## 0.1.0

- Initial runnable examples for dlt ingestion, dbt transformations, Databricks orchestration, claims
  analytics, notebooks, and update tracking.
