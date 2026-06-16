# dlt (dlthub) — update log

Newest on top. Each entry dated + sourced.

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
