import json
import sys
import time

import pytest

duckdb = pytest.importorskip("duckdb", reason="duckdb lane extra not installed")

from collect_gate_metrics import collect, main  # noqa: E402


def create_warehouse(path, claim_lines, now):
    con = duckdb.connect(str(path))
    con.execute("create schema analytics")
    con.execute("create schema raw")
    con.execute("create table analytics.stg_claims as select * from range(?)", [claim_lines])
    con.execute("create table analytics.mart_claims_by_payer(allowed_ratio double)")
    con.execute("insert into analytics.mart_claims_by_payer values (0.5), (1.84), (null)")
    con.execute("create table raw.rest_posts(_dlt_load_id varchar)")
    con.execute("insert into raw.rest_posts values (?)", [f"{now - 120:.6f}"])
    con.close()


def test_collect_reads_marts_and_freshness(tmp_path):
    path = tmp_path / "warehouse.duckdb"
    now = time.time()
    create_warehouse(path, claim_lines=5, now=now)

    metrics = collect(path, now=now)

    assert metrics == {
        "claim_service_lines": 5,
        "max_allowed_ratio": 1.84,
        "freshness_minutes": 2.0,
    }


@pytest.mark.parametrize("explicit_path", [False, True])
def test_cli_uses_selected_warehouse(tmp_path, monkeypatch, explicit_path):
    default = tmp_path / "default.duckdb"
    selected = tmp_path / "selected.duckdb"
    create_warehouse(default, claim_lines=5, now=time.time())
    create_warehouse(selected, claim_lines=9, now=time.time())
    monkeypatch.setattr("collect_gate_metrics.DEFAULT_DUCKDB_PATH", default)
    monkeypatch.setenv("DUCKDB_PATH", str(default if explicit_path else selected))
    output = tmp_path / "metrics.json"
    arguments = ["collect_gate_metrics.py", "--output", str(output)]
    if explicit_path:
        arguments.extend(["--duckdb-path", str(selected)])
    monkeypatch.setattr(sys, "argv", arguments)

    assert main() == 0

    assert json.loads(output.read_text())["claim_service_lines"] == 9
