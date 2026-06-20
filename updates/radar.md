# Radar — top of mind

Rolling cross-tool summary. Newest snapshot on top. Details live in the per-tool files.

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
