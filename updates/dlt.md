# dlt (dlthub) — update log

Newest on top. Each entry dated + sourced.

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
