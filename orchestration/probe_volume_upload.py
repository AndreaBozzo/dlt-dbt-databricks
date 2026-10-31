"""Compare SQL PUT and SDK Files API uploads from local or Databricks serverless compute.

Run with existing Databricks SDK authentication:
    uv run --env-file .env python orchestration/probe_volume_upload.py \
        --http-path /sql/1.0/warehouses/ID

The probe creates a unique schema, uploads the same JSON payload by both routes, loads each
successful upload with COPY INTO and verifies the rows. It removes the schema on completion.
Run this file as a serverless Python job to test the compute-side networking reported in
https://github.com/dlt-hub/dlt/issues/4606. It does not change the production loader.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import re
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse

from databricks import sql
from databricks.sdk import WorkspaceClient


def identifier(value: str) -> str:
    return "`" + value.replace("`", "``") + "`"


def literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def error_summary(error: Exception) -> str:
    """Keep transport diagnostics without copying signed URL query parameters into output."""
    return re.sub(r"\?[^\s'\"<>]+", "?[redacted]", str(error))[:500]


def probe(http_path: str, catalog: str) -> dict[str, dict[str, object]]:
    # The connector can log signed storage URLs itself; emit our sanitized result instead.
    logging.getLogger("databricks.sql").setLevel(logging.CRITICAL)
    workspace = WorkspaceClient()
    schema = "volume_probe_" + uuid.uuid4().hex[:12]
    qualified_schema = f"{identifier(catalog)}.{identifier(schema)}"
    payload = b'{"id":1,"label":"one"}\n{"id":2,"label":"two"}\n'
    results: dict[str, dict[str, object]] = {}
    with (
        tempfile.TemporaryDirectory(prefix="volume-upload-probe-") as scratch,
        sql.connect(
            server_hostname=urlparse(workspace.config.host).hostname,
            http_path=http_path,
            credentials_provider=lambda: workspace.config.authenticate,
            staging_allowed_local_path=[scratch],
        ) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(f"CREATE SCHEMA {qualified_schema}")
        try:
            cursor.execute(f"CREATE VOLUME {qualified_schema}.uploads")
            local_file = Path(scratch) / "rows.json"
            local_file.write_bytes(payload)
            for method in ("put", "files_api"):
                directory = f"/Volumes/{catalog}/{schema}/uploads/{method}"
                remote_file = directory + "/rows.json"
                table = f"{qualified_schema}.{identifier(method)}"
                try:
                    if method == "put":
                        cursor.execute(
                            f"PUT {literal(local_file.as_posix())} INTO "
                            f"{literal(remote_file)} OVERWRITE"
                        )
                    else:
                        workspace.files.create_directory(directory)
                        workspace.files.upload(remote_file, io.BytesIO(payload), overwrite=True)
                    with workspace.files.download(remote_file).contents as stream:
                        if stream.read() != payload:
                            raise RuntimeError("Uploaded bytes differ from the source")
                    cursor.execute(f"CREATE TABLE {table} (id BIGINT, label STRING)")
                    cursor.execute(f"COPY INTO {table} FROM {literal(directory)} FILEFORMAT = JSON")
                    cursor.execute(f"SELECT id, label FROM {table} ORDER BY id")
                    rows = [tuple(row) for row in cursor.fetchall()]
                    if rows != [(1, "one"), (2, "two")]:
                        raise RuntimeError(f"Unexpected loaded rows: {rows}")
                    results[method] = {"success": True, "rows": len(rows)}
                except Exception as error:
                    results[method] = {
                        "success": False,
                        "error_type": type(error).__name__,
                        "error": error_summary(error),
                    }
                print(json.dumps({method: results[method]}), flush=True)
        finally:
            cursor.execute(f"DROP SCHEMA {qualified_schema} CASCADE")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--http-path", required=True, help="SQL warehouse HTTP path")
    parser.add_argument("--catalog", default="workspace")
    args = parser.parse_args()
    results = probe(args.http_path, args.catalog)
    print("VOLUME_UPLOAD_PROBE=" + json.dumps(results), flush=True)
    if not results["files_api"]["success"]:
        raise SystemExit("Files API upload/load verification failed")


if __name__ == "__main__":
    main()
