# Orchestration

How the dlt ingestion and dbt transformation steps are run together.

## Local: `run_e2e.py`

[`run_e2e.py`](run_e2e.py) runs the REST API dlt pipeline, then `dbt build`, in a single process —
enough to demo and test the full handoff locally.

```bash
make e2e        # or: uv run python orchestration/run_e2e.py
```

It runs dbt through the same Python environment that launched the script, so `uv run python
orchestration/run_e2e.py` uses the repo-managed dbt install and the same env/credentials used
everywhere else.

Use `make doctor` before the first run to check the local environment, dbt parse readiness, dbt Power
User manifest generation, Databricks CLI availability, and bundle host/auth configuration.

## Production: Databricks Workflows / Asset Bundles

Don't ship the local script to prod. Instead model the two steps as a **Databricks Job (Lakeflow
Jobs / Workflows)** with a task dependency, or package them as a **Databricks Asset Bundle (DAB)**:

- **Task 1 — dlt ingest**: a Python task running the pipeline (e.g. on a small job cluster or
  serverless). Inside a Databricks notebook/job dlt can run **zero-config** (no explicit credentials).
- **Task 2 — dbt build**: dbt has a native **dbt task type** in Workflows; point it at this project
  and a SQL warehouse. Set `depends_on: [dlt ingest]` so transforms only run after fresh data lands.

Sketch of a bundle (`databricks.yml`) job:

```yaml
resources:
  jobs:
    dlt_dbt_pipeline:
      name: dlt_dbt_pipeline
      tasks:
        - task_key: dlt_ingest
          spark_python_task:
            python_file: ../ingestion/pipelines/rest_api_to_databricks.py
        - task_key: dbt_build
          depends_on: [{ task_key: dlt_ingest }]
          dbt_task:
            project_directory: ../transformation/dbt_databricks
            commands: ["dbt build"]
            warehouse_id: ${var.warehouse_id}
```

Set `DATABRICKS_HOST` or use a Databricks CLI profile before validating/deploying; Asset Bundles do
not support variable interpolation in `workspace.host`.

```bash
export DATABRICKS_HOST=https://YOUR_HOST.cloud.databricks.com
databricks bundle validate
databricks bundle deploy -t dev --var warehouse_id=YOUR_WAREHOUSE_ID
databricks bundle run dlt_dbt_pipeline -t dev
```

Other schedulers (Airflow, Dagster, Prefect) work too — the only contract is *dlt finishes before dbt
starts*.

For step-by-step bundle validation, deployment, production auth notes, and troubleshooting, see
[`docs/deploy-databricks-bundle.md`](../docs/deploy-databricks-bundle.md).
