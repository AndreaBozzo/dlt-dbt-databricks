# Radar — top of mind

Rolling cross-tool summary. Newest snapshot on top. Details live in the per-tool files.

---

## 2026-09-07 — databricks-sdk v0.136.0 new; dlt and dbt unchanged

**dlt** — **1.30.0** (2026-08-11) unchanged. No new release since the 2026-09-04 entry; no
Databricks-specific changes; no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.5** (2026-09-01) unchanged. SDK cap still
`databricks-sdk>=0.68.0,<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk v0.136.0** released **2026-09-07**. New: `w.domains` workspace
service for domain management; ML feature-engineering additions (`entity_columns`,
`timeseries_column` on `DeltaTableSource`; `filter_condition`/`inputs` on `Feature`;
`extra_parameters`/`function_type` on `Function`; `entity_column_identifiers`/
`timeseries_column_identifier` on `KafkaSource`; `cron_schedule` on `MaterializedFeature`;
`continuous` on `TimeWindow`). No breaking changes. v0.136.0 still exceeds the adapter cap;
repo stays on **0.117.0**. Next SDK gate: whenever dbt-databricks raises the cap
past v0.136.0. → [databricks.md](databricks.md)

**Repo follow-through** — no example changes warranted. v0.136.0's additions (domains service,
ML feature-engineering fields) have no dlt/dbt overlap. The Zerobus append example
(`ingestion/advanced/zerobus_append.py`) and the pending Unity Catalog Volume serverless staging
issue remain unchanged.

---

## 2026-09-04 — databricks-sdk v0.135.0 new; prior "v1.0.0" entry corrected; dlt and dbt unchanged

**dlt** — **1.30.0** (2026-08-11) unchanged. No new release since the 2026-09-03 entry; no
Databricks-specific changes; no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.5** (2026-09-01) unchanged. SDK cap still
`databricks-sdk>=0.68.0,<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk v0.135.0** released **2026-09-04**. New: `execute_command_sync()`
for `w.sandbox`; ML scheduling `mode` on `CronSchedule`; `time_window` and `full_feature_name` for
ML feature engineering. Breaking: `first_token_timeout` removed from model-service routing config;
`request_tag_key`/`request_tag_value` removed from `RateLimit`; corresponding enum value removed.
**Correction from 2026-09-03:** that entry described a "v1.0.0" release — the tag does not exist
(HTTP 404); the content matches **v0.134.0** exactly. Both v0.134.0 and v0.135.0 exceed the
adapter cap; repo stays on **0.117.0**. Next SDK gate: whenever dbt-databricks raises the cap
past v0.135.0. → [databricks.md](databricks.md)

**Repo follow-through** — no example changes warranted. v0.135.0's additions (sandbox sync
execution, ML scheduling fields) have no dlt/dbt overlap. The Zerobus append example
(`ingestion/advanced/zerobus_append.py`) and the pending Unity Catalog Volume serverless staging
issue remain unchanged.

---

## 2026-09-03 — databricks-sdk v1.0.0 first major release; dlt and dbt-databricks unchanged

