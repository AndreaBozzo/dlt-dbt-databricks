"""Shared helpers for the dlt example pipelines.

Keeps credential loading and the dlt→Databricks destination wiring in one place so each example
script stays focused on the *source* and the dlt feature it demonstrates.

Scripts under ingestion/pipelines/ and ingestion/advanced/ import this by adding the parent
`ingestion/` directory to sys.path (see the top of each script).
"""

from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Anchor dlt's project/settings directory to ingestion/ even when examples are launched from the
# repository root. This makes the checked-in ingestion/.dlt/config.toml and a local secrets.toml
# discoverable. An explicit DLT_PROJECT_DIR supplied by a caller still wins.
_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
_REPO_ROOT = _THIS_FILE.parents[1]
load_dotenv(_REPO_ROOT / ".env")
os.environ.setdefault("DLT_PROJECT_DIR", str(_THIS_FILE.parent))

# dlt 1.30+ maps this setting to spark.sql.session.timeZone. Environment values loaded above win;
# UTC is the deterministic default for the SQL example's timestamp cursor.
_CATALOG_ENV = "DESTINATION__DATABRICKS__CREDENTIALS__CATALOG"
_SESSION_TIMEZONE_ENV = "DESTINATION__DATABRICKS__CREDENTIALS__SESSION_TIMEZONE"
os.environ.setdefault(_CATALOG_ENV, "workspace")
os.environ.setdefault(_SESSION_TIMEZONE_ENV, "UTC")


def import_dlt():
    """Import dltHub's dlt package in Databricks serverless despite the built-in DLT hook."""
    metas = list(sys.meta_path)
    if os.getenv("DATABRICKS_RUNTIME_VERSION") and metas:
        sys.meta_path = metas[1:]
    try:
        import dlt

        return dlt
    finally:
        sys.meta_path = metas


dlt = import_dlt()

# The Unity Catalog schema dlt lands raw data into. dbt's sources.yml must point at the same name.
DATASET_NAME = os.getenv("DLT_DATASET_NAME", "raw")

# Destination lane. "databricks" needs a workspace + credentials; "duckdb" runs anywhere (used by
# CI and local smoke runs) and lands the same raw tables in a local file that dbt's `duckdb`
# profile target reads. Same pipelines, same schema — only the destination differs.
DESTINATION_NAME = os.getenv("DLT_DESTINATION", "databricks")
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", str(_REPO_ROOT / "local" / "dlt_dbt.duckdb")))


def demo_pipeline(name: str, dataset_name: str = DATASET_NAME) -> dlt.Pipeline:
    """Return a dlt pipeline for the destination selected by DLT_DESTINATION.

    Credentials (for Databricks) are resolved by dlt from env vars / .dlt/secrets.toml — nothing
    secret here. For DuckDB there are no credentials; the file lives at DUCKDB_PATH.
    """
    if DESTINATION_NAME == "duckdb":
        DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
        destination = dlt.destinations.duckdb(str(DUCKDB_PATH))
    else:
        destination = DESTINATION_NAME
    return dlt.pipeline(
        pipeline_name=name,
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )
