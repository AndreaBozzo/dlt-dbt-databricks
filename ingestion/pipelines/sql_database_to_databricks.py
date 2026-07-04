"""SQL database → Databricks (Unity Catalog, Delta), incrementally — runs out of the box.

Replicates a Postgres table into the lakehouse with a **custom dlt resource that issues a plain SQL
query** (no schema reflection). dlt infers the table schema from the yielded rows. This pattern:
  - works against ANY Postgres — including locked-down read replicas where dlt's high-level
    `sql_database` source can't run because the user is denied schema reflection (a real gotcha;
    e.g. the public RNAcentral reader blocks `pg_collation`);
  - demonstrates `dlt.sources.incremental` (only fetch rows past the stored cursor) + `merge`
    (idempotent upsert on the primary key);
  - is exactly how you'd replicate an operational Allianz-style DB (policies, claims, customers).

Default source (in .env.example): EBI's **public read-only** RNAcentral Postgres. We replicate
`rnacen.rnc_database` — a 56-row reference table with an `id` PK and a `timestamp` cursor — so it's
fast and runs with zero setup. Swap the connection string + query for your own table.

Prereqs:  uv sync --extra postgres   (psycopg2 driver)
Run:      uv run python ingestion/pipelines/sql_database_to_databricks.py   (rerun → no-op)
"""

from __future__ import annotations

import inspect
import os
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

import dlt  # noqa: E402
from _common import demo_pipeline  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

# A real source table: which databases RNAcentral imports from. Swap for your own.
SOURCE_QUERY = """
    SELECT id, timestamp, descr, current_release, alive
    FROM rnacen.rnc_database
    {where}
    ORDER BY timestamp
"""


@dlt.resource(name="rnc_database", primary_key="id", write_disposition="merge")
def rnc_database(
    # dlt's idiom requires the incremental cursor as a default arg (B008 is a false positive here).
    cursor=dlt.sources.incremental("timestamp", initial_value=datetime(1970, 1, 1)),  # noqa: B008
):
    """Stream rows newer than the stored cursor via a direct SQL query (no reflection)."""
    dsn = os.environ["SOURCES__SQL_DATABASE__CREDENTIALS"]
    engine = create_engine(dsn)
    # Pre-filter in SQL using the last cursor value — the efficient, real-world incremental pattern.
    where = "WHERE timestamp > :last" if cursor.last_value else ""
    query = text(SOURCE_QUERY.format(where=where))
    with engine.connect() as conn:
        result = conn.execution_options(stream_results=True).execute(
            query, {"last": cursor.last_value} if cursor.last_value else {}
        )
        for row in result.mappings():
            yield dict(row)
    engine.dispose()


def main() -> None:
    pipeline = demo_pipeline("sql_database_demo")
    load_info = pipeline.run(rnc_database())
    print(load_info)


if __name__ == "__main__":
    main()
