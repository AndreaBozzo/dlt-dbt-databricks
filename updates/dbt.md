# dbt + dbt-databricks — update log

Newest on top. Each entry dated + sourced.

---

## 2026-07-16 — dbt-databricks 1.12.2 (2026-07-09): SDK cap raised to <0.118.0

- **dbt-databricks 1.12.2** shipped **2026-07-09** — the first adapter release to break past the
  `<0.105.0` SDK ceiling that has kept this repo on **databricks-sdk 0.104.0** since June 2026.
- **databricks-sdk cap raised to `<0.118.0`** (up from `<0.105.0` in 1.12.1). With 1.12.2
  installed, `uv lock` will resolve databricks-sdk up to **0.117.x**. Note: 0.118.0–0.120.0
  remain out of reach until the adapter bumps its cap again.
- **dbt-core upper bound raised to `<1.11.13`** (picks up dbt-core 1.11.12).
- **databricks-sql-connector upper bound raised to `<4.3.1`** (up from `<4.3.0`).
- **New features:**
  - **catalogs.yml v2 support** — opt in with `use_catalogs_v2: true` in dbt-core settings.
  - **`skip_optimize` model config** — lets a model opt out of the post-materialization
    `OPTIMIZE` call without dropping `zorder`/`liquid_clustered_by`, delegating optimization
    elsewhere (useful for latency-sensitive models or external OPTIMIZE orchestration).
  - **Rust kernel backend** — enable via `connection_parameters: {use_kernel: true}` on SQL
    warehouses; supports PAT + Databricks OAuth; requires Python ≥ 3.10 (satisfied by this repo's
    ≥ 3.12 requirement).
- **Behavioral change:** changing `expression` on an existing PK/FK constraint
  (`RELY`↔`NORELY`) no longer applies on incremental runs — requires `--full-refresh`.
  (Relevant if constraints are added to the marts; current marts use `data_tests` only.)
- **Action for this repo:** run `uv lock` to upgrade from dbt-databricks 1.12.1 → 1.12.2 and
  databricks-sdk 0.104.0 → 0.117.x. SDK breaking changes introduced between 0.104.0 and 0.117.x
  (`replicate_workspace_assets` becoming optional in 0.119.0, `cancel_pending_cluster_enforcement`
  added in 0.119.0, `iamv2.User.name` removed in 0.120.0) are all above the new cap and therefore
  not a concern.

Sources:
- https://github.com/databricks/dbt-databricks/releases/tag/v1.12.2

---

## 2026-06-18 — release check: 1.12.1 still latest; contract.enforced detail

- **No new `dbt-databricks` release** since 1.12.1 (2026-06-10); it remains the current adapter line.
- **Detail worth flagging for this repo:** 1.12.1 made column-level constraints require
  `contract.enforced: true` explicitly (a breaking change vs. earlier behavior). The marts here lean
  on dbt contracts, so if column constraints are ever added, set `contract.enforced: true` or they'll
  be silently ignored.
- 1.12.1's runtime correlation IDs (`job_id`, `job_run_id`, `task_run_id`) line up with the
  parent-vs-task run-output CLI pattern logged under databricks.md — handy for tracing dbt-task runs.
- Adapter floor is `databricks-sql-connector>=4.2.6` and `databricks-sdk>=0.76.0`; the SDK upper cap
  (`<0.105.0`) is what keeps the repo on SDK 0.104.0. → [databricks.md](databricks.md)

Sources:
- https://github.com/databricks/dbt-databricks/releases

---

## 2026-06-17 — Databricks dbt task contract findings from live bundle run

- **dbt task logs are high signal:** `dbt_output.logs` from the task run clearly showed dbt
  `1.11.11`, adapter `databricks=1.12.1`, failing model names, SQLSTATEs, and final
  `PASS/WARN/ERROR/SKIP` totals.
- **Raw landing contract matters:** the Spark fallback initially wrote JSONPlaceholder camelCase
  fields (`userId`, `postId`) and omitted dlt metadata. The dbt staging models expected dlt-style
  `user_id`, `post_id`, and `_dlt_load_id`. Normalizing the fallback to that contract made the
  end-to-end Databricks bundle run succeed.
- **Upstream opportunity:** add a small "raw contract" note/example for dbt-on-Databricks demos that
  are fed by dlt: preserve dlt's column normalization and `_dlt_load_id` when using fallback loaders
  or seed data.

Sources:
- https://docs.getdbt.com/reference/dbt-commands
- https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types

---

## 2026-06-17 — dbt-databricks 1.12.1 in June compatible track

- **`dbt-databricks` 1.12.1** is now listed in dbt's June 2026 compatible track and is the version
  resolved by this repo.
- Local parse still runs with `dbt-core` **1.11.11** plus the Databricks adapter **1.12.1**; the
  project parses cleanly with the existing SQL/model layout.
- The old "~1.11.x" radar wording is stale; treat **1.12.x** as the current adapter line for this
  repo unless a future release note says otherwise.

Sources:
- https://docs.getdbt.com/docs/dbt-versions/compatible-track-changelog
- https://pypi.org/project/dbt-databricks/
- https://github.com/databricks/dbt-databricks/releases

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
