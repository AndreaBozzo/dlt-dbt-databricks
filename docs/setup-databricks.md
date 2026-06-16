# Databricks setup

What you need before running anything in this repo, and how to wire credentials.

## 1. Prerequisites in the workspace

- **Unity Catalog** enabled, with a catalog you can write to (default in examples: `main`).
- A **SQL warehouse** (Serverless or Pro). Both dlt and dbt connect through it via its HTTP path.
- Permission to **create schemas and tables** in your catalog. dlt creates the *raw* schema
  (default `raw`); dbt creates the *analytics* schema (default `analytics`).

### Find your connection details
SQL Warehouses → select your warehouse → **Connection details**:
- **Server hostname** → `DATABRICKS_HOST` (without `https://`)
- **HTTP path** → `DATABRICKS_HTTP_PATH` (e.g. `/sql/1.0/warehouses/abcd1234efgh5678`)

## 2. Authentication

### Now: Personal Access Token (PAT)
User Settings → **Developer** → **Access tokens** → *Generate new token*. Put it in
`DATABRICKS_TOKEN`. Quickest path to a runnable demo.

### Production: OAuth machine-to-machine (service principal)
Prefer a **service principal** with OAuth M2M over a personal PAT for anything beyond local dev.

- **dlt**: set `client_id` / `client_secret` instead of `access_token` in
  `ingestion/.dlt/secrets.toml` (see `DESTINATION__DATABRICKS__CREDENTIALS__CLIENT_ID` /
  `__CLIENT_SECRET` env vars).
- **dbt**: in `profiles.yml`, replace `token:` with
  `auth_type: oauth`, `client_id:`, `client_secret:` (`dbt-databricks` supports OAuth M2M).

## 3. Configure this repo

```bash
cp .env.example .env
# fill: DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN, DATABRICKS_CATALOG, DATABRICKS_SCHEMA

cp transformation/dbt_databricks/profiles.yml.example transformation/dbt_databricks/profiles.yml
# profiles.yml reads the same env vars, so usually no edits needed
```

The Python scripts call `load_dotenv()`, so `.env` is picked up automatically under `uv run`.
dlt also accepts the same values from `ingestion/.dlt/secrets.toml` (copy from the `.example`).

### Which schema does what
| Layer | Schema (default) | Created by | Set via |
| --- | --- | --- | --- |
| Raw / landed | `raw` | dlt | `DLT_DATASET_NAME` |
| Models (staging→marts) | `analytics` | dbt | `DATABRICKS_SCHEMA` |

dbt's `sources.yml` points at the dlt **raw** schema — that's the handoff. Keep the two schema names
consistent across `.env` and `profiles.yml`.

## 4. Verify connectivity

```bash
uv sync
uv run python -c "import dlt, dbt; print('imports ok')"
make dbt-parse        # parses dbt project; needs profiles.yml but does not write tables
make dlt-rest         # first real write: loads a small REST API dataset into <catalog>.raw
```

If `dlt-rest` succeeds you'll see the new tables under your catalog's `raw` schema in the
Databricks **Catalog** explorer.

## 5. Staging for large/file loads (optional)

For file or bulk loads dlt stages data before `COPY INTO`. On Databricks the simplest staging is a
**Unity Catalog Volume**. Create one (`CREATE VOLUME <catalog>.<schema>.dlt_staging;`) and reference
it from `ingestion/.dlt/config.toml`. The REST/SQL examples here are small enough to load directly.

## Troubleshooting

- **403 / permission denied** → your principal lacks `USE CATALOG` / `CREATE SCHEMA` / `CREATE TABLE`.
- **Warehouse won't start / timeouts** → confirm the warehouse is running and the HTTP path matches it.
- **dbt can't find profile** → pass `--profiles-dir transformation/dbt_databricks` (the Makefile does).
