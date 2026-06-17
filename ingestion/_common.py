"""Shared helpers for the dlt example pipelines.

Keeps credential loading and the dlt→Databricks destination wiring in one place so each example
script stays focused on the *source* and the dlt feature it demonstrates.

Scripts under ingestion/pipelines/ and ingestion/advanced/ import this by adding the parent
`ingestion/` directory to sys.path (see the top of each script).
"""

from __future__ import annotations

import os
import inspect
from pathlib import Path

import dlt
from dotenv import load_dotenv

# Load repo-root .env so DESTINATION__DATABRICKS__CREDENTIALS__* etc. are available to dlt.
# (dlt also reads ingestion/.dlt/secrets.toml directly if you prefer that.)
_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
_REPO_ROOT = _THIS_FILE.parents[1]
load_dotenv(_REPO_ROOT / ".env")

# The Unity Catalog schema dlt lands raw data into. dbt's sources.yml must point at the same name.
DATASET_NAME = os.getenv("DLT_DATASET_NAME", "raw")


def databricks_pipeline(name: str, dataset_name: str = DATASET_NAME) -> dlt.Pipeline:
    """Return a dlt pipeline configured for the Databricks destination.

    Credentials are resolved by dlt from env vars / .dlt/secrets.toml — nothing secret here.
    """
    return dlt.pipeline(
        pipeline_name=name,
        destination="databricks",
        dataset_name=dataset_name,
        progress="log",
    )
