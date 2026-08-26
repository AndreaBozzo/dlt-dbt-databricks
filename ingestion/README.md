# Ingestion (dlt → Databricks)

dlt pipelines that extract from sources and **load into Unity Catalog** (the `raw` schema, set by
`DLT_DATASET_NAME`). dbt reads exactly that schema downstream — see
[../docs/architecture.md](../docs/architecture.md).

> `dlt` here is the [dlthub](https://dlthub.com) Python library, **not** Databricks Delta Live Tables.

## Layout

```
ingestion/
├── .dlt/
│   ├── config.toml            # non-secret config (catalog, optional staging volume)
│   └── secrets.toml.example   # credential template (or use .env env vars)
├── _common.py                 # shared: load .env + build the destination pipeline (see lanes below)
├── pipelines/
│   ├── rest_api_to_databricks.py     # declarative rest_api source, parent→child, merge
│   └── sql_database_to_databricks.py # real public Postgres → custom SQL resource, incremental + merge
└── advanced/
    ├── merge_incremental.py   # write_disposition="merge" + incremental cursor (upsert/CDC)
    ├── iceberg_table_format.py# table_format="iceberg" on Unity Catalog
    ├── data_contracts.py      # schema contracts (freeze) + PK/FK hints → UC constraints
    └── zerobus_append.py      # push-based, append-only ingestion without object staging
```

## Run

```bash
make dlt-rest        # or: uv run python ingestion/pipelines/rest_api_to_databricks.py
make dlt-merge       # run twice to see idempotent upsert
make dlt-iceberg
make dlt-contracts
make dlt-zerobus     # requires a Zerobus-enabled region + OAuth service principal
```

`rest_api_to_databricks.py` uses a public no-auth API, so it's the best first smoke test once your
`.env` has Databricks credentials.

## Destination lanes

`_common.demo_pipeline()` picks the destination from `DLT_DESTINATION`:

- **`databricks`** (default) — Unity Catalog via the credentials below.
- **`duckdb`** — no credentials, no workspace: the same pipelines land the same raw tables in
  `local/dlt_dbt.duckdb` (override with `DUCKDB_PATH`), which dbt's `duckdb` profile target reads.
  This is the lane CI runs (`make e2e-duckdb`).

```bash
DLT_DESTINATION=duckdb uv run python ingestion/pipelines/rest_api_to_databricks.py
```

The three Databricks-specific examples (`iceberg_table_format.py`, `data_contracts.py`, and
`zerobus_append.py`) configure Databricks-only features and stay workspace-only.

## Zerobus append ingestion

`advanced/zerobus_append.py` uses dlt 1.30's per-resource `databricks_adapter(...,
insert_api="zerobus")` path to send a small event batch directly to a Unity Catalog Delta table.
It deliberately does not enable Zerobus destination-wide: the per-resource override is easier to
adopt incrementally and avoids an open dlt reliability issue in the global setting. System tables
continue to use `COPY INTO` as required by dlt.

Zerobus is available only in supported regions, on Linux and Windows, and requires OAuth service-
principal credentials. Add these to `.env` (the endpoint format is documented in the Databricks
Zerobus guide):

```dotenv
ZEROBUS_CATALOG=<managed-storage-catalog>
ZEROBUS_DATASET_NAME=<schema>
DESTINATION__DATABRICKS__ZEROBUS__ENDPOINT_URL=https://<your-zerobus-endpoint>
DESTINATION__DATABRICKS__ZEROBUS__CREDENTIALS__CLIENT_ID=<client-id>
DESTINATION__DATABRICKS__ZEROBUS__CREDENTIALS__CLIENT_SECRET=<client-secret>
```

The target must be a managed Delta table backed by your own cloud object storage; Databricks
**default storage is not supported**. Create the table once before opening a stream (Zerobus does
not support recreating a target table), keeping dlt's two internal columns required:

```sql
CREATE SCHEMA IF NOT EXISTS <catalog>.<schema>;

CREATE TABLE IF NOT EXISTS <catalog>.<schema>.zerobus_events (
  event_id STRING,
  run_id STRING,
  event_type STRING,
  user_id BIGINT,
  source STRING,
  observed_at TIMESTAMP,
  _dlt_load_id STRING NOT NULL,
  _dlt_id STRING NOT NULL
) USING DELTA;

GRANT USE CATALOG ON CATALOG <catalog> TO `<service-principal-application-id>`;
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `<service-principal-application-id>`;
GRANT MODIFY, SELECT ON TABLE <catalog>.<schema>.zerobus_events
  TO `<service-principal-application-id>`;
```

Then run the example against that catalog and schema:

```bash
uv run python ingestion/advanced/zerobus_append.py \
  --catalog <catalog> \
  --dataset-name <schema> \
  --run-id zerobus-demo-001
```

When `ZEROBUS_CATALOG` and `ZEROBUS_DATASET_NAME` are set, `make dlt-zerobus` uses those
example-specific values automatically without changing the catalog/schema used by the other dlt
pipelines.

Delivery is at least once. The example emits a stable `event_id` and accepts `--run-id` so
downstream consumers can demonstrate de-duplication. Zerobus currently supports only `append`;
keep the existing merge examples on the default `COPY INTO` path. The command preflights the
endpoint and OAuth settings before extraction, avoiding dlt's current late-configuration failure.

## Credentials

dlt resolves credentials from (in order) env vars → `.dlt/secrets.toml`. The repo standard is **env
vars in the root `.env`** (`_common.py` calls `load_dotenv`). See
[../docs/setup-databricks.md](../docs/setup-databricks.md). The env-var names use dlt's
`DESTINATION__DATABRICKS__CREDENTIALS__*` convention.

## Extending

- New REST API: copy `rest_api_to_databricks.py`, change `base_url`/`resources`.
- New DB: set `SOURCES__SQL_DATABASE__CREDENTIALS` and edit the `SOURCE_QUERY` / table; `uv sync
  --extra postgres` (or add the driver you need). The custom-resource pattern avoids schema
  reflection, so it works even against restricted read replicas.
- Keep every pipeline pointed at the same `dataset_name` (`raw`) so the dbt sources stay valid.
