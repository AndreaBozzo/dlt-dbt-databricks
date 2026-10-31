# Compare Unity Catalog Volume upload paths

`orchestration/probe_volume_upload.py` compares the SQL connector's `PUT` upload with the
Databricks SDK Files API from the same compute. This investigates the serverless staging
failure tracked in [dlt #4606](https://github.com/dlt-hub/dlt/issues/4606).

The probe creates a unique schema and managed Volume, uploads identical JSON bytes by both
routes, downloads each successful upload to compare the bytes, then runs `COPY INTO` and
checks the resulting table rows. It drops its temporary schema on completion. It does not
modify the Asset Bundle's ingestion mode.

## Run locally

With this repository's `.env` credentials and a working SQL warehouse:

```bash
uv run --env-file .env python orchestration/probe_volume_upload.py \
  --http-path /sql/1.0/warehouses/YOUR_WAREHOUSE_ID \
  --catalog workspace
```

The principal needs permission to create schemas, Volumes and tables in the selected catalog.
Only the probe's newly created schema is removed. Local success does not establish that
uploads work from serverless compute, where network routing differs.

## Run from serverless compute

Upload the Python file to your workspace and run it as a serverless Python job task with:

- Parameters: `--http-path`, the SQL warehouse HTTP path, `--catalog`, the writable catalog.
- Environment version: `2`.
- Dependencies: `databricks-sql-connector[pyarrow]==4.4.0` and `databricks-sdk==0.117.0`.
- SDK runtime authentication, with no embedded token or credentials in the Python file.

The probe permits `PUT` to read only its temporary local directory through the connector's
`staging_allowed_local_path`. Missing this setting causes a local configuration failure
before the upload reaches the storage gateway.

Each method emits a JSON result. The final `VOLUME_UPLOAD_PROBE=` line contains both results;
the task fails if Files API upload, byte comparison or table-row verification fails. For a
multi-task run, fetch the Python task's output rather than the parent run's output.

## Result on 2026-10-31

The comparison ran on an AWS Free Edition workspace, from a serverless Python job using the
versions above and a serverless SQL warehouse.

| Upload route | Result |
| --- | --- |
| SQL `PUT` | `RequestError`: connection refused at `us-east-2.storage.cloud.databricks.com` |
| SDK Files API | Exact uploaded bytes matched; `COPY INTO` produced both expected rows |

Parent run: `1010254343036247`. Python task run: `343916839495925`. The task completed
successfully and removed its temporary schema and workspace file. Transport messages in the
probe output redact URL query parameters, which can contain signed storage credentials.

Separately, the CDC example loaded and merged its two snapshots successfully from the local
machine into the same workspace. The failure reproduced from serverless compute, matching
the deployment boundary behind the existing Spark landing fallback.

## Upstream opening

dlt 1.32 still uploads local files to a managed Volume with SQL `PUT`. A supported Files API
upload option or an upload/cleanup extension hook would let callers keep dlt's normal loading
and merge machinery on serverless workspaces affected by storage gateway failures. Issue
#4606 already owns this proposal, and its author has offered to contribute a PR.
