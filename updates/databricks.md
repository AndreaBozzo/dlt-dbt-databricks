# Databricks (Lakeflow / Unity Catalog) — update log

Newest on top. Each entry dated + sourced.

---

## 2026-07-16 — SDK gate lifted: dbt-databricks 1.12.2 raises cap to <0.118.0

- **No new databricks-sdk release** since 0.120.0 (2026-07-02, logged 2026-07-03).
- **Gate lifted by dbt-databricks 1.12.2 (2026-07-09):** the adapter's SDK upper cap has been
  raised from `<0.105.0` to `<0.118.0`. Running `uv lock` in this repo will resolve
  **databricks-sdk to 0.117.x** (the highest 0.117.x on PyPI), ending the long period of being
  stuck on 0.104.0.
- **SDK 0.118.0–0.120.0 still out of reach** until the adapter bumps its cap past 0.118.0.
  The `iamv2.User.name` breaking change (0.120.0) therefore remains irrelevant to this repo.
- **SDP / platform release notes** returned HTTP 403 this run — no new Lakeflow/SDP entries confirmed.

Sources:
- https://github.com/databricks/dbt-databricks/releases/tag/v1.12.2
- https://github.com/databricks/databricks-sdk-py/releases

---

## 2026-07-03 — databricks-sdk 0.120.0 released (adapter cap still binds)

- **Databricks SDK for Python 0.120.0** shipped **2026-07-02**. Highlights: `download_message_attachment_visualization()` added to the Genie workspace service; new `sql_condition` fields across job trigger-related classes; `full_name` field added to IAM User (paired with breaking change below); `excluded_schemas` for `CatalogConfig`; `telemetry_config` across serving endpoint classes; `status_message` for `AiRuntimeTaskOutput`; PostgreSQL service additions (`replace_existing`, pooled host options, autoscaling limits). Breaking change — **`name` field removed from `databricks.sdk.service.iamv2.User`** (replaced by `full_name`); code calling `.name` on an IAM User object will break on 0.120.0+.
- **No repo change:** `dbt-databricks 1.12.1` still pins `databricks-sdk<0.105.0`, so the resolved environment stays on **0.104.0**. The `iamv2.User.name` breaking change is therefore irrelevant to this repo until the adapter cap is lifted.
- **SDP / platform release notes** returned HTTP 403 this run — no new Lakeflow/SDP entries confirmed.

Sources:
- https://github.com/databricks/databricks-sdk-py/releases/tag/v0.120.0

---

## 2026-06-25 — databricks-sdk 0.119.0 released (adapter cap still binds)

- **Databricks SDK for Python 0.119.0** shipped **2026-06-24**. Highlights: meta-harness user-agent
  detection via `OMNIGENT` env var; new `cancel_pending_cluster_enforcement()` for workspace policy
  compliance; `ai_runtime_task` and `ai_runtime_task_output` fields in the jobs service; `xlarge`
  compute sizing option; breaking change — `replicate_workspace_assets` is now optional (was
  required) in workspace-set disaster recovery configurations.
- **No repo change:** `dbt-databricks 1.12.1` still pins `databricks-sdk<0.105.0`, so the resolved
  environment stays on **0.104.0**. Watch dbt-databricks releases for the cap bump.
- **SDP / platform release notes** returned HTTP 403 this run — no new Lakeflow/SDP entries confirmed.

Sources:
- https://github.com/databricks/databricks-sdk-py/releases

---

## 2026-06-18 — databricks-sdk 0.118.0 released (adapter cap still binds)

- **Databricks SDK for Python 0.118.0** shipped **2026-06-18** (today). Highlights: data API methods
  for the PostgreSQL service, an Azure capacity-reservation-group attribute, and serverless compute
  support for pipelines. (0.117.0 on 2026-06-11 added OIDC token caching and made
  `WorkspaceClient.dbutils` lazy.)
- **No repo change:** `dbt-databricks 1.12.1` still pins `databricks-sdk<0.105.0`, so the resolved
  environment stays on **0.104.0**. 0.117.x/0.118.0 are out of reach until the adapter relaxes the
  cap — keep watching dbt-databricks releases for that bump rather than the SDK side.
- **No new SDP / platform release notes** to fold in since the 2026-06-17 entry.

Sources:
- https://github.com/databricks/databricks-sdk-py/releases

---

## 2026-06-17 — serverless bundle task behavior from live deployment

- **Serverless-only workspace:** bundle deployment failed until job clusters/libraries were replaced
  with serverless task `environment_key` plus a shared `environments` specification.
- **Run-output workflow:** multi-task parent run output is not supported; use
  `databricks jobs get-run <parent-run-id> --output json` to find each `tasks[].run_id`, then call
  `databricks jobs get-run-output <task-run-id> --output json`.
- **Successful run:** the dev bundle reached `TERMINATED SUCCESS` after landing `workspace.raw`
  demo tables via Spark and running the Databricks dbt task against warehouse `b8e5ba2ff75d1ce5`.
- **Upstream opportunity:** Databricks docs/examples could better connect Asset Bundle serverless
  `environment_key`, dbt tasks, Python task logs, and the parent-vs-task run-output CLI pattern.

Sources:
- https://docs.databricks.com/api/workspace/jobs/create
- https://docs.databricks.com/api/workspace/jobs/getrunoutput
- https://docs.databricks.com/aws/en/compute/serverless/dependencies

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
