"""Run the agentic quality gate as a Databricks job task, after dbt build.

dbt's run_results.json is not shared across job tasks, so this task rebuilds the gate's
evidence from the warehouse itself: it runs the same three queries the DuckDB lane's
collect_gate_metrics.py runs, but through Spark, then evaluates the same deterministic
policy. dbt test failures already fail the job at the dbt task — this task adds the
metric thresholds (volume, freshness, allowed-ratio) and the promotion packet, and
fails the job on a `block` decision.

Wired as the `quality_gate` task in databricks.yml; run standalone with:
    databricks bundle run dlt_dbt_pipeline -t dev
"""

from __future__ import annotations

import argparse
import inspect
import sys
import time
from pathlib import Path

# Databricks serverless execs this file without __file__; recover it from the frame.
_THIS_FILE = Path(globals().get("__file__", inspect.currentframe().f_code.co_filename)).resolve()
sys.path.insert(0, str(_THIS_FILE.parent))  # make agentic_quality_gate importable

from agentic_quality_gate import evaluate_gate  # noqa: E402


def collect_metrics(spark, catalog: str, schema: str, raw_schema: str) -> dict[str, int | float]:
    """Same metric names as collect_gate_metrics.py, computed via Spark SQL."""
    claim_lines = spark.sql(f"select count(*) from `{catalog}`.`{schema}`.stg_claims").first()[0]
    max_ratio = spark.sql(
        f"select coalesce(max(allowed_ratio), 0) from `{catalog}`.`{schema}`.mart_claims_by_payer"
    ).first()[0]
    last_load_id = spark.sql(
        f"select max(_dlt_load_id) from `{catalog}`.`{raw_schema}`.rest_posts"
    ).first()[0]

    freshness_minutes = (time.time() - float(last_load_id)) / 60 if last_load_id else float("inf")
    return {
        "claim_service_lines": int(claim_lines),
        "max_allowed_ratio": round(float(max_ratio), 4),
        "freshness_minutes": round(max(freshness_minutes, 0), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Quality gate task for the Databricks job.")
    parser.add_argument("--catalog", default="workspace")
    parser.add_argument("--schema", default="analytics", help="Schema where dbt built the marts.")
    parser.add_argument("--raw-schema", default="raw", help="Schema where dlt landed raw tables.")
    args = parser.parse_args()

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    metrics = collect_metrics(spark, args.catalog, args.schema, args.raw_schema)
    # No run_results.json across job tasks: evidence is the warehouse metrics. dbt test
    # failures already failed the job one task earlier.
    report = evaluate_gate([], metrics)
    print(report.to_markdown(include_prompt=False))

    if report.decision == "block":
        raise SystemExit(f"Gate decision is BLOCK (score {report.score}/100) — failing the job.")


# No SystemExit on success: Databricks' job runner flags ANY SystemExit — even
# SystemExit(0) — as a task failure, so success must fall off the end quietly.
if __name__ == "__main__":
    main()
