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

import pyarrow as pa

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))

from _common import demo_pipeline, dlt  # noqa: E402


@dlt.resource(
    name="cdc_customers",
    primary_key="id",
    # An empty first snapshot has no values from which dlt can infer these types.
    columns={
        "id": {"data_type": "bigint"},
        "name": {"data_type": "text"},
        "tier": {"data_type": "text"},
        # Empty Arrow batches need the bookkeeping schema before the first JSON batch.
        "_dlt_load_id": {"data_type": "text", "nullable": False},
        "_dlt_id": {"data_type": "text", "nullable": False, "unique": True},
    },
    write_disposition={
        "disposition": "merge",
        "strategy": "cdc",
        "skip_unchanged_rows": True,
    },
)
def customers_snapshot(rows: Sequence[dict[str, object]]):
    """Yield a complete snapshot; an explicitly empty snapshot clears the destination."""
    # An empty generator creates no load job. A typed Arrow batch materializes an empty
    # table even on the first load, avoiding dlt 1.32's JSON empty-row primary-key hashing.
    # Only call this with a verified complete snapshot, including a verified empty one.
    if not rows:
        yield pa.table(
            {
                "id": pa.array([], type=pa.int64()),
                "name": pa.array([], type=pa.string()),
                "tier": pa.array([], type=pa.string()),
                "_dlt_load_id": pa.array([], type=pa.string()),
                "_dlt_id": pa.array([], type=pa.string()),
            }
        )
    else:
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
