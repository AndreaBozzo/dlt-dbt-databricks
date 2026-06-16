# Databricks setup

What you need before running anything in this repo, and how to wire credentials.

## 1. Prerequisites in the workspace

- **Unity Catalog** enabled, with a catalog you can write to (default in examples: `workspace`).
- A **SQL warehouse** (Serverless or Pro). Both dlt and dbt connect through it via its HTTP path.
- Permission to **create schemas and tables** in your catalog. dlt creates the *raw* schema
  (default `raw`); dbt creates the *analytics* schema (default `analytics`).

### Find your connection details
SQL Warehouses → select your warehouse → **Connection details**:
- **Server hostname** → `DATABRICKS_HOST` (without `https://`)
- **HTTP path** → `DATABRICKS_HTTP_PATH` (e.g. `/sql/1.0/warehouses/abcd1234efgh5678`)

## 2. Authentication

### Local dev: Databricks CLI OAuth (recommended)

One-time setup — no PAT, no secrets in files:

```bash
databricks auth login --host https://YOUR_HOST.cloud.databricks.com
# browser opens → login → done. Credentials saved to ~/.databrickscfg.
```

- **dbt**: `auth_type: oauth` in `profiles.yml` reads `~/.databrickscfg` automatically.
  Run `uv run dbt debug` — no env vars, no browser popup after first login.
- **dlt**: still needs a PAT (see below). dlt doesn't yet read `~/.databrickscfg`.

### dlt: Personal Access Token (PAT)
User Settings → **Developer** → **Access tokens** → *Generate new token*. Put it in
`.env` as `DATABRICKS_TOKEN` and `DESTINATION__DATABRICKS__CREDENTIALS__ACCESS_TOKEN`.
dlt loads `.env` automatically via `python-dotenv`.

### Production: OAuth machine-to-machine (M2M / service principal)
Replace the PAT/U2M token with a service principal for any non-local workload:

- **dlt**: set `client_id` / `client_secret` in `ingestion/.dlt/secrets.toml` (env vars:
  `DESTINATION__DATABRICKS__CREDENTIALS__CLIENT_ID` / `__CLIENT_SECRET`).
- **dbt**: add `client_id:` / `client_secret:` env vars to `profiles.yml` prod target
  (see the `prod:` block in `profiles.yml.example`).

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
