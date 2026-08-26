"""Offline contract tests for the Databricks Zerobus example."""

from datetime import UTC, datetime

from zerobus_append import build_zerobus_events, event_rows


def test_event_rows_have_stable_deduplication_keys():
    observed_at = datetime(2026, 8, 26, 12, 0, tzinfo=UTC)

    rows = event_rows("run-42", observed_at)

    assert [row["event_id"] for row in rows] == ["run-42-001", "run-42-002"]
    assert all(row["run_id"] == "run-42" for row in rows)
    assert all(row["observed_at"] == observed_at for row in rows)


def test_resource_is_append_only_and_selects_zerobus():
    resource = build_zerobus_events(
        run_id="run-42",
        observed_at=datetime(2026, 8, 26, 12, 0, tzinfo=UTC),
    )

    schema = resource.compute_table_schema()

    assert schema["name"] == "zerobus_events"
    assert schema["write_disposition"] == "append"
    assert schema["x-insert-api"] == "zerobus"
