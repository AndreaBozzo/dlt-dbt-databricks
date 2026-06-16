# dbt + dbt-databricks — update log

Newest on top. Each entry dated + sourced.

---

## 2026-06-16 — seed: adapter 1.11.x + Fusion beta on Databricks

- **`dbt-databricks` ~1.11.x** is the current adapter line in 2026. Design defaults: Delta format,
  `merge` for incremental models, Photon for expensive queries, Unity Catalog for governance.
- **Fusion engine (Rust)** — Databricks support is in **beta**. New dbt Cloud environments (Developer/
  Starter/Enterprise) provision on a **Fusion Stable** release track by default across supported
  adapters (Snowflake, Redshift, BigQuery, Databricks).
- **Release tracks** — Nightly / Stable / Extended / Fallback let you control update cadence and risk.
- **Databricks-specific**: Fusion **ignores user-set `threads`** and auto-optimizes parallelism for
  max performance.

Implication for this repo: models are standard SQL and parse under both the classic engine and Fusion;
no changes needed to try Fusion.

Sources:
- https://docs.getdbt.com/docs/dbt-versions/2025-release-notes
- https://docs.getdbt.com/docs/fusion/about-fusion
- https://github.com/databricks/dbt-databricks/releases

> Refresh: fetch dbt Cloud release notes + dbt-databricks GitHub releases (see ../sources.md).
