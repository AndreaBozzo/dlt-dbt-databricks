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
   [`radar.md`](radar.md).
3. Reviews `ingestion/` and `transformation/` to decide if any finding warrants a new/improved example
   (conservatively — infra-heavy ideas are logged as proposals, not built blind).
4. **Delivers via PR** from a `radar/auto-YYYY-MM-DD` branch. It never pushes to `main` directly.

> **Silence = no news, not a failure.** On days when no release moved, the run makes **no commit and
> opens no PR** (by design, to avoid noise). So "no PR today" and "the routine is broken" look identical
> from the repo alone — the only proof-of-life is the green run in the routine's
> [run history](https://claude.ai/code/routines/trig_01TA23trUmtuLtCPrtATMXM8).

**Managing it**

- Created/edited through the `/schedule` skill in Claude Code (it calls the routines API under the hood).
- Enable / disable / **Run now** (to force an immediate check) from the routine page linked above.
- The API can't delete routines — remove it at <https://claude.ai/code/routines> if ever needed.

## How to refresh on demand

To refresh outside the daily run, ask me: **"refresh the update radar"** (or scope it: "refresh the dlt
updates"). Same three steps as above (fetch → append dated entry → update [`radar.md`](radar.md)), applied
to your local checkout.

Each entry is dated and sourced so the file stays an auditable timeline rather than a vague blob.

## Why this exists

Per the project goal, this repo isn't just examples — it tracks the moving target of these tools so the
examples stay current. Notable friction or gaps found while researching are also logged here as
candidate **upstream contributions** (issues / PRs / example submissions).
