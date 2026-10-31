"""Execute the snapshot example against DuckDB, including deletion and change detection."""

import pyarrow.parquet as pq
import pytest

pytest.importorskip("duckdb", reason="duckdb lane extra not installed")

from cdc_merge import customers_snapshot, dlt  # noqa: E402


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

    pipeline.run(customers_snapshot(snapshot))
    assert loaded_rows(pipeline) == changed


def test_empty_snapshot_deletes_existing_rows(pipeline):
    pipeline.run(customers_snapshot([{"id": 1, "name": "removed"}]))
    assert len(loaded_rows(pipeline)) == 1

    pipeline.run(customers_snapshot([]))

    assert loaded_rows(pipeline) == []


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
