"""Advanced: schema contracts + primary/foreign-key hints.

Two governance features that matter when raw data feeds a modeled warehouse:

1. **Schema contracts** — control what happens when the source drifts. Here we `freeze` columns
   (reject new/unexpected columns by raising), while still allowing new tables. Options per entity
   (`tables`, `columns`, `data_type`) are: "evolve" | "freeze" | "discard_row" | "discard_value".

2. **Key hints** — `primary_key` and `references` (foreign keys). The Databricks destination emits
   PRIMARY KEY / FOREIGN KEY constraints on the created tables, which document the model and help
   downstream tools (and dbt tests) reason about relationships. Note: since dlt 1.28.0 these
   constraints are only emitted when the destination is configured with `create_indexes=True`
   (the default is `False`) — see `main()` below.

The `freeze` contract makes this example *intentionally* fail if you add an unexpected column to the
data below — that's the contract doing its job.

Run:  uv run python ingestion/advanced/data_contracts.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

import dlt  # noqa: E402
from _common import DATASET_NAME  # noqa: E402


@dlt.resource(name="dim_product", primary_key="product_id", write_disposition="merge")
def products():
    yield from [
        {"product_id": 100, "name": "Keyboard", "price": 49.0},
        {"product_id": 101, "name": "Mouse", "price": 25.0},
    ]


@dlt.resource(
    name="fact_sale",
    primary_key="sale_id",
    write_disposition="merge",
    # Foreign key → dim_product.product_id, surfaced as a constraint on Databricks.
    references=[
        {
            "referenced_table": "dim_product",
            "columns": ["product_id"],
            "referenced_columns": ["product_id"],
        }
    ],
)
def sales():
    yield from [
        {"sale_id": 1, "product_id": 100, "qty": 2},
        {"sale_id": 2, "product_id": 101, "qty": 5},
    ]


@dlt.source
def catalog_source():
    return [products(), sales()]


def main() -> None:
    # create_indexes=True is required (since dlt 1.28.0) for FK constraints to be emitted.
    # Without it, references= hints are silently ignored on the Databricks destination.
    destination = dlt.destinations.databricks(create_indexes=True)
    pipeline = dlt.pipeline(
        pipeline_name="contracts_demo",
        destination=destination,
        dataset_name=DATASET_NAME,
        progress="log",
    )
    # Freeze columns: reject unexpected columns; allow brand-new tables to be created.
    load_info = pipeline.run(
        catalog_source(),
        schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"},
    )
    print(load_info)


if __name__ == "__main__":
    main()
