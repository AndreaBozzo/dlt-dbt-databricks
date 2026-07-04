"""Collect real mart metrics for the agentic quality gate from the DuckDB lane warehouse.

The gate (agentic_quality_gate.py) blocks conservatively when metrics are missing, so a real run
needs a metrics JSON alongside dbt's run_results.json. This queries the DuckDB file that the dlt
pipelines wrote and dbt built into, and emits the metric names the gate's thresholds understand:

  - claim_service_lines  row count of stg_claims (empty -> block)
  - freshness_minutes    age of the newest dlt load package (from _dlt_load_id, a unix timestamp)
  - max_allowed_ratio    worst payer-group allowed/charged ratio from mart_claims_by_payer

On Databricks the same three queries run against the SQL warehouse instead; this script is the
lane-local implementation so CI can exercise the full dlt -> dbt -> gate loop.

Run:  uv run python orchestration/collect_gate_metrics.py --output local/gate_metrics.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DUCKDB_PATH = REPO_ROOT / "local" / "dlt_dbt.duckdb"


def collect(duckdb_path: Path, now: float | None = None) -> dict[str, int | float]:
    import duckdb

    now = time.time() if now is None else now
    con = duckdb.connect(str(duckdb_path), read_only=True)
    try:
        claim_lines = con.sql("select count(*) from analytics.stg_claims").fetchone()[0]
        max_ratio = con.sql(
            "select coalesce(max(allowed_ratio), 0) from analytics.mart_claims_by_payer"
        ).fetchone()[0]
        # dlt load ids are unix-timestamp strings; the newest one dates the last load package.
        last_load_id = con.sql("select max(_dlt_load_id) from raw.rest_posts").fetchone()[0]
    finally:
        con.close()

    freshness_minutes = (now - float(last_load_id)) / 60 if last_load_id else float("inf")
    return {
        "claim_service_lines": int(claim_lines),
        "max_allowed_ratio": round(float(max_ratio), 4),
        "freshness_minutes": round(max(freshness_minutes, 0), 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect gate metrics from the DuckDB lane.")
    parser.add_argument(
        "--duckdb-path",
        type=Path,
        default=DEFAULT_DUCKDB_PATH,
        help="DuckDB file written by the dlt pipelines and dbt (DLT_DESTINATION=duckdb).",
    )
    parser.add_argument("--output", type=Path, help="Write the metrics JSON to this path.")
    args = parser.parse_args()

    metrics = collect(args.duckdb_path)
    payload = json.dumps(metrics, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
