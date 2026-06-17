# Radar — top of mind

Rolling cross-tool summary. Newest snapshot on top. Details live in the per-tool files.

---

## 2026-06-17 — dependency and bundle validation refresh

**dlt (dlthub)** — latest PyPI/GitHub release is **1.28.0** (released 2026-06-15). The repo's
dependency range and lockfile already resolve to this line, so no code change was needed. → [dlt.md](dlt.md)

**dbt** — `dbt-databricks` has moved to **1.12.1** in the June 2026 compatible track while this repo
still runs with classic dbt Core **1.11.11** locally. The project parses cleanly on the resolved
adapter, and the update note now replaces the older "~1.11.x" wording. → [dbt.md](dbt.md)

**Databricks** — Asset Bundle validation caught a current CLI rule: `workspace.host` is auth
configuration and cannot use `${var...}` interpolation. The bundle now expects `DATABRICKS_HOST` or
a configured CLI profile. `databricks-sdk` **0.117.0** is available, but `dbt-databricks 1.12.1`
currently caps the SDK below `0.105.0`, so the repo remains on **0.104.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Add a lightweight CI bundle-validate step once repository secrets for
`DATABRICKS_HOST` and auth are available; otherwise keep validation documented as a local/pre-deploy
check.

---

## 2026-06-16 — initial seed

**dlt (dlthub)** — Databricks destination is mature: Unity Catalog integration, **Delta (default) +
Iceberg** via `table_format`, PRIMARY/FOREIGN KEY constraints from `primary_key`/`references` hints,
full state sync, and **zero-config** runs inside Databricks notebooks. → [dlt.md](dlt.md)

**dbt** — `dbt-databricks` ~**1.11.x**. The new Rust **Fusion** engine supports Databricks in **beta**;
new dbt Cloud environments provision on a Fusion release track by default. Fusion ignores user-set
threads on Databricks and auto-optimizes parallelism. → [dbt.md](dbt.md)

**Databricks** — **DLT (Delta Live Tables) was renamed to Lakeflow Spark Declarative Pipelines (SDP)**;
existing code runs unchanged. Jan–Feb 2026 SDP additions: **type widening** for Delta (no full reset),
**data-quality expectations stored in Unity Catalog**, **queued execution mode**, and **new flow
syntax** for streaming tables. → [databricks.md](databricks.md)

**Watch / opportunities** — Iceberg-on-UC + dlt is an area worth a hands-on writeup; potential upstream
example contribution to dlt or dbt-databricks docs. (See updates/README.md.)
