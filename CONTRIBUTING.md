# Contributing

Thanks for your interest! This repo is a living collection of **advanced, runnable** dlt + dbt +
Databricks examples and an update radar. Contributions that add real, working examples or keep the
radar current are very welcome.

## Setup

```bash
uv sync --extra postgres            # env + deps (postgres extra for the SQL example)
cd transformation/dbt_databricks && uv run dbt deps && cd ../..
databricks auth login --host https://YOUR_HOST.cloud.databricks.com   # OAuth for dbt
cp .env.example .env                # fill in Databricks host/http_path/PAT for dlt
cp transformation/dbt_databricks/profiles.yml.example transformation/dbt_databricks/profiles.yml
```

See [docs/setup-databricks.md](docs/setup-databricks.md) for the full workspace setup.

## Standards

- **Python**: formatted & linted with `ruff` (`make lint`, `make fmt`). Keep examples self-contained
  and heavily commented — they double as teaching material.
- **dbt**: models must `dbt parse` cleanly; add tests for new models. Prefer `staging → intermediate
  → marts` layering and reference the dlt-loaded `raw` schema via `source()`.
- **Examples must actually run.** If an example can't run out of the box, either make it runnable
  (use a public source) or clearly mark it and explain why — don't ship dead demos.
- **No secrets.** See [SECURITY.md](SECURITY.md).

## Before opening a PR

```bash
make lint                                    # ruff
make dbt-parse                               # dbt compiles
databricks bundle validate                   # DAB still valid
```

## Upstream first

If you hit a bug, doc gap, or rough edge in **dlt**, **dbt-databricks**, or **Databricks** itself
while working here, consider reporting/fixing it upstream too — and log the finding in
[`updates/`](updates/). That's a core goal of this project.
