"""Advanced: incremental loading with `merge` (upsert / CDC-style).

Shows how dlt turns a stream of changing records into an idempotent upsert on Databricks:
  - `write_disposition="merge"` + `primary_key` → MERGE INTO on the destination table
  - `dlt.sources.incremental` → only emit rows whose cursor advanced since the last run
  - rerunning with overlapping data updates rows in place instead of duplicating them

The source here is a tiny in-memory generator so the example is fully self-contained; swap it
for any real resource (DB, API) and the destination behavior is identical.

Run twice to see the merge in action:
    uv run python ingestion/advanced/merge_incremental.py
    uv run python ingestion/advanced/merge_incremental.py   # second run upserts, no duplicates
"""

from __future__ import annotations

import inspect
import sys
from datetime import UTC, datetime
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

import dlt  # noqa: E402
from _common import databricks_pipeline  # noqa: E402


@dlt.resource(
    name="customers",
    write_disposition="merge",
    primary_key="id",
)
def customers(
    # dlt's idiom requires the incremental cursor as a default arg (B008 is a false positive here).
    updated_at=dlt.sources.incremental("updated_at", initial_value="2026-01-01T00:00:00Z"),  # noqa: B008
):
    """Yield customers. `incremental` filters to rows newer than the last stored cursor."""
    now = datetime.now(UTC).isoformat()
    # In a real source these rows come from a DB/API query bounded by `updated_at.last_value`.
    yield from [
        {"id": 1, "name": "Ada Lovelace", "tier": "gold", "updated_at": now},
        {"id": 2, "name": "Alan Turing", "tier": "silver", "updated_at": now},
        {"id": 3, "name": "Grace Hopper", "tier": "gold", "updated_at": now},
    ]


def main() -> None:
    pipeline = databricks_pipeline("merge_demo")
    load_info = pipeline.run(customers())
    print(load_info)


if __name__ == "__main__":
    main()
