"""Project doctor for local dlt + dbt + Databricks setup.

This is intentionally a mostly-offline preflight. It helps a new user understand whether the repo is
ready to parse dbt, run examples, and validate/deploy a Databricks Asset Bundle without performing
warehouse writes.

Run:
    uv run python orchestration/doctor.py
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = REPO_ROOT / "transformation" / "dbt_databricks"


class Reporter:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print(f"[OK]   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"[WARN] {message}")

    def fail(self, message: str) -> None:
        self.errors += 1
        print(f"[FAIL] {message}")


def run_command(command: Sequence[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def first_line(output: str) -> str:
    return next((line.strip() for line in output.splitlines() if line.strip()), "")


def output_tail(output: str, lines: int = 8) -> str:
    content = [line.rstrip() for line in output.splitlines() if line.strip()]
    return "\n      ".join(content[-lines:]) if content else "(no output)"


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    upper = value.upper()
    return (
        "YOUR_" in upper
        or "EXAMPLE" in upper
        or value in {"https://YOUR_HOST.cloud.databricks.com"}
    )


def env_value(values: dict[str, str | None], key: str) -> str | None:
    return os.getenv(key) or values.get(key)


def load_env_values() -> dict[str, str | None]:
    env_path = REPO_ROOT / ".env"
    return dotenv_values(env_path) if env_path.exists() else {}


def warehouse_id_from_values(values: dict[str, str | None]) -> str | None:
    warehouse_id = env_value(values, "DATABRICKS_WAREHOUSE_ID")
    if not is_placeholder(warehouse_id):
        return warehouse_id

    http_path = env_value(values, "DATABRICKS_HTTP_PATH") or env_value(
        values, "DESTINATION__DATABRICKS__CREDENTIALS__HTTP_PATH"
    )
    if not http_path:
        return None

    match = re.search(r"/warehouses/([^/?#]+)", http_path)
    return match.group(1) if match else None


def bundle_vars(values: dict[str, str | None]) -> dict[str, str]:
    vars_: dict[str, str] = {}
    warehouse_id = warehouse_id_from_values(values)
    if warehouse_id:
        vars_["warehouse_id"] = warehouse_id
    vars_["catalog"] = env_value(values, "DATABRICKS_CATALOG") or "workspace"
    vars_["schema"] = env_value(values, "DATABRICKS_SCHEMA") or "analytics"
    return vars_


def bundle_var_args(values: dict[str, str | None]) -> list[str]:
    args: list[str] = []
    for key, value in bundle_vars(values).items():
        args.extend(["--var", f"{key}={value}"])
    return args


def check_files(reporter: Reporter) -> None:
    print("\nFiles")
    required = [
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "uv.lock",
        REPO_ROOT / "databricks.yml",
        DBT_DIR / "dbt_project.yml",
        DBT_DIR / "profiles.yml.example",
    ]
    for path in required:
        if path.exists():
            reporter.ok(f"{path.relative_to(REPO_ROOT)} exists")
        else:
            reporter.fail(f"{path.relative_to(REPO_ROOT)} is missing")

    if (REPO_ROOT / ".env").exists():
        reporter.ok(".env exists")
    else:
        reporter.warn(".env is missing; copy .env.example before running dlt examples")

    if (DBT_DIR / "profiles.yml").exists():
        reporter.ok("transformation/dbt_databricks/profiles.yml exists")
    else:
        reporter.warn("profiles.yml is missing; copy profiles.yml.example before dbt debug/build")


def check_python_and_imports(reporter: Reporter) -> None:
    print("\nPython")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    reporter.ok(f"Python {version}")

    for module in ["dlt", "dbt", "databricks", "dotenv"]:
        if importlib.util.find_spec(module):
            reporter.ok(f"Python import available: {module}")
        else:
            reporter.fail(f"Python import missing: {module}")


def check_tools(reporter: Reporter) -> None:
    print("\nTools")
    for tool in ["uv", "dbt", "databricks"]:
        path = shutil.which(tool)
        if path:
            reporter.ok(f"{tool} found at {path}")
        elif tool == "databricks":
            reporter.warn("Databricks CLI not found; bundle validate/deploy will be unavailable")
        else:
            reporter.fail(f"{tool} not found on PATH")

    result = run_command(["uv", "lock", "--check"])
    if result.returncode == 0:
        reporter.ok("uv.lock is in sync")
    else:
        reporter.fail(f"uv.lock check failed: {first_line(result.stdout)}")


def check_environment(reporter: Reporter) -> None:
    print("\nEnvironment")
    values = load_env_values()

    required_for_dlt = [
        "DATABRICKS_HOST",
        "DATABRICKS_HTTP_PATH",
        "DATABRICKS_TOKEN",
        "DESTINATION__DATABRICKS__CREDENTIALS__SERVER_HOSTNAME",
        "DESTINATION__DATABRICKS__CREDENTIALS__HTTP_PATH",
        "DESTINATION__DATABRICKS__CREDENTIALS__ACCESS_TOKEN",
    ]
    for key in required_for_dlt:
        value = env_value(values, key)
        if is_placeholder(value):
            reporter.warn(f"{key} is not set; dlt writes to Databricks will not run yet")
        else:
            reporter.ok(f"{key} is set")

    dlt_dataset = env_value(values, "DLT_DATASET_NAME") or "raw"
    catalog = env_value(values, "DATABRICKS_CATALOG") or "workspace"
    schema = env_value(values, "DATABRICKS_SCHEMA") or "analytics"
    reporter.ok(
        "dbt/dlt handoff defaults: "
        f"catalog={catalog}, raw_schema={dlt_dataset}, dbt_schema={schema}"
    )

    warehouse_id = warehouse_id_from_values(values)
    if warehouse_id:
        reporter.ok(f"bundle warehouse_id resolved: {warehouse_id}")
    else:
        reporter.warn(
            "bundle warehouse_id not found; set DATABRICKS_WAREHOUSE_ID or DATABRICKS_HTTP_PATH"
        )


def check_dbt(reporter: Reporter) -> None:
    print("\ndbt")
    if not (DBT_DIR / "profiles.yml").exists():
        reporter.warn("Skipping dbt parse because profiles.yml is missing")
        return

    if not run_dbt_deps_if_needed(reporter):
        return

    parse = run_command(
        [
            "uv",
            "run",
            "dbt",
            "parse",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
        ]
    )
    if parse.returncode == 0:
        reporter.ok("dbt parse succeeded")
        if (DBT_DIR / "target" / "manifest.json").exists():
            reporter.ok("dbt manifest exists for dbt Power User")
        else:
            reporter.warn("dbt parse succeeded but target/manifest.json was not found")
    else:
        reporter.fail(f"dbt parse failed:\n      {output_tail(parse.stdout)}")


def default_databricks_profile() -> str | None:
    result = run_command(["databricks", "auth", "profiles"])
    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if "(Default)" in line and line.rstrip().endswith("YES"):
            return line.split("(Default)", maxsplit=1)[0].strip()
    return None


def dbt_packages_installed() -> bool:
    package_dir = DBT_DIR / "dbt_packages"
    return package_dir.exists() and any(path.is_dir() for path in package_dir.iterdir())


def run_dbt_deps_if_needed(reporter: Reporter) -> bool:
    if dbt_packages_installed():
        reporter.ok("dbt packages are installed")
        return True

    deps = run_command(
        [
            "uv",
            "run",
            "dbt",
            "deps",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
        ]
    )
    if deps.returncode == 0:
        reporter.ok("dbt deps succeeded")
        return True

    reporter.fail(f"dbt deps failed:\n      {output_tail(deps.stdout)}")
    return False


def check_bundle(reporter: Reporter, online: bool) -> None:
    print("\nDatabricks Asset Bundle")
    if not shutil.which("databricks"):
        reporter.warn("Skipping bundle checks because Databricks CLI is not installed")
        return

    host = os.getenv("DATABRICKS_HOST")
    profile = default_databricks_profile()
    if not is_placeholder(host):
        reporter.ok("DATABRICKS_HOST is set in the shell")
    elif profile:
        reporter.ok(f"Databricks CLI default profile is valid: {profile}")
    else:
        reporter.warn(
            "No shell DATABRICKS_HOST or valid default Databricks CLI profile found; "
            "bundle validate/deploy needs one of them"
        )

    if not online:
        reporter.ok(
            "Skipped online bundle validation; run with --online to call Databricks CLI auth"
        )
        return

    values = load_env_values()
    warehouse_id = warehouse_id_from_values(values)
    if not warehouse_id:
        reporter.fail("Cannot run online bundle validation without a warehouse_id")
        return

    command = ["databricks", "bundle", "validate", *bundle_var_args(values)]
    result = run_command(command)
    if result.returncode == 0:
        reporter.ok("databricks bundle validate succeeded")
    else:
        reporter.fail(f"databricks bundle validate failed: {first_line(result.stdout)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local readiness for this dlt/dbt/Databricks repo."
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Also run Databricks CLI bundle validation, which needs workspace auth.",
    )
    args = parser.parse_args()

    print("dlt-dbt-databricks doctor")
    print(f"Repo: {REPO_ROOT}")

    reporter = Reporter()
    check_files(reporter)
    check_python_and_imports(reporter)
    check_tools(reporter)
    check_environment(reporter)
    check_dbt(reporter)
    check_bundle(reporter, online=args.online)

    print("\nSummary")
    if reporter.errors:
        print(f"{reporter.errors} error(s), {reporter.warnings} warning(s)")
        return 1
    print(f"Ready with {reporter.warnings} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
