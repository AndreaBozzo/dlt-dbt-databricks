"""Mirror complete customer snapshots, including deletions, with dlt's CDC merge strategy.

Each batch must contain the entire source table with unique primary keys. Do not apply an
incremental cursor: records missing from a snapshot are deleted from the destination.
Unchanged rows retain their _dlt_load_id, so that column dates the last change, not the last
successful ingestion. Use load metadata for ingestion freshness when enabling change skipping.

The example loads two snapshots into raw.cdc_customers, separately from merge_incremental.py's
customers table. The second snapshot updates Ada, removes Alan, keeps Grace and adds Katherine.
It runs on Databricks or DuckDB with dlt >= 1.31; this project validates dlt 1.32.

Run: uv run python ingestion/advanced/cdc_merge.py
     DLT_DESTINATION=duckdb uv run python ingestion/advanced/cdc_merge.py
"""

from __future__ import annotations

import inspect
import sys
from collections.abc import Sequence
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))

from _common import demo_pipeline, dlt  # noqa: E402


@dlt.resource(
    name="cdc_customers",
    primary_key="id",
    write_disposition={
        "disposition": "merge",
        "strategy": "cdc",
        "skip_unchanged_rows": True,
    },
)
def customers_snapshot(rows: Sequence[dict[str, object]]):
    """Yield a complete snapshot; an explicitly empty snapshot clears the destination."""
    # An empty generator creates no load job, which would leave the old rows untouched.
    # Only call this with a verified complete snapshot, including a verified empty one.
    if not rows:
        yield dlt.mark.materialize_table_schema()
    yield from rows


def main() -> None:
    pipeline = demo_pipeline("cdc_merge_demo")
    snapshots = [
        [
            {"id": 1, "name": "Ada Lovelace", "tier": "silver"},
            {"id": 2, "name": "Alan Turing", "tier": "silver"},
            {"id": 3, "name": "Grace Hopper", "tier": "gold"},
        ],
        [
            {"id": 1, "name": "Ada Lovelace", "tier": "gold"},
            {"id": 3, "name": "Grace Hopper", "tier": "gold"},
            {"id": 4, "name": "Katherine Johnson", "tier": "silver"},
        ],
    ]
    for index, rows in enumerate(snapshots, start=1):
        print(pipeline.run(customers_snapshot(rows)))
        with pipeline.sql_client() as client:
            table = client.make_qualified_table_name("cdc_customers")
            current = client.execute_sql(f"SELECT id, name, tier FROM {table} ORDER BY id")
        print(f"Snapshot {index}: {current}")


if __name__ == "__main__":
    main()
