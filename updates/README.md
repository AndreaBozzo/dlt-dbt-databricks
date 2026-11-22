# Update radar

A knowledge base tracking what's new and notable across the three tools this repo
builds on: **dlt (dlthub)**, **dbt / dbt-databricks**, and **Databricks** (Lakeflow, Unity Catalog).
It refreshes two ways: **automatically every day** via a cloud routine (see below), and **on demand**
when you ask.

## Files

| File | Contents |
| --- | --- |
| [`radar.md`](radar.md) | Rolling, dated top-of-mind summary across all three tools — read this first |
| [`dlt.md`](dlt.md) | dlthub release / feature notes |
| [`dbt.md`](dbt.md) | dbt + dbt-databricks notes (incl. Fusion) |
| [`databricks.md`](databricks.md) | Databricks / Lakeflow SDP / Unity Catalog notes |
| [`sources.md`](sources.md) | Canonical release-note URLs to monitor |
| [`adoption.toml`](adoption.toml) | Evidence record: available releases, adopted versions, and the claims the entries rely on |

## Automated daily refresh (cloud routine)

A scheduled **Claude Code cloud routine** refreshes this radar every day — no local machine needed.

| Property | Value |
| --- | --- |
| Name | `Update radar — daily refresh + examples check` |
| Routine ID | `trig_01TA23trUmtuLtCPrtATMXM8` |
| Schedule | `0 6 * * *` — daily **06:00 UTC** (= **08:00 Europe/Rome**) |
| Model | `claude-sonnet-4-6` |
| Where it runs | Anthropic cloud, on a fresh checkout of this repo (no access to your laptop) |
| Manage / run history | <https://claude.ai/code/routines/trig_01TA23trUmtuLtCPrtATMXM8> |

**What each run does**

1. Web-fetches the canonical URLs in [`sources.md`](sources.md) and finds the current latest release of
   dlt, dbt-databricks, and databricks-sdk (plus notable Databricks / dbt news).
2. Appends a new **dated, sourced** entry to any per-tool file that changed, and a snapshot to
   [`radar.md`](radar.md). A newer release goes into the `observed` block of
   [`adoption.toml`](adoption.toml) only (see [Available versus adopted](#available-versus-adopted)).
3. Reviews `ingestion/` and `transformation/` to decide if any finding warrants a new/improved example
   (conservatively — infra-heavy ideas are logged as proposals, not built blind).
4. Runs `make radar-check` (or `uv run --frozen python orchestration/check_radar.py`) and fixes the
   entries until it passes. The check only reads files; it never upgrades a dependency.
5. **Delivers via PR** from a `radar/auto-YYYY-MM-DD` branch. It never pushes to `main` directly.

The routine's prompt lives in the routine settings linked above, not in this repository. It must tell
the run to follow this section and the rules below.

> **Silence = no news, not a failure.** On days when no release moved, the run makes **no commit and
> opens no PR** (by design, to avoid noise). So "no PR today" and "the routine is broken" look identical
> from the repo alone — the only proof-of-life is the green run in the routine's
> [run history](https://claude.ai/code/routines/trig_01TA23trUmtuLtCPrtATMXM8).

**Managing it**

- Created/edited through the `/schedule` skill in Claude Code (it calls the routines API under the hood).
- Enable / disable / **Run now** (to force an immediate check) from the routine page linked above.
- The API can't delete routines — remove it at <https://claude.ai/code/routines> if ever needed.

## Available versus adopted

A new upstream release is not an adopted one. [`adoption.toml`](adoption.toml) keeps the two apart for
dlt, dbt-databricks and databricks-sdk, and `orchestration/check_radar.py` compares it with the repo.

| Block | Meaning | Who edits it |
| --- | --- | --- |
| `[dependency.observed]` | Newest upstream release the radar saw: version, release date, first-seen date, source link | The radar refresh |
| `[dependency.adopted]` | Version in `uv.lock`, adoption date, link to the change, links to the validation that exercised it | Only the change that edits `uv.lock` |
| `[[claim]]` | A statement an entry relies on, checked against the repo | Whoever writes the entry |

Rules for a refresh:

- Write "available" for the `observed` version and "adopted" for the `adopted` one. A radar entry never
  says "adopted" for a version that `uv.lock` does not hold.
- Do not edit `pyproject.toml`, `databricks.yml` or `uv.lock`, and do not run `uv lock`, `uv add` or
  `uv sync --upgrade`. Adoption is a separate change with its own validation.
- When `observed` is newer than `adopted`, `adoption_note` says why it is not adopted.
- An entry that says a dependency floor is already met needs a `floor_met` claim. The check compares
  it with `uv.lock`.
- An entry that argues from how models are materialized (for example "staging models are views, so this
  view change applies") needs a `materialization` claim. It lists the models and cites the file that
  decides each one, either `dbt_project.yml` or the model's own `config()`; the check resolves the
  effective setting from the dbt project, properties files and model overrides, without running dbt.
- `adopted.validation` lists links to the run, PR or CI job that exercised the adoption. If none exists,
  leave it empty and explain in `validation_note`. Do not invent a link.

The check needs `uv` and the locked environment (`uv run --frozen` syncs it from `uv.lock` and never
changes the lockfile). Its only third-party import is PyYAML, which dbt already installs.

## How to refresh on demand

To refresh outside the daily run, ask me: **"refresh the update radar"** (or scope it: "refresh the dlt
updates"). Same steps as above (fetch → append dated entry → update [`radar.md`](radar.md) and the
`observed` record → `make radar-check`), applied to your local checkout.

Each entry is dated and sourced so the file stays an auditable timeline rather than a vague blob.

## Why this exists

Per the project goal, this repo isn't just examples — it tracks the moving target of these tools so the
examples stay current. Notable friction or gaps found while researching are also logged here as
candidate **upstream contributions** (issues / PRs / example submissions).
