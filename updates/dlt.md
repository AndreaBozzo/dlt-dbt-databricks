# dlt (dlthub) — update log

Newest on top. Each entry dated + sourced.

---

## 2026-10-09 — dlt 1.31.0 new minor; `cdc` merge strategy adds Databricks support

- **dlt 1.31.0** shipped **2026-10-07** — new minor release.
- **Databricks-specific addition:** `cdc` merge strategy now supported on Databricks (alongside
  DuckDB, MotherDuck, DuckLake, Snowflake, Postgres, BigQuery, MSSQL, Fabric, Athena/Iceberg,
  and Delta). `cdc` upserts a full snapshot and deletes destination rows that are absent from the
  incoming batch — useful for syncing tables that arrive as complete snapshots rather than diffs.
- **Delta `upsert` + `hard_delete`:** Delta `upsert` now honors `hard_delete`. Important caveat:
  nested tables with `upsert` + `hard_delete` raise `SchemaCorruptedException`; use flat tables or
  the `cdc` strategy with nested data.
- **`skip_unchanged_rows`:** New option for `cdc` and `upsert` strategies — only writes rows that
  changed. `row_version_column_name` enables single-column hash comparison. Reduces write
  amplification on large stable tables.
- **Breaking changes (review required for this repo's examples):**
  - `pendulum>=3` is now a hard requirement; `pendulum` helpers removed from `dlt.common.time`.
    None of this repo's ingestion examples use pendulum — no change needed.
  - JSON datetimes now serialized with `+00:00` offset instead of `Z`. The `merge_incremental.py`
    example passes `initial_value="2026-01-01T00:00:00Z"` as an input string — still accepted
    by dlt; no change needed.
  - `Incremental.last_value` now reflects the current cursor position (was previously the
    last-committed position). `sql_database_to_databricks.py` uses `cursor.last_value` for
    query filtering — behavior is compatible; no change needed.
  - `auto_abort_on_terminal_error` already defaulted to `False` since 1.30.0; no additional
    impact.
- **Other additions:** `source_filter` / `destination_scope` for merge row scoping;
  stateful `Relation.incremental()` for SQL push-down; `with_cursor()`, `get_current_range()`,
  `advance()` helpers on `Incremental`; `TTimeInterval` is now a `NamedTuple`; `croniter` added
  as a core dependency.
- **Example proposal — `cdc` merge strategy:** A new `ingestion/advanced/cdc_merge.py` example
  demonstrating the `cdc` write disposition on Databricks would be a useful addition. The example
  could use an in-memory generator (like `merge_incremental.py`) to emit a snapshot that includes
  updates and a deletion, showing that the destination row is removed. **Flagged as a proposal** —
  no infrastructure beyond a Databricks workspace is needed, but it should be reviewed alongside
  the `hard_delete` + nested-table caveat before building.

Sources:
- https://github.com/dlt-hub/dlt/releases/tag/1.31.0
- https://github.com/dlt-hub/dlt/releases

---

## 2026-08-26 — repo adopts 1.30.0 and adds per-resource Zerobus

- Re-locked the project from dlt 1.28.0 to **1.30.0** and raised the dependency floor so fresh
  environments cannot silently install an older Databricks integration.
- Leave Databricks `session_timezone` unset because serverless SQL warehouses can reject its
  Spark session configuration; timestamp-producing examples already emit explicit UTC values.
- Added `ingestion/advanced/zerobus_append.py` using the supported per-resource
  `databricks_adapter(..., insert_api="zerobus")` route. This is append-only and at-least-once; the
  example includes stable event IDs for downstream de-duplication. It avoids dlt's still-open
  destination-wide Zerobus reliability issue and the prior Unity Catalog Volume staging failure.

Sources:
- https://dlthub.com/docs/dlt-ecosystem/destinations/databricks
- https://github.com/dlt-hub/dlt/issues/3936

---

## 2026-08-12 — dlt 1.30.0 new minor; Databricks CREATE TABLE now atomic

- **dlt 1.30.0** shipped **2026-08-11** — first minor release since 1.29.0.
- **Databricks-specific change:** Comments on `_dlt_*` tables are no longer created by
  default. Previously, comment creation made `CREATE TABLE` non-atomic; 1.30.0 removes this
  behaviour by default and adds a `TBLPROPS`-based option to re-enable it. Existing pipelines
  benefit automatically — no example change needed.
- **Configurable session timezone:** `session_timezone` is now configurable on the Databricks
  destination (alongside ClickHouse, DuckDB, Postgres, Redshift, Snowflake). Informational for
  this repo — no timezone-sensitive pipelines exist yet.
- **Cross-destination joins:** New `Relation.join()` capability for joining datasets across
  different destinations (duckdb, motherduck, ducklake, lance, lancedb, filesystem). Databricks
  is not in the supported query-engine list; Databricks-to-Databricks joins still require a
  Unity Catalog query or a dbt model.
- **Breaking changes (none affect this repo):**
  - `auto_abort_on_terminal_error` now defaults to `False` — failed load packages no longer
    auto-abort; use `pipeline.abort_packages()` or the equivalent CLI command.
  - Filesystem layouts without `{ext}` now append the extension automatically.
  - Table prefix separator preserved (e.g. `event.` not `event`).
- **Other additions:** Input/output lineage in traces (OpenLineage-compatible); manual load
  package abort with `abort_packages`; retryable schema migrations via `retry_schema_update`.

Sources:
- https://github.com/dlt-hub/dlt/releases/tag/1.30.0
- https://github.com/dlt-hub/dlt/releases

---

## 2026-07-25 — dlt 1.29.1 patch (2026-07-24); no Databricks-specific changes

- **dlt 1.29.1** shipped **2026-07-24** — a patch release on top of 1.29.0.
- **No Databricks-specific changes** to the destination; no example updates needed.
- **Key changes:**
  - `instance` requirement spec added for job resources.
  - Case-sensitive identifier handling fixed in sqlglot schema normalization.
  - REST paginator stop-condition now preserved across paginator chains.
  - JWT authentication fixed when scopes are absent.
  - Column removal logic improved in `_dlt_load_id` column processing.
  - **CI note:** transient Databricks (and Azure SQL/ODBC) connection errors are now retried
    rather than failing the test run — a testing-infrastructure improvement, not a destination
    code change.

Sources:
- https://github.com/dlt-hub/dlt/releases/tag/1.29.1
- https://github.com/dlt-hub/dlt/releases

---

## 2026-07-15 — dlt 1.29.0 new minor release (2026-07-13); no Databricks-specific changes

- **dlt 1.29.0** shipped **2026-07-13** — the first new minor release since 1.28.x.
- **No Databricks-specific changes** in this release; no example updates needed.
- **Key new features (generic):**
  - **ClickHouse staging-optimized replace** (PR #3927): atomic table swaps via `EXCHANGE TABLES` on
    ClickHouse — not relevant for Databricks.
  - **AWS Secret Manager provider** (PR #4162): resolve dlt secrets directly from AWS Secrets Manager
    without a local config file — useful for Databricks-on-AWS deployments that already use ASM for
    credentials, but requires no changes to Databricks-destination code.
  - **Explicit `Relation.join()`** (PR #3868): dataset-level join API with cross-destination
    compatibility rules (`physical_location()` + `can_join_with`). Enables querying across dlt
    datasets from different destinations — worth watching for future Unity Catalog cross-schema
    query examples.
  - **Arrow type promotion fix** (PR #3896): fixes crashes when Arrow type promotions span multiple
    flush batches — relevant if loading large columnar payloads to any destination including
    Databricks, though no Databricks-specific regressions were reported.
- **Python support**: 3.10–3.14 (unchanged).

Sources:
- https://github.com/dlt-hub/dlt/releases/tag/1.29.0
- https://github.com/dlt-hub/dlt/releases

---

## 2026-07-14 — dlt 1.29.0 minor release (2026-07-13); no Databricks impact

- **dlt 1.29.0** shipped **2026-07-13** — first minor release since 1.28.0.
- **No Databricks-specific changes** in this release; no example updates needed.
- Notable additions in other destinations and capabilities:
  - **ClickHouse** — new `staging-optimized` replace strategy for atomic table swaps via
    `EXCHANGE TABLES`.
  - **AWS Secret Manager** config provider added (feature-parity with Google Secret Manager).
  - **Relations API** — `Relation.join()` for explicit cross-dataset joins; `physical_location()`
    accessor and `can_join_with` rules for cross-destination join-compatibility checks.
  - **BigQuery** — opt-in atomic replace via `enable_atomic_replace` using single-job
    `WRITE_TRUNCATE_DATA` loads.
  - **DuckDB** now fully supported as a SQLAlchemy destination.
  - **Parquet compression** configurable via `DATA_WRITER__COMPRESSION`.
- Notable fixes: normalize crash on empty Arrow tables with `_dlt_id`; metric aggregation
  undercounting across normalize workers; Airflow parallel staging truncation; merge SQL
  generation (subquery placement).

Sources:
- https://github.com/dlt-hub/dlt/releases/tag/1.29.0
- https://github.com/dlt-hub/dlt/releases

---

## 2026-07-11 — dlt 1.28.2 maintenance patch (2026-07-10); no Databricks impact

- **dlt 1.28.2** shipped **2026-07-10** — a maintenance patch on top of 1.28.1.
- **Sole change:** the `dlthub-client` upper-version cap is relaxed so the 1.28.x branch can
  consume future `dlthub-client` releases without requiring a new dlt minor release. No
  functional changes to the dlt library itself.
- **No Databricks-specific changes** in this release; no example updates needed.
- Python support unchanged: 3.10–3.14.

Sources:
- https://pypi.org/project/dlt/#history
- https://github.com/dlt-hub/dlt/releases

---

## 2026-06-25 — release check: still 1.28.1; retroactive FK/create_indexes finding affects example

- **No new dlt release** since 1.28.1 (2026-06-19).
- **Retroactive finding from 1.28.0 (missed in prior checks):** PR #4011 fixed the Databricks
  destination to emit PRIMARY/FOREIGN KEY constraints **only when `create_indexes=True`** is set
  (default is `False`). Previously FK hints were emitted unconditionally, triggering Unity Catalog
  `UC_REFERENTIAL_CONSTRAINT_DOES_NOT_EXIST` errors when the matching primary key constraint was
  absent.
- **Impact on this repo:** `ingestion/advanced/data_contracts.py` documents FK emission via
  `references=[...]` hints but called `databricks_pipeline()`, which uses `destination="databricks"`
  with `create_indexes` at its default (`False`). As of 1.28.0+ the FK constraints were silently
  skipped, making the example incorrect.
- **Fix applied:** `data_contracts.py` now constructs an explicit destination object with
  `create_indexes=True`, so FK constraints are actually emitted as the docstring describes.

Sources:
- https://github.com/dlt-hub/dlt/releases
- https://github.com/dlt-hub/dlt/pull/4011

---

## 2026-06-20 — 1.28.1 patch released (2026-06-19); no Databricks impact

- **dlt 1.28.1** shipped **2026-06-19** — a patch release on top of 1.28.0.
- **Python 3.9 dropped**: 3.9 reached EOL 2025-10-31; dlt now tests 3.10+ only. *Not relevant for
  this repo* — `pyproject.toml` already requires `>=3.12`.
- **Dataset browser**: dashboard now opens directly on the dataset browser and auto-selects the most
  recently used pipeline (UI improvement, no code impact).
- **connectorx temporal columns**: fixes nanosecond-precision timestamps returned by newer connectorx
  versions being mis-normalised. Does not affect this repo's `sql_database_to_databricks.py`, which
  uses a plain SQLAlchemy query resource (not connectorx).
- **ISO week cursor fix**: week-date format `YYYY-Www` was mis-detected as `%Y-W%W`, causing
  round-trip errors at year boundaries. Fix ensures incremental cursors using ISO week dates are
  stored and re-parsed correctly.
- **PostgreSQL NULL-char removal**: INSERT statements now strip 0x0 characters. Low impact for this
  repo's Postgres example (RNAcentral read replica is clean data).
- **SQL metadata caching**: user-provided metadata now correctly consulted in both eager and deferred
  reflection modes — relevant if you pass a pre-built `MetaData` object to `sql_database`.
- **No Databricks-specific changes** in this release.

Sources:
- https://github.com/dlt-hub/dlt/releases

---

## 2026-06-18 — release check: 1.28.0 still latest; Databricks-relevant 1.27/1.28 detail

- **No new `dlt` release** since 1.28.0 (2026-06-15); it remains latest. No example change needed.
- **Relevant to the staging workaround logged on 2026-06-17:**
  - **1.28.0** made default credentials pass to external consumers as *refreshable*, fixing
    `ExpiredToken` failures on long-running loads — a plausible mitigation for some Databricks
    destination staging failures, worth a focused retest before filing the upstream issue.
  - **1.27.0** added a **Databricks Zerobus** insert API option via `databricks_adapter` for Delta
    loading — an alternative ingestion path to evaluate against the current Spark landing fallback.

Sources:
- https://github.com/dlt-hub/dlt/releases

---

## 2026-06-17 — Databricks serverless compatibility findings from live bundle run

- **Import collision:** Databricks serverless can preload built-in Delta Live Tables (`dlt`) hooks
  that collide with dlthub's `dlt` package. The live job log showed:
  `Unexpected internal error when monkey patching dlt module: cannot import name 'overrides' from partially initialized module 'dlt'`.
  dlt's Databricks destination docs now call out removing Databricks post-import hooks / partially
  initialized DLT modules, but also warn that `sys.meta_path` / `sys.modules` workarounds are fragile.
- **Unity Catalog Volume staging:** dlt's Databricks destination reached load, then failed while
  uploading parquet through SQL connector staging to
  `/Volumes/workspace/raw_staging/_dlt_staging_load_volume/...`, with
  `LoadClientJobRetry` wrapping a `Connection refused` to the Databricks storage host.
- **Repo workaround:** the bundle now uses a Spark landing mode for the minimal REST demo tables in
  Databricks serverless, while preserving the normal dlt destination path for local/direct dlt runs.
- **Upstream opportunity:** turn this into a focused dlt issue or docs PR: "Databricks serverless
  job task + Unity Catalog volume staging failure / DLT import hook collision", including sanitized
  task run ids, dlt/dbt/databricks versions, and the exact workaround.

Sources:
- https://dlthub.com/docs/dlt-ecosystem/destinations/databricks

---

## 2026-06-17 — latest release check: 1.28.0

- **Latest release is 1.28.0**, published on 2026-06-15.
- The repo's dependency range (`dlt[databricks]>=1.6.0` and `dlt[sql_database]>=1.6.0`) already
  resolves to this release in the current lockfile.
- No example changes required from this refresh.

Sources:
- https://pypi.org/project/dlt/
- https://github.com/dlt-hub/dlt/releases

---

## 2026-06-16 — seed: Databricks destination capabilities

State of the Databricks destination as of seeding:

- **Unity Catalog** integration for governed loads (catalog/schema/table).
- **Table formats**: Delta (default) and **Apache Iceberg** via `table_format="iceberg"`.
- **Constraints**: emits PRIMARY KEY / FOREIGN KEY when `primary_key` and `references` hints are set.
- **State sync** fully supported (incremental cursors, pipeline state persisted).
- **Two run modes**: (a) anywhere, with explicit Databricks + cloud-storage credentials; (b) **inside
  a Databricks notebook with zero config** (credentials inferred).
- **Staging**: bulk/file loads stage to cloud storage / a Unity Catalog Volume, then `COPY INTO`.

Reflected in the examples under `ingestion/`.

Sources:
- https://dlthub.com/docs/dlt-ecosystem/destinations/databricks
- https://dlthub.com/blog/dlt-for-databricks

> Refresh: fetch the dlt changelog + GitHub releases (see ../sources.md) and append the next dated entry.
