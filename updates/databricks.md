# Databricks (Lakeflow / Unity Catalog) — update log

Newest on top. Each entry dated + sourced.

---

## 2026-06-17 — bundle host rule + SDK refresh

- **Asset Bundle host configuration**: current Databricks CLI validation rejects variable
  interpolation in `workspace.host` because that field configures authentication. Use
  `DATABRICKS_HOST`, an explicit CLI profile, or a literal host in target-specific local config
  instead of `${var.workspace_host}`.
- **Databricks SDK for Python**: latest release is **0.117.0** (2026-06-11), but
  `dbt-databricks 1.12.1` currently requires `databricks-sdk>=0.68.0,<0.105.0`. The repo therefore
  stays on **0.104.0** until the adapter relaxes that cap.
- **Platform watch**: June 2026 platform notes include Lakeflow Designer GA, AUTO CDC flows for
  streaming tables in Databricks SQL GA, OIDC support for sharing to Iceberg clients, and more
  Lakeflow/Unity Catalog improvements worth watching for future examples.

Sources:
- https://docs.databricks.com/aws/en/dev-tools/bundles/variables
- https://github.com/databricks/databricks-sdk-py/releases
- https://docs.databricks.com/aws/en/release-notes/product/

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
