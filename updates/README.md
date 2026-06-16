# Update radar

A manual, on-demand knowledge base tracking what's new and notable across the three tools this repo
builds on: **dlt (dlthub)**, **dbt / dbt-databricks**, and **Databricks** (Lakeflow, Unity Catalog).

## Files

| File | Contents |
| --- | --- |
| [`radar.md`](radar.md) | Rolling, dated top-of-mind summary across all three tools — read this first |
| [`dlt.md`](dlt.md) | dlthub release / feature notes |
| [`dbt.md`](dbt.md) | dbt + dbt-databricks notes (incl. Fusion) |
| [`databricks.md`](databricks.md) | Databricks / Lakeflow SDP / Unity Catalog notes |
| [`sources.md`](sources.md) | Canonical release-note URLs to monitor |

## How to refresh

Ask me: **"refresh the update radar"** (or scope it: "refresh the dlt updates"). I will:

1. Web-fetch the canonical URLs in [`sources.md`](sources.md).
2. Append a new **dated** entry to the relevant per-tool file, with a one-line source link each.
3. Update the summary at the top of [`radar.md`](radar.md).

Each entry is dated and sourced so the file stays an auditable timeline rather than a vague blob.

## Why this exists

Per the project goal, this repo isn't just examples — it tracks the moving target of these tools so the
examples stay current. Notable friction or gaps found while researching are also logged here as
candidate **upstream contributions** (issues / PRs / example submissions).
