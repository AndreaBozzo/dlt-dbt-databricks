"""Advanced: append events to a Unity Catalog Delta table with Databricks Zerobus.

Zerobus is a push-based, serverless ingestion API: records go directly to a Delta table without
the object-storage staging used by COPY INTO. dlt supports it only for append resources and gives
at-least-once delivery, so every row below has a stable event_id that consumers can de-duplicate.

This example intentionally selects Zerobus per resource with ``databricks_adapter``. The
destination-wide dlt setting still has an open reliability issue; the per-resource route is the
documented, working path and lets other resources in the same pipeline keep using COPY INTO.

Prerequisites: a Zerobus-supported Databricks region, a managed Delta target backed by your cloud
object storage (Databricks default storage is unsupported), and an OAuth service principal with
access to the pre-created target table. Set DESTINATION__DATABRICKS__ZEROBUS__ENDPOINT_URL plus the
nested Zerobus CLIENT_ID/CLIENT_SECRET variables shown in .env.example. The exact target DDL and
least-privilege grants are documented in ingestion/README.md.

Run:  uv run python ingestion/advanced/zerobus_append.py --catalog <catalog> --dataset-name <schema>
"""

from __future__ import annotations

import argparse
import inspect
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parents[1]))  # make ingestion/_common importable

from _common import demo_pipeline, dlt  # noqa: E402
from dlt.destinations.adapters import databricks_adapter  # noqa: E402


def event_rows(run_id: str, observed_at: datetime) -> list[dict[str, object]]:
    """Return a small, flat batch compatible with Zerobus' broadest Parquet type support."""
    return [
        {
            "event_id": f"{run_id}-001",
            "run_id": run_id,
            "event_type": "page_view",
            "user_id": 101,
            "source": "docs",
            "observed_at": observed_at,
        },
        {
            "event_id": f"{run_id}-002",
            "run_id": run_id,
            "event_type": "example_run",
            "user_id": 102,
            "source": "cli",
            "observed_at": observed_at,
        },
    ]


def build_zerobus_events(
    run_id: str | None = None,
    observed_at: datetime | None = None,
) -> dlt.DltResource:
    """Build an append-only resource whose table data uses Zerobus instead of COPY INTO."""
    batch_id = run_id or uuid.uuid4().hex
    batch_time = observed_at or datetime.now(UTC)

    @dlt.resource(name="zerobus_events", write_disposition="append")
    def events():
        yield from event_rows(batch_id, batch_time)

    return databricks_adapter(
        events,
        insert_api="zerobus",
        table_comment="Append-only demo events ingested through Databricks Zerobus.",
    )


def _has_oauth_credentials(credentials: object | None) -> bool:
    return bool(
        credentials
        and getattr(credentials, "client_id", None)
        and getattr(credentials, "client_secret", None)
    )


def require_zerobus_configuration() -> None:
    """Fail before extraction when the endpoint or OAuth credentials are incomplete."""
    config = dlt.destinations.databricks().configuration(None, accept_partial=True)
    zerobus = config.zerobus
    missing: list[str] = []

    if zerobus is None or not zerobus.endpoint_url:
        missing.append("Zerobus endpoint URL")

    dedicated_credentials = zerobus.credentials if zerobus else None
    if not (
        _has_oauth_credentials(dedicated_credentials) or _has_oauth_credentials(config.credentials)
    ):
        missing.append("OAuth client ID/client secret")

    if missing:
        raise RuntimeError(
            f"Zerobus configuration incomplete ({', '.join(missing)}). "
            "Set the DESTINATION__DATABRICKS__ZEROBUS__* variables shown in .env.example."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a demo event batch through Zerobus.")
    parser.add_argument(
        "--catalog",
        default=os.getenv("ZEROBUS_CATALOG"),
        help="Target Unity Catalog catalog (defaults to ZEROBUS_CATALOG when set).",
    )
    parser.add_argument(
        "--dataset-name",
        default=os.getenv("ZEROBUS_DATASET_NAME", "raw"),
        help="Target Unity Catalog schema (defaults to ZEROBUS_DATASET_NAME or raw).",
    )
    parser.add_argument(
        "--run-id",
        help="Stable batch id for replay/de-duplication demos (defaults to a random UUID).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.catalog:
        os.environ["DESTINATION__DATABRICKS__CREDENTIALS__CATALOG"] = args.catalog

    require_zerobus_configuration()
    pipeline = demo_pipeline("zerobus_append_demo", dataset_name=args.dataset_name)
    load_info = pipeline.run(build_zerobus_events(run_id=args.run_id))
    print(load_info)


if __name__ == "__main__":
    main()
