"""REST API → Databricks (Unity Catalog, Delta).

Demonstrates dlt's declarative `rest_api` source: paginated extraction, a parent→child
relationship (`posts` → `comments`), and merge loading — landed as Delta tables in the `raw`
schema that the dbt project reads from.

Source: https://jsonplaceholder.typicode.com (public, no auth) so the example runs out of the box.

Run:  uv run python ingestion/pipelines/rest_api_to_databricks.py
"""

from __future__ import annotations

import argparse
import inspect
import os
import sys
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

from _common import databricks_pipeline  # noqa: E402
from dlt.sources.rest_api import rest_api_source  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load the REST API demo source into Databricks.")
    parser.add_argument(
        "--catalog",
        help="Unity Catalog catalog for dlt destination credentials.",
    )
    parser.add_argument(
        "--dataset-name",
        default="raw",
        help="Unity Catalog schema where dlt lands raw tables.",
    )
    return parser.parse_args()


def build_source():
    """A declarative REST API source: two endpoints with a parent/child dependency."""
    return rest_api_source(
        {
            "client": {
                "base_url": "https://jsonplaceholder.typicode.com/",
                "paginator": "single_page",  # this demo API is not paginated
            },
            "resource_defaults": {
                "write_disposition": "merge",  # upsert on primary_key across runs
                "primary_key": "id",
            },
            "resources": [
                # Top-level resource → table raw.rest_posts
                {
                    "name": "rest_posts",
                    "endpoint": {"path": "posts"},
                },
                # Child resource: one request per post id, → table raw.rest_comments
                {
                    "name": "rest_comments",
                    "endpoint": {
                        "path": "posts/{post_id}/comments",
                        "params": {
                            "post_id": {
                                "type": "resolve",
                                "resource": "rest_posts",
                                "field": "id",
                            }
                        },
                    },
                },
            ],
        }
    )


def main() -> None:
    args = parse_args()
    if args.catalog:
        os.environ["DESTINATION__DATABRICKS__CREDENTIALS__CATALOG"] = args.catalog

    pipeline = databricks_pipeline("rest_api_demo", dataset_name=args.dataset_name)
    load_info = pipeline.run(build_source())
    print(load_info)


if __name__ == "__main__":
    main()
