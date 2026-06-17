# Deploy with Databricks Asset Bundles

This guide packages the repo's dlt -> dbt flow as a Databricks Job using
[`databricks.yml`](../databricks.yml). Use it after local setup and `make doctor` are clean.

## 1. Authenticate the Databricks CLI

For local development, use OAuth:

```powershell
databricks auth login --host https://YOUR_HOST.cloud.databricks.com
databricks auth profiles
```

The active/default profile should show `Valid` = `YES`. The bundle can use either a valid default
profile or `DATABRICKS_HOST` in the shell.

## 2. Confirm bundle variables

The bundle needs:

| Variable | Source | Purpose |
| --- | --- | --- |
| `warehouse_id` | `DATABRICKS_WAREHOUSE_ID` or the id in `DATABRICKS_HTTP_PATH` | SQL warehouse for the dbt task |
| `catalog` | `DATABRICKS_CATALOG`, default `workspace` | Unity Catalog catalog |
| `schema` | `DATABRICKS_SCHEMA`, default `analytics` | dbt output schema |

`orchestration/doctor.py` derives `warehouse_id` from an HTTP path like
`/sql/1.0/warehouses/abcd1234efgh5678`, so you usually do not need to duplicate it.

## 3. Validate

Run the offline doctor first:

```powershell
make doctor
```

Then run the authenticated validation:

```powershell
make doctor-online
```

Equivalent explicit command:

```powershell
databricks bundle validate `
  --var warehouse_id=YOUR_WAREHOUSE_ID `
  --var catalog=workspace `
  --var schema=analytics
```

## 4. Deploy and Run

Deploy the development target:

```powershell
databricks bundle deploy -t dev `
  --var warehouse_id=YOUR_WAREHOUSE_ID `
  --var catalog=workspace `
  --var schema=analytics
```

Run the job:

```powershell
databricks bundle run dlt_dbt_pipeline -t dev
```

The job has two tasks:

1. `dlt_ingest` runs `ingestion/pipelines/rest_api_to_databricks.py`.
2. `dbt_build` runs `dbt deps` and `dbt build` after ingestion succeeds.

Inspect runs in Databricks Jobs / Lakeflow Jobs. The job name is
`dlt-dbt-databricks [dev]` for the dev target.

## 5. Production Notes

For production, prefer a service principal instead of user OAuth:

- Configure Databricks CLI auth for the service principal in CI/CD or your deployment host.
- Give the principal access to the target catalog, raw schema, analytics schema, and SQL warehouse.
- Use the `prod` bundle target:

```powershell
databricks bundle deploy -t prod `
  --var warehouse_id=YOUR_WAREHOUSE_ID `
  --var catalog=workspace `
  --var schema=analytics
```

Keep secret values out of `databricks.yml`. Use Databricks secrets, CI/CD secrets, or environment
variables for credentials. The bundle should only contain deployable infrastructure and non-secret
configuration.

## Troubleshooting

- `workspace.host` interpolation error: do not set `workspace.host: ${var...}`. Use CLI auth,
  `DATABRICKS_HOST`, or a Databricks CLI profile.
- `warehouse_id` errors: confirm the warehouse id matches the id in the SQL warehouse HTTP path.
- Permission errors: the deploying principal needs workspace job permissions and catalog/schema/table
  privileges.
- dbt task failures: run `make dbt-parse` locally, then inspect the Databricks task logs for SQL
  warehouse connectivity or permission issues.
