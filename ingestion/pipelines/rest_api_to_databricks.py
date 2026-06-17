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
import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable


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
    parser.add_argument(
        "--load-mode",
        choices=("dlt", "spark"),
        default="dlt",
        help=(
            "Use dlt's Databricks destination, or Spark table writes for Databricks "
            "serverless demos."
        ),
    )
    return parser.parse_args()


def build_source():
    """A declarative REST API source: two endpoints with a parent/child dependency."""
    from dlt.sources.rest_api import rest_api_source

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


def fetch_json(path: str) -> list[dict[str, object]]:
    with urlopen(f"https://jsonplaceholder.typicode.com/{path}", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def run_with_spark(catalog: str, dataset_name: str) -> None:
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    posts = [
        {
            "id": row["id"],
            "user_id": row["userId"],
            "title": row["title"],
            "body": row["body"],
        }
        for row in fetch_json("posts")
    ]
    comments = [
        {
            "id": row["id"],
            "post_id": row["postId"],
            "name": row["name"],
            "email": row["email"],
            "body": row["body"],
        }
        for row in fetch_json("comments")
    ]

    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{dataset_name}`")
    for table_name, rows in (("rest_posts", posts), ("rest_comments", comments)):
        (
            spark.createDataFrame(rows)
            .write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(f"`{catalog}`.`{dataset_name}`.`{table_name}`")
        )
        print(f"Wrote {len(rows)} rows to {catalog}.{dataset_name}.{table_name}")


def run_with_dlt(catalog: str | None, dataset_name: str) -> None:
    from _common import databricks_pipeline

    if catalog:
        os.environ["DESTINATION__DATABRICKS__CREDENTIALS__CATALOG"] = catalog
    pipeline = databricks_pipeline("rest_api_demo", dataset_name=dataset_name)
    load_info = pipeline.run(build_source())
    print(load_info)


def main() -> None:
    args = parse_args()
    if args.load_mode == "spark":
        if not args.catalog:
            raise ValueError("--catalog is required when --load-mode spark")
        run_with_spark(args.catalog, args.dataset_name)
    else:
        run_with_dlt(args.catalog, args.dataset_name)


if __name__ == "__main__":
    main()
