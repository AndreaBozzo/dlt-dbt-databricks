import time

import pytest

duckdb = pytest.importorskip("duckdb", reason="duckdb lane extra not installed")

from collect_gate_metrics import collect  # noqa: E402


def test_collect_reads_marts_and_freshness(tmp_path):
    path = tmp_path / "warehouse.duckdb"
    now = time.time()
    con = duckdb.connect(str(path))
    con.execute("create schema analytics")
    con.execute("create schema raw")
    con.execute("create table analytics.stg_claims as select * from range(5)")
    con.execute("create table analytics.mart_claims_by_payer(allowed_ratio double)")
    con.execute("insert into analytics.mart_claims_by_payer values (0.5), (1.84), (null)")
    con.execute("create table raw.rest_posts(_dlt_load_id varchar)")
    con.execute("insert into raw.rest_posts values (?)", [f"{now - 120:.6f}"])
    con.close()

    metrics = collect(path, now=now)

    assert metrics == {
        "claim_service_lines": 5,
        "max_allowed_ratio": 1.84,
        "freshness_minutes": 2.0,
    }
