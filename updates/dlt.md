# dlt (dlthub) — update log

Newest on top. Each entry dated + sourced.

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
