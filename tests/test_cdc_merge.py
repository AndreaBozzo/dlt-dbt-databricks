"""Execute the snapshot example against DuckDB, including deletion and change detection."""

import pyarrow.parquet as pq
import pytest

pytest.importorskip("duckdb", reason="duckdb lane extra not installed")

from cdc_merge import (  # noqa: E402
    CDC_SOURCE,
    customers_snapshot,
    dlt,
    load_snapshot,
    record_dlt_load,
)


@pytest.fixture
def pipeline(tmp_path):
    return dlt.pipeline(
        pipeline_name="test_cdc_merge",
        destination=dlt.destinations.duckdb(str(tmp_path / "warehouse.duckdb")),
        dataset_name="raw",
        pipelines_dir=str(tmp_path / "pipelines"),
    )


def loaded_rows(pipeline):
    with pipeline.sql_client() as client:
        return client.execute_sql(
            "SELECT id, name, _dlt_load_id FROM raw.cdc_customers ORDER BY id"
        )


def audit_rows(pipeline):
    with pipeline.sql_client() as client:
        return client.execute_sql(
            "SELECT load_id, committed_at FROM raw.ingestion_audit "
            "WHERE source_name = 'cdc_customers' ORDER BY committed_at"
        )


def test_snapshot_inserts_updates_and_deletes_absent_keys(pipeline):
    pipeline.run(
        customers_snapshot(
            [
                {"id": 11, "name": "before"},
                {"id": 22, "name": "removed"},
                {"id": 33, "name": "stable"},
            ]
        )
    )
    pipeline.run(
        customers_snapshot(
            [
                {"id": 11, "name": "after"},
                {"id": 33, "name": "stable"},
                {"id": 44, "name": "added"},
            ]
        )
    )

    assert [(id_, name) for id_, name, _ in loaded_rows(pipeline)] == [
        (11, "after"),
        (33, "stable"),
        (44, "added"),
    ]


def test_snapshot_skips_unchanged_rows_and_replays(pipeline):
    pipeline.run(customers_snapshot([{"id": 1, "name": "same"}, {"id": 2, "name": "before"}]))
    original = loaded_rows(pipeline)
    snapshot = [{"id": 1, "name": "same"}, {"id": 2, "name": "after"}]
    pipeline.run(customers_snapshot(snapshot))
    changed = loaded_rows(pipeline)

    assert changed[0] == original[0]
    assert changed[1][1] == "after"
    assert changed[1][2] != original[1][2]

    load_snapshot(pipeline, snapshot)
    first_audit = audit_rows(pipeline)
    replay = load_snapshot(pipeline, snapshot)

    assert loaded_rows(pipeline) == changed
    second_audit = audit_rows(pipeline)
    assert second_audit[:1] == first_audit
    assert second_audit[1][0] == replay.loads_ids[0]
    assert second_audit[1][1] > first_audit[0][1]

    record_dlt_load(replay, CDC_SOURCE, {CDC_SOURCE})
    assert audit_rows(pipeline) == second_audit


def test_empty_snapshot_deletes_existing_rows(pipeline):
    pipeline.run(customers_snapshot([{"id": 1, "name": "removed"}]))
    assert len(loaded_rows(pipeline)) == 1

    empty = load_snapshot(pipeline, [])

    assert loaded_rows(pipeline) == []
    assert [load_id for load_id, _ in audit_rows(pipeline)] == empty.loads_ids


def test_empty_first_snapshot_can_be_populated(pipeline):
    load_info = pipeline.run(customers_snapshot([]))
    load_info.raise_on_failed_jobs()
    parquet_job = next(
        job
        for job in load_info.load_packages[0].jobs["completed_jobs"]
        if job.job_file_info.table_name == "cdc_customers"
        and job.job_file_info.file_format == "parquet"
    )
    empty_batch = pq.read_table(parquet_job.file_path)
    assert empty_batch.num_rows == 0
    assert {"id", "name", "tier", "_dlt_id", "_dlt_load_id"} <= set(empty_batch.column_names)
    with pipeline.sql_client() as client:
        assert client.execute_sql("SELECT id, name, tier FROM raw.cdc_customers") == []
        required_columns = client.execute_sql(
            "SELECT column_name, is_nullable FROM information_schema.columns "
            "WHERE table_schema = 'raw' AND table_name = 'cdc_customers' "
            "AND column_name IN ('id', '_dlt_id', '_dlt_load_id')"
        )
        assert set(required_columns) == {
            ("id", "NO"),
            ("_dlt_id", "NO"),
            ("_dlt_load_id", "NO"),
        }

    pipeline.run(
        customers_snapshot([{"id": 1, "name": "first", "tier": "gold"}])
    ).raise_on_failed_jobs()

    with pipeline.sql_client() as client:
        assert client.execute_sql("SELECT id, name, tier FROM raw.cdc_customers") == [
            (1, "first", "gold")
        ]


@pytest.mark.parametrize("status", [None, 1])
def test_package_without_success_marker_does_not_advance_freshness(pipeline, status):
    load_snapshot(pipeline, [{"id": 1, "name": "same"}])
    baseline = audit_rows(pipeline)
    load_info = pipeline.run(customers_snapshot([{"id": 1, "name": "same"}]))
    with pipeline.sql_client() as client:
        load_id = load_info.loads_ids[0]
        if status is None:
            client.execute_sql("DELETE FROM raw._dlt_loads WHERE load_id = %s", load_id)
        else:
            client.execute_sql(
                "UPDATE raw._dlt_loads SET status = %s WHERE load_id = %s", status, load_id
            )

    record_dlt_load(load_info, CDC_SOURCE, {CDC_SOURCE})

    assert audit_rows(pipeline) == baseline


def test_failed_dlt_load_does_not_advance_freshness(pipeline):
    from dlt.common.destination.exceptions import DestinationHasFailedJobs

    load_snapshot(pipeline, [{"id": 1, "name": "same"}])
    baseline = audit_rows(pipeline)
    load_info = pipeline.run(customers_snapshot([{"id": 1, "name": "same"}]))
    package = load_info.load_packages[0]
    package.jobs["failed_jobs"].append(package.jobs["completed_jobs"][0])
    with pytest.raises(DestinationHasFailedJobs):
        record_dlt_load(load_info, CDC_SOURCE, {CDC_SOURCE})

    assert audit_rows(pipeline) == baseline
