"""End-to-end: run dlt ingestion, then dbt build, in one process.

A minimal local orchestrator that proves the dlt → Databricks → dbt handoff. For production,
schedule the same two steps as tasks in a Databricks Workflow / Asset Bundle (see README.md)
rather than this script.

Run:  uv run python orchestration/run_e2e.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = REPO_ROOT / "transformation" / "dbt_databricks"


def dbt_executable() -> str:
    """Return the dbt console script from the active Python environment."""
    executable = Path(sys.executable).with_name("dbt.exe" if sys.platform == "win32" else "dbt")
    return str(executable) if executable.exists() else shutil.which("dbt") or "dbt"


def run_dlt() -> None:
    """Run the REST API ingestion example (loads into the Unity Catalog `raw` schema)."""
    print("\n=== [1/2] dlt ingestion: rest_api_to_databricks ===")
    script = REPO_ROOT / "ingestion" / "pipelines" / "rest_api_to_databricks.py"
    subprocess.run([sys.executable, str(script)], check=True)


def run_dbt() -> None:
    """Build + test the dbt models on top of the freshly loaded raw tables."""
    print("\n=== [2/2] dbt build ===")
    subprocess.run(
        [
            dbt_executable(),
            "build",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
        ],
        check=True,
    )


def main() -> None:
    run_dlt()
    run_dbt()
    print("\n✅ End-to-end run complete: dlt loaded raw tables and dbt built marts on top.")


if __name__ == "__main__":
    main()
