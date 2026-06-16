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
├── _common.py                 # shared: load .env + build the Databricks-destination pipeline
├── pipelines/
│   ├── rest_api_to_databricks.py     # declarative rest_api source, parent→child, merge
│   └── sql_database_to_databricks.py # sql_database source, incremental cursor + merge
└── advanced/
    ├── merge_incremental.py   # write_disposition="merge" + incremental cursor (upsert/CDC)
    ├── iceberg_table_format.py# table_format="iceberg" on Unity Catalog
    └── data_contracts.py      # schema contracts (freeze) + PK/FK hints → UC constraints
```

## Run

```bash
make dlt-rest        # or: uv run python ingestion/pipelines/rest_api_to_databricks.py
make dlt-merge       # run twice to see idempotent upsert
make dlt-iceberg
make dlt-contracts
```

`rest_api_to_databricks.py` uses a public no-auth API, so it's the best first smoke test once your
`.env` has Databricks credentials.

## Credentials

dlt resolves credentials from (in order) env vars → `.dlt/secrets.toml`. The repo standard is **env
vars in the root `.env`** (`_common.py` calls `load_dotenv`). See
[../docs/setup-databricks.md](../docs/setup-databricks.md). The env-var names use dlt's
`DESTINATION__DATABRICKS__CREDENTIALS__*` convention.

## Extending

- New REST API: copy `rest_api_to_databricks.py`, change `base_url`/`resources`.
- New DB: set `SOURCES__SQL_DATABASE__CREDENTIALS` and the `TABLES` list; `uv sync --extra postgres`
  (or add the driver you need).
- Keep every pipeline pointed at the same `dataset_name` (`raw`) so the dbt sources stay valid.