**dlt** — **1.30.0** (2026-08-11) unchanged. No new release since the 2026-09-02 entry; no
Databricks-specific changes; no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.5** (2026-09-01) unchanged. SDK cap still
`databricks-sdk>=0.68.0,<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk v1.0.0** released **2026-09-03** — the first stable major
version of the Python SDK. Breaking: `TableSpec.source_table` and `SchemaSpec.source_schema`
now optional; `disabled` removed from `InferenceTableConfig`; `owner` removed from MCP/model
service types; ML feature-engineering fields pruned; `traffic_splitting` removed from
model-service routing. New: `aifunctions` and `sandbox` workspace services,
`update_deployment()`, `genie_cancel_response()`, external IAM retrieval, and GPU/RabbitMQ/
provisioned-capacity additions across Catalog/ML/Jobs. Still out of reach: dbt-databricks 1.12.5
caps `<0.118.0` — repo stays on **0.117.0**. Next SDK gate: whenever dbt-databricks raises
the cap to v1.0.0 or beyond. → [databricks.md](databricks.md)

**Repo follow-through** — no example changes warranted. v1.0.0's new AI Functions and Sandbox
services have no dlt/dbt overlap. The Zerobus append example
(`ingestion/advanced/zerobus_append.py`) and the pending Unity Catalog Volume serverless staging
issue remain unchanged.

---

## 2026-09-02 — dbt-databricks 1.12.5 patch; dlt and SDK unchanged

**dlt** — **1.30.0** (2026-08-11) unchanged. No new release; no Databricks-specific changes;
no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.5** released **2026-09-01** — patch on top of 1.12.4.
SDK cap **unchanged** (`databricks-sdk>=0.68.0,<0.118.0`); repo remains on **0.117.0**.
Key fixes: metric view backup-and-create logic replaces broken `CREATE OR REPLACE VIEW ... WITH METRICS`
path; lazy SQL-log interpolation improvement. dbt-core upper bound raised to `<1.12.4`. No impact
on this repo — no metric views used, and the SDK gate stays the same. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.133.0** (2026-08-19) unchanged. All releases above 0.117.0
still exceed the adapter's `<0.118.0` cap — repo stays on **0.117.0**. Next SDK gate: whenever
dbt-databricks raises the cap past 0.133.0. → [databricks.md](databricks.md)

**Repo follow-through** — no example changes warranted. v1.12.5's metric-view fix does not apply
(this repo's marts use standard table materializations, no metric views). The Zerobus append
example (`ingestion/advanced/zerobus_append.py`) and the pending Unity Catalog Volume serverless
staging issue remain unchanged from the 2026-08-26 entry.

---

## 2026-08-26 — SDK 0.128.0–0.133.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.30.0** (2026-08-11) unchanged. No Databricks-specific changes; no example
updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.4** (2026-08-12) unchanged. SDK cap still
`databricks-sdk<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — Six new SDK releases since the last entry: **0.128.0** (2026-08-13) through
**0.133.0** (2026-08-19). Highlights: IAM v2 account/workspace management methods (0.128.0);
paginated group-member and workspace-assignment listing on IAM v2 (0.129.0–0.130.0); LinkedIn
Ads and Marketo connector options (0.130.0); bundle deployments `create_operation()` removed
(0.131.0); App Git-source fields and ML custom UDF (0.132.0); serving telemetry feature flags
(0.133.0). All six releases exceed the `<0.118.0` adapter cap — repo stays on **0.117.0**.
Next SDK gate: whenever dbt-databricks raises the cap past 0.133.0. → [databricks.md](databricks.md)

**Repo follow-through** — dependency drift was corrected: the lock now resolves dlt 1.30.0,
dbt-databricks 1.12.4, dbt-core 1.12.0, and the adapter-compatible SDK 0.117.0. Serverless SQL
sessions keep their warehouse-managed timezone configuration, and a per-resource Zerobus append
example now bypasses the old Volume staging path while the destination-wide dlt Zerobus
reliability issue remains open.
Next SDK gate: whenever dbt-databricks raises the cap past 0.133.0.

---

## 2026-08-12 — dlt 1.30.0 + dbt-databricks 1.12.4 + SDK 0.127.0 new

