"""SQL database → Databricks (Unity Catalog, Delta), incrementally.

Demonstrates dlt's `sql_database` source with incremental extraction: only rows whose cursor
column (`updated_at`) advanced since the last run are pulled, and merged into the destination on
the primary key. This is the typical "replicate an operational DB into the lakehouse" pattern.

Configure the source connection string via env var (see .env.example):
    SOURCES__SQL_DATABASE__CREDENTIALS=postgresql://user:pass@host:5432/dbname
A driver is needed — install the optional extra:  uv sync --extra postgres

Run:  uv run python ingestion/pipelines/sql_database_to_databricks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make ingestion/_common importable

import dlt  # noqa: E402
from _common import databricks_pipeline  # noqa: E402
from dlt.sources.sql_database import sql_database  # noqa: E402

# Edit to match your source schema. Keep the list small to start.
TABLES = ["customers", "orders"]
CURSOR_COLUMN = "updated_at"


def build_source():
    source = sql_database().with_resources(*TABLES)
    # Apply an incremental cursor to each selected resource so reruns only fetch new/changed rows.
    for table in TABLES:
        source.resources[table].apply_hints(
            incremental=dlt.sources.incremental(CURSOR_COLUMN),
            write_disposition="merge",
            primary_key="id",
        )
    return source


def main() -> None:
    pipeline = databricks_pipeline("sql_database_demo")
    load_info = pipeline.run(build_source())
    print(load_info)


if __name__ == "__main__":
    main()
