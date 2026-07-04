"""End-to-end: run dlt ingestion, then dbt build, then the quality gate, in one process.

A minimal local orchestrator that proves the dlt → warehouse → dbt handoff on either lane:

  --lane databricks  (default) load into Unity Catalog and build with the dbt `dev` target.
                     For production, schedule the same steps as a Databricks Asset Bundle job
                     (see databricks.yml) rather than this script.
  --lane duckdb      the warehouse-free lane: same pipelines and models against a local DuckDB
                     file, then collect real mart metrics and run the agentic quality gate on the
                     real dbt artifacts. This is what CI runs on every PR.

Run:  uv run python orchestration/run_e2e.py
      uv run python orchestration/run_e2e.py --lane duckdb
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = REPO_ROOT / "transformation" / "dbt_databricks"
LOCAL_DIR = REPO_ROOT / "local"


def dbt_executable() -> str:
    """Return the dbt console script from the active Python environment."""
    executable = Path(sys.executable).with_name("dbt.exe" if sys.platform == "win32" else "dbt")
    return str(executable) if executable.exists() else shutil.which("dbt") or "dbt"


def run_step(title: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"\n=== {title} ===")
    subprocess.run(command, check=True, cwd=REPO_ROOT, env=env)


def run_dlt(lane: str, env: dict[str, str]) -> None:
    """Load raw tables: REST API always; the merge example too on DuckDB (exercises upserts)."""
    scripts = ["pipelines/rest_api_to_databricks.py"]
    if lane == "duckdb":
        scripts.append("advanced/merge_incremental.py")
    for index, script in enumerate(scripts, start=1):
        run_step(
            f"[dlt {index}/{len(scripts)}] {Path(script).name}",
            [sys.executable, str(REPO_ROOT / "ingestion" / script)],
            env=env,
        )


def dbt_command(subcommand: list[str], lane: str) -> list[str]:
    command = [
        dbt_executable(),
        *subcommand,
        "--project-dir",
        str(DBT_DIR),
        "--profiles-dir",
        str(DBT_DIR),
    ]
    if lane == "duckdb":
        command.extend(["--target", "duckdb"])
    return command


def run_dbt(lane: str, env: dict[str, str]) -> None:
    """Check raw-source freshness, then build + test the dbt models on top."""
    run_step(
        "[dbt] source freshness",
        dbt_command(["source", "freshness", "--select", "source:raw"], lane),
        env=env,
    )
    run_step("[dbt] build", dbt_command(["build"], lane), env=env)


def run_gate(env: dict[str, str]) -> None:
    """DuckDB lane only: real metrics + real dbt artifacts → promote/review/block packet."""
    run_step(
        "[gate 1/2] collect mart metrics",
        [
            sys.executable,
            str(REPO_ROOT / "orchestration" / "collect_gate_metrics.py"),
            "--output",
            str(LOCAL_DIR / "gate_metrics.json"),
        ],
        env=env,
    )
    run_step(
        "[gate 2/2] agentic quality gate",
        [
            sys.executable,
            str(REPO_ROOT / "orchestration" / "agentic_quality_gate.py"),
            "--run-results",
            str(DBT_DIR / "target" / "run_results.json"),
            "--metrics",
            str(LOCAL_DIR / "gate_metrics.json"),
            "--output",
            str(LOCAL_DIR / "gate_packet.md"),
            "--fail-on-block",
        ],
        env=env,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dlt, dbt, and the quality gate end to end.")
    parser.add_argument(
        "--lane",
        choices=("databricks", "duckdb"),
        default="databricks",
        help="Warehouse lane: Unity Catalog (default) or the local/CI DuckDB file.",
    )
    args = parser.parse_args()

    env = dict(os.environ)
    if args.lane == "duckdb":
        env["DLT_DESTINATION"] = "duckdb"

    run_dlt(args.lane, env)
    run_dbt(args.lane, env)
    if args.lane == "duckdb":
        run_gate(env)
        print(f"\nGate packet: {LOCAL_DIR / 'gate_packet.md'}")
    print("\n[OK] End-to-end run complete: dlt loaded raw tables and dbt built marts on top.")


if __name__ == "__main__":
    main()
