"""Execute the snapshot example against DuckDB, including deletion and change detection."""

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
