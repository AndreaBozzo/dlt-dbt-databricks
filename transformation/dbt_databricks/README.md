# Transformation (dbt on Databricks)

dbt project using the `dbt-databricks` adapter. It reads the `raw` schema that dlt loads
([../../ingestion/](../../ingestion/)) and builds `staging → intermediate → marts`.

## Layout

```
models/
├── sources.yml                       # dlt-owned `raw` schema + samples.healthverity (the handoffs)
├── staging/      stg_rest_posts, stg_rest_comments, stg_claims        (+ tests)
├── intermediate/ int_post_comment_counts, int_claims
└── marts/        mart_post_engagement (incremental merge),
                  mart_claims_by_payer, mart_member_summary            (+ tests)
macros/    cents_to_dollars.sql        # example reusable macro
snapshots/ snap_customers.sql          # SCD2 example (disabled until raw.customers exists)
```

### Two domains

- **jsonplaceholder** (`*_rest_*`, `*_post_*`) — models on the dlt REST API output.
- **insurance** (`*_claims`, `mart_claims_by_payer`, `mart_member_summary`) — a real analytics layer
  on `samples.healthverity` synthetic claims (~410k rows). Shows type casting from all-string source
  data, surrogate keys, payer/member metrics, and `warn`-severity DQ tests for claim reversals
  (negative/NULL money is expected in real claims data).

Materializations (set in `dbt_project.yml`): staging/intermediate = `view`, marts = `table`;
`mart_post_engagement` overrides to `incremental` + `merge`.

## Run

```bash
make dbt-deps     # install dbt_utils + dbt_expectations (once)
make dbt-parse    # validate without touching the warehouse
make dbt-build    # run + test all models
make dbt-test     # tests only
```

Or directly (note the dirs flags the Makefile passes):

```bash
uv run dbt build \
  --project-dir transformation/dbt_databricks \
  --profiles-dir transformation/dbt_databricks
```

## Config

`profiles.yml` (copy from `.example`) reads everything from env vars in the repo-root `.env`:
`DATABRICKS_HOST/HTTP_PATH/TOKEN/CATALOG/SCHEMA` and `DLT_DATASET_NAME` (the raw source schema).
For production auth use OAuth M2M — see [../../docs/setup-databricks.md](../../docs/setup-databricks.md).

## dbt Fusion (2026)

`dbt-databricks` works with the new Rust **Fusion** engine (Databricks support in beta). To try it,
provision the project on a Fusion release track in dbt Cloud, or install the Fusion CLI — see
[../../updates/dbt.md](../../updates/dbt.md). This project's models are standard SQL and parse under
both engines.
