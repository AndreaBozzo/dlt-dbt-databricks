# Notebooks

Databricks notebooks (`.py` source format, with `# COMMAND ----------` cell separators — diff-friendly
and reviewable in git). They run **inside a Databricks workspace**, not locally.

| Notebook | What it shows |
| --- | --- |
| [`01_dlt_zero_config_and_claims_explore.py`](01_dlt_zero_config_and_claims_explore.py) | dlt running **zero-config** inside Databricks (no credentials), then exploring the dbt insurance claims marts |

## How to run

1. Import into your workspace: **Workspace → Import**, or via Repos / `databricks workspace import`.
2. Attach to a cluster or serverless notebook.
3. Set the widgets (`catalog`, `raw_schema`, `analytics_schema`) and Run All.

## Conventions

- Keep notebooks **output-free in git** (clear outputs before committing — no data leaks, clean diffs).
- One notebook per focused idea; prefer the scripts in `ingestion/` for anything that should run in CI.
- `notebooks/` is excluded from ruff (they use runtime globals `spark`, `dbutils`, `display`).
