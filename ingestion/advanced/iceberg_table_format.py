"""Advanced: write Apache Iceberg tables on Unity Catalog (instead of Delta).

The Databricks destination defaults to Delta. Setting `table_format="iceberg"` makes dlt create the
destination tables as Unity Catalog–managed Iceberg tables — useful when other engines in your stack
read Iceberg, or you want UC's Iceberg interoperability (UniForm-style).

Notes / prerequisites:
  - Your workspace/catalog must allow managed Iceberg tables (recent UC + DBR).
  - Set the format at the destination level so every table in the load uses it.

Run:  uv run python ingestion/advanced/iceberg_table_format.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

import dlt  # noqa: E402
from _common import DATASET_NAME  # noqa: E402


@dlt.resource(name="iceberg_events", write_disposition="append")
def events():
    yield from [
        {"event_id": 1, "kind": "click", "value": 0.5},
        {"event_id": 2, "kind": "view", "value": 1.0},
        {"event_id": 3, "kind": "purchase", "value": 42.0},
    ]


def main() -> None:
    # Configure the destination explicitly so we can pass table_format="iceberg".
    destination = dlt.destinations.databricks(table_format="iceberg")
    pipeline = dlt.pipeline(
        pipeline_name="iceberg_demo",
        destination=destination,
        dataset_name=DATASET_NAME,
        progress="log",
    )
    load_info = pipeline.run(events())
    print(load_info)


if __name__ == "__main__":
    main()
