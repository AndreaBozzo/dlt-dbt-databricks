# Databricks (Lakeflow / Unity Catalog) — update log

Newest on top. Each entry dated + sourced.

---

## 2026-06-16 — seed: DLT → Lakeflow SDP rename + 2026 features

- **Delta Live Tables (DLT) renamed to Lakeflow Spark Declarative Pipelines (SDP).** No migration
  required — existing DLT code runs unchanged under SDP. (Note: unrelated to dlthub's `dlt` library.)
- **Lakeflow** is the umbrella: **Connect** (ingestion), **Spark Declarative Pipelines** (ex-DLT),
  **Jobs** (ex-Workflows).

SDP features/improvements shipped **Jan 14 – Feb 25, 2026**:
- **Type widening** for Delta tables — broaden column types without a full pipeline reset (schema
  evolution that previously needed manual intervention).
- **Data-quality expectations stored in Unity Catalog** — version-controlled, auditable, shareable
  across pipelines.
- **Queued execution mode** — concurrent update requests queue and run sequentially instead of
  failing with conflicts.
- **New flow syntax** for creating streaming tables — more direct, declarative streaming definitions.

Sources:
- https://docs.databricks.com/aws/en/release-notes/dlt/2026
- https://docs.databricks.com/aws/en/ldp/where-is-dlt

> Refresh: fetch the SDP 2026 release-notes page + platform release notes (see ../sources.md).