**dlt** — **1.30.0** (2026-08-11) new minor. Databricks `CREATE TABLE` is now atomic:
comments on `_dlt_*` tables are no longer created by default, removing a non-atomicity hazard.
Cross-destination joins added but Databricks is not a supported query engine for joins.
`session_timezone` is now configurable on the Databricks destination. Breaking:
`auto_abort_on_terminal_error` defaults to `False`; filesystem layout separator/extension changes.
No example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.4** (2026-08-12) patch. SDK cap still
`databricks-sdk<0.118.0`; repo remains on **0.117.0**. Key fixes: SQL credential redaction
from logged SQL (security), delete+insert composite key fix (DBR < 17.1), materialized view
comment escaping. CVE fix: `databricks-sql-connector` pinned to 4.4.0, resolving 3 CVEs.
→ [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.127.0** (2026-08-12): Jobs gain `trigger_details`/`triggers`
fields; Pipelines gain connector source config options; GCP endpoint fields added; no breaking
changes. SDK 0.126.0 (2026-08-11) already logged below. Both remain out of reach under the
`<0.118.0` adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. `session_timezone`
on the Databricks destination (new in dlt 1.30.0) worth a config note if timezone-sensitive
pipelines are added. Next SDK gate: whenever dbt-databricks raises the cap past 0.127.0.

---

## 2026-08-11 — SDK 0.126.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.29.1** (2026-07-24) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.3** (2026-07-29) unchanged. SDK cap still
`databricks-sdk<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.126.0** shipped **2026-08-11** (today). Highlights: Apps
gain `forward_user_access_token`; `include_value` added to `GetSecretRequest` in Catalog; Jobs
`AiRuntimeTask` gains `docker_image_url`; `gpu_xlarge_8` workload type added in Serving.
Breaking: IAMv2 `ServicePrincipal` now requires `account_sp_status` and `display_name`; `User`
requires `account_user_status`, `full_name`, and `username`; `include_browse` and `browse_only`
removed from catalog MCP/model-provider/model-service request and response types. Still out of
reach under the `<0.118.0` adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. `catalog_database`
in v2 `catalogs.yml` (1.12.3) worth a minimal example once `dbt-core>=1.12` is adopted. Next
SDK gate: whenever dbt-databricks raises the cap past 0.126.0.

---

## 2026-08-06 — SDK 0.124.0 + 0.125.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.29.1** (2026-07-24) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.3** (2026-07-29) unchanged. SDK cap still
`databricks-sdk<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — Two new SDK releases. **databricks-sdk 0.124.0** (2026-08-04): explicit IAM
ID fields (`group_id`, `service_principal_id`, `user_id`) replace `internal_id`; credential
fields pruned from model provider configs (Amazon Bedrock, Azure OpenAI, Microsoft Foundry);
`mode` on pipeline update operations; `kinesis_stream_config` for ML streaming. Breaking: `state`
type changed from enum to string in `bundledeployments.Operation` and `bundledeployments.Resource`;
`internal_id` removed from all IAM types. **databricks-sdk 0.125.0** (2026-08-05): billing
alert/budget scope controls (`principal_overrides`, `scope_type`, `resource_type`, new `block_usage`
enum); `netsuite` connection type; `PolicyInfo.grant`; `Transformer.input_column` /
`output_column` in Pipelines; no breaking changes. Both remain out of reach under the `<0.118.0`
adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. `catalog_database`
in v2 `catalogs.yml` (1.12.3) worth a minimal example once `dbt-core>=1.12` is adopted. Next
SDK gate: whenever dbt-databricks raises the cap past 0.125.0.

---

## 2026-07-31 — SDK 0.123.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.29.1** (2026-07-24) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.3** (2026-07-29) unchanged. SDK cap still
`databricks-sdk<0.118.0`; repo remains on **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.123.0** shipped **2026-07-30** (new since yesterday's check).
Highlights: new `w.ai_gateway` workspace-level service, `update_operation()` for bundle
deployments, `patch_telemetry_config()` for serving endpoints, `dependency_mode` on compute
clusters, and `parameters` on SQL alerts. Breaking: `create_deployment()` argument order changed;
`deployment_id` removed from `CreateDeploymentRequest`; `lifetime` removed from `TimeWindow`.
Still out of reach under the `<0.118.0` adapter cap — repo stays on **0.117.0**.
→ [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. `catalog_database`
in v2 `catalogs.yml` (1.12.3) worth a minimal example once `dbt-core>=1.12` is adopted. Next
SDK gate: whenever dbt-databricks raises the cap past 0.123.0.

---

## 2026-07-30 — dbt-databricks 1.12.3 patch; dlt and SDK unchanged

**dlt** — **1.29.1** (2026-07-24) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.3** released **2026-07-29** — patch on top of 1.12.2. SDK cap
unchanged (`<0.118.0`); repo remains on **0.117.0**. Key fixes: race condition in lazy SDK init,
streaming table tag diffing, `--full-refresh` view no-op bug, non-ASCII column names in incremental
strategies, and Managed Iceberg Python model failure. New: `catalog_database` in v2 `catalogs.yml`
(requires `dbt-core>=1.12` — informational for this repo; no `catalogs.yml` exists yet).
→ [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.122.0** (2026-07-21) unchanged. Still out of reach under the
`<0.118.0` adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. `catalog_database` in
v2 `catalogs.yml` (1.12.3) worth a minimal example once `dbt-core>=1.12` is adopted. Next SDK
gate: whenever dbt-databricks raises the cap past 0.122.0.

---

## 2026-07-25 — dlt 1.29.1 patch; dbt-databricks and SDK unchanged

**dlt** — **1.29.1** (2026-07-24) new patch on top of 1.29.0. No Databricks-specific destination
changes; no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is `<0.118.0`; repo resolves
to **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.122.0** (2026-07-21) unchanged. Still out of reach under the
`<0.118.0` adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. Next SDK gate:
whenever dbt-databricks raises the cap past 0.122.0.

---

## 2026-07-22 — SDK 0.122.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.29.0** (2026-07-13) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is `<0.118.0`; repo resolves
to **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.122.0** shipped **2026-07-21** (new since 2026-07-18 check).
Highlights: clean room task-run listing, Postgres CDF config methods (6 new), pipeline connectors
for Reddit/Google Ads/TikTok, Jobs performance-target field, Azure capacity reservation for
instance pools. Breaking: `internal_id` type changed to string on Group/ServicePrincipal/User;
`AiRuntimeTask.code_source_path` removed; `TimeWindow.long_rolling` removed. Still out of reach
under the `<0.118.0` adapter cap — repo stays on **0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. Next SDK gate:
whenever dbt-databricks raises the cap past 0.122.0.

---

## 2026-07-18 — SDK 0.121.0 new; dlt and dbt-databricks unchanged

**dlt** — **1.29.0** (2026-07-13) unchanged. No Databricks-specific changes; no example updates
needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is `<0.118.0`; repo resolves
to **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.121.0** shipped **2026-07-17** (new since 2026-07-15 check).
Highlights: workspace-level grants methods added; API enhancements across jobs, ML, and serving
services. Breaking changes: `include_browse` removed from secret operations; several ML aggregation
function fields removed. Still out of reach under the `<0.118.0` adapter cap — repo stays on
**0.117.0**. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. Next SDK gate: whenever
dbt-databricks raises the cap past 0.121.0.

---

## 2026-07-15 — dlt 1.29.0 new minor; dbt-databricks and SDK unchanged

**dlt** — **1.29.0** released **2026-07-13** (first minor since 1.28.x). No Databricks-specific
changes. New cross-tool features: ClickHouse staging-optimized replace, AWS Secret Manager
provider, explicit `Relation.join()` API with cross-destination `can_join_with` rules, and an
Arrow type-promotion flush-batch fix. No example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is `<0.118.0`; repo
resolves to **0.117.0**. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** (2026-07-02) unchanged. Under the `<0.118.0` cap,
**0.117.0** remains the highest reachable version. → [databricks.md](databricks.md)

**Watch / opportunities** — dlt 1.29.0's `Relation.join()` + `physical_location()` accessor is
worth watching as a future cross-schema Unity Catalog query example. Zerobus ingestion example
still a candidate once the Unity Catalog Volume serverless staging issue (`Connection refused`) is
resolved upstream. Next SDK gate: whenever dbt-databricks raises the cap past 0.120.0.

---

## 2026-07-14 — dlt 1.29.0 minor release; dbt-databricks and SDK unchanged

**dlt** — **1.29.0** released **2026-07-13**. No Databricks-specific changes. New in other
destinations/capabilities: ClickHouse atomic-swap replace (`staging-optimized` strategy), AWS
Secret Manager config provider, Relations API explicit joins (`Relation.join()`) with
`physical_location()` and cross-destination `can_join_with` compatibility checks, BigQuery
atomic replace (opt-in), DuckDB as SQLAlchemy destination, configurable Parquet compression.
No example updates needed for this repo. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is `<0.118.0`; repo
resolves to 0.117.0. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** (2026-07-02) unchanged. Under the `<0.118.0` cap,
0.117.0 remains the highest reachable version. SDP / platform release notes returned HTTP 403
again this run — no new Lakeflow/SDP entries confirmed. → [databricks.md](databricks.md)

**Watch / opportunities** — Relations API `Relation.join()` (dlt 1.29.0) is a future candidate
for a cross-pipeline dataset-join example; needs design thought on cross-destination semantics
before implementing. Zerobus ingestion example still a candidate once the Unity Catalog Volume
serverless staging issue (`Connection refused`) is resolved upstream. Next SDK gate: whenever
dbt-databricks raises the cap past 0.120.0.

---

## 2026-07-11 — dlt 1.28.2 maintenance patch; dbt-databricks and SDK tip unchanged

**dlt** — **1.28.2** released **2026-07-10** (missed in yesterday's radar). Maintenance only:
loosens the `dlthub-client` upper-version cap so the 1.28.x branch can work with future client
releases without a new dlt minor. No Databricks-specific changes; no example updates needed.
→ [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** (2026-07-09) unchanged. SDK cap is now `<0.118.0`; repo
resolves to 0.117.0 after upgrading. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** (2026-07-02) unchanged. Under the `<0.118.0` cap,
0.117.0 remains the highest reachable version. SDP / platform release notes returned HTTP 403
again this run — no new Lakeflow/SDP entries confirmed. → [databricks.md](databricks.md)

**Watch / opportunities** — Zerobus ingestion example still a candidate once the Unity Catalog
Volume serverless staging issue (`Connection refused`) is resolved upstream. Next SDK gate:
whenever dbt-databricks raises the cap past 0.120.0 to reach the 0.120.0 tip.

---

## 2026-07-10 — dbt-databricks 1.12.2 unlocks SDK to 0.117.0; dlt and SDK tip unchanged

**dlt** — **1.28.1** still latest (no change since 2026-06-19). No Databricks-specific fixes or example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** released **2026-07-09** — the gating release. Adapter's `databricks-sdk` upper cap raised from `<0.105.0` → `<0.118.0`. After upgrading and re-locking, the repo environment moves from SDK **0.104.0 → 0.117.0** (the highest version satisfying the new cap). Also ships: `skip_optimize` model config, Rust kernel backend (`use_kernel: true`), catalogs.yml v2, Spark Connect WorkspaceClient fix, and a constraint-drop bugfix for incremental runs. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** (2026-07-02) is still the latest release. Under the new `<0.118.0` cap, 0.117.0 is the highest reachable version — 3 minor releases below the tip. SDP / platform release notes returned HTTP 403 again this run. → [databricks.md](databricks.md)

**Watch / opportunities** — Upgrade path is now open: `uv sync` against dbt-databricks 1.12.2 resolves SDK to 0.117.0. Zerobus ingestion path still a candidate example once the Unity Catalog Volume serverless staging issue (`Connection refused`) is resolved upstream. Next gate: whenever dbt-databricks raises the cap past 0.120.0 to reach the current SDK tip.

---

## 2026-07-03 — SDK 0.120.0 released; dlt and dbt-databricks unchanged

**dlt** — **1.28.1** still latest (no change since 2026-06-19). No Databricks-specific fixes or example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.1** (2026-06-10) still latest. SDK cap (`databricks-sdk<0.105.0`) unchanged — this remains the gate on every SDK upgrade. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** shipped **2026-07-02**. Key additions: `sql_condition` job triggers, `full_name` for IAM User (breaking: `name` field removed), Genie visualization APIs, `telemetry_config` for serving endpoints, PostgreSQL service extensions. Still out of reach for this repo: adapter pins `<0.105.0`, environment stays on **0.104.0**. SDP / platform release notes returned HTTP 403 again — no new Lakeflow entries confirmed. → [databricks.md](databricks.md)

**Watch / opportunities** — dbt-databricks release remains the gate on every SDK upgrade. Zerobus ingestion path (dlt 1.27+) still a candidate for a focused example once the Unity Catalog Volume serverless staging issue (`Connection refused`) is resolved upstream.

---

## 2026-06-25 — SDK 0.119.0 new; dlt FK bug fixed in data_contracts.py example

**dlt** — **1.28.1** still latest (no new release). Retroactive finding from 1.28.0 (PR #4011,
missed in prior checks): the Databricks destination now emits FK constraints **only when
`create_indexes=True`** (default is `False`). The `ingestion/advanced/data_contracts.py` example
was silently skipping the FK it described — fixed by switching to an explicit
`dlt.destinations.databricks(create_indexes=True)` call. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.1** (2026-06-10) unchanged. Adapter cap
(`databricks-sdk<0.105.0`) still holds. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.119.0** shipped **2026-06-24** (new since 2026-06-20 check).
Still out of reach: adapter pins `<0.105.0`, repo stays on **0.104.0**. SDP / platform release
notes returned HTTP 403 this run — no new Lakeflow entries confirmed. → [databricks.md](databricks.md)

**Watch / opportunities** — dbt-databricks release remains the gate on every SDK upgrade. Zerobus
ingestion path (dlt 1.27+) still candidate for a focused example once the serverless staging issue
(`Connection refused` to Unity Catalog Volume) is resolved upstream.

---

## 2026-06-20 — release-check refresh: dlt 1.28.1 patch; dbt and SDK unchanged

**dlt** — **1.28.1** released **2026-06-19** (patch on 1.28.0). Changes are housekeeping: Python 3.9
dropped (irrelevant — this repo requires ≥3.12), a dataset-browser UX tweak, connectorx temporal
precision fix, ISO week cursor fix, and a PostgreSQL NULL-char cleanup. No Databricks-specific
changes; no example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.1** (2026-06-10) remains latest. No change.
Adapter cap (`databricks-sdk<0.105.0`) still holds. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.118.0** (2026-06-18) remains latest. No change. The repo stays on
**0.104.0** because of the adapter pin. Databricks and dbt platform blogs were unreachable (403)
during this run; no new SDP/platform notes confirmed. → [databricks.md](databricks.md)

**Watch / opportunities** — dbt-databricks release remains the gate on every SDK upgrade. dlt 1.28.x
Databricks staging issue (Volume + serverless `Connection refused`) still open; retest on 1.28.1
refreshable-credentials fix before filing upstream.

---

## 2026-06-18 — release-check refresh: only the Databricks SDK moved

**dlt** — **1.28.0** (2026-06-15) is still latest; no change for the repo. Two Databricks-relevant
details surfaced on a closer read: 1.28.0's *refreshable* default credentials may mitigate
`ExpiredToken`-class staging failures (retest before filing upstream), and 1.27.0's **Zerobus** insert
API (`databricks_adapter`) is an alternative to the current Spark landing fallback. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.1** (2026-06-10) is still latest. Flag for this repo: 1.12.1 made
column-level constraints require `contract.enforced: true` explicitly. Runtime correlation IDs
(`job_id`/`job_run_id`/`task_run_id`) pair well with the task run-output CLI pattern. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.118.0** shipped **today (2026-06-18)**; 0.117.0 landed 2026-06-11.
Both remain out of reach: `dbt-databricks 1.12.1` pins `databricks-sdk<0.105.0`, so the repo stays on
**0.104.0** until the adapter relaxes the cap. No new SDP/platform notes since 2026-06-17.
→ [databricks.md](databricks.md)

**Watch / opportunities** — track dbt-databricks releases for the SDK cap bump (the gate on every SDK
update); retest the dlt Databricks staging failure on 1.28.0's refreshable creds before opening the
upstream issue.

---

## 2026-06-17 — live Databricks bundle run green + upstream findings

**Outcome** — the dev Databricks Asset Bundle now runs end-to-end successfully: Spark Python ingest
lands `workspace.raw.rest_posts` and `workspace.raw.rest_comments`, then the Databricks dbt task
builds the analytics models. → [databricks.md](databricks.md)

**dlt** — live serverless testing exposed two upstream-worthy issues: Databricks' built-in Delta Live
Tables import hook can collide with dlthub `dlt`, and dlt's Databricks destination failed during
Unity Catalog Volume staging to `_dlt_staging_load_volume`. The repo uses a Spark landing fallback
for the serverless demo while preserving the dlt path. → [dlt.md](dlt.md)

**dbt** — dbt task logs made the remaining failures straightforward: the fallback loader had to match
dlt's raw contract (`user_id`, `post_id`, `_dlt_load_id`) before staging models and incremental marts
could build. → [dbt.md](dbt.md)

**Codex workflow** — added a personal `databricks-cli-debug` skill to make future Databricks CLI
log triage repeatable, including parent-run/task-run handling and upstream evidence capture.

**Watch / opportunities** — prepare sanitized upstream issues/docs PRs for dlt Databricks serverless
staging, dlt/DLT import-hook collision, Databricks CLI run-output docs, and dbt raw-contract examples.

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
