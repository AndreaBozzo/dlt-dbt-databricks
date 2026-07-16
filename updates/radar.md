# Radar — top of mind

Rolling cross-tool summary. Newest snapshot on top. Details live in the per-tool files.

---

## 2026-07-16 — dbt-databricks 1.12.2 lifts SDK gate; dlt 1.29.0 out; SDK unchanged

**dlt** — **1.29.0** released **2026-07-13** (up from 1.28.1). No Databricks-specific changes —
new features are ClickHouse atomic swap, AWS Secret Manager config provider, explicit Relation
joins, and Parquet codec config. No example updates needed. → [dlt.md](dlt.md)

**dbt** — **dbt-databricks 1.12.2** shipped **2026-07-09**. The headline change: **databricks-sdk
cap raised from `<0.105.0` to `<0.118.0`** — the first SDK gate lift since the adapter has been at
1.12.x. With 1.12.2 installed, `uv lock` will resolve databricks-sdk to **0.117.x** (currently
0.104.0 in this repo's lockfile). Additional features: `skip_optimize` model config, Rust kernel
backend support, catalogs.yml v2. → [dbt.md](dbt.md)

**Databricks** — **databricks-sdk 0.120.0** (2026-07-02) remains latest — no new release since
last check. With dbt-databricks 1.12.2 the repo can now reach **0.117.x**; 0.118.0–0.120.0 remain
out of reach until the adapter cap advances past 0.118.0. SDP / platform release notes returned
HTTP 403 again — no new Lakeflow entries confirmed. → [databricks.md](databricks.md)

**Watch / action items** — Run `uv lock` to upgrade this repo from dbt-databricks 1.12.1 →
1.12.2 and databricks-sdk 0.104.0 → 0.117.x. The `iamv2.User.name` breaking change (0.120.0) is
above the new cap and won't be picked up. No example code changes needed from this cycle.

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
