"""Publish source freshness after the destination has committed the data."""

from __future__ import annotations

AUDIT_TABLE = "ingestion_audit"
REST_SOURCE = "rest_api"
CDC_SOURCE = "cdc_customers"


def audit_table_ddl(table: str, timestamp_type: str) -> str:
    return (
        f"CREATE TABLE IF NOT EXISTS {table} ("
        f"source_name VARCHAR(128) NOT NULL, load_id VARCHAR(128) NOT NULL, "
        f"committed_at {timestamp_type} NOT NULL)"
    )


def record_dlt_load(load_info, source_name: str, tables: set[str]) -> None:
    """Record committed packages with a source data job, including typed empty batches."""
    load_info.raise_on_failed_jobs()
    load_ids = [
        package.load_id
        for package in load_info.load_packages
        if package.state == "loaded"
        and any(job.job_file_info.table_name in tables for job in package.jobs["completed_jobs"])
    ]
    if not load_ids:
        return

    with load_info.pipeline.sql_client() as client:
        audit = client.make_qualified_table_name(AUDIT_TABLE)
        loads = client.make_qualified_table_name("_dlt_loads")
        timestamp_type = "TIMESTAMPTZ" if load_info.destination_name == "duckdb" else "TIMESTAMP"
        client.execute_sql(audit_table_ddl(audit, timestamp_type))
        for load_id in load_ids:
            # Use the destination's original completion timestamp so replaying publication
            # cannot make an old package look newer.
            client.execute_sql(
                f"INSERT INTO {audit} (source_name, load_id, committed_at) "
                f"SELECT %s, load_id, MAX(inserted_at) FROM {loads} "
                "WHERE load_id = %s AND status = 0 "
                f"AND NOT EXISTS (SELECT 1 FROM {audit} WHERE source_name = %s AND load_id = %s) "
                "GROUP BY load_id",
                source_name,
                load_id,
                source_name,
                load_id,
            )
