# Agentic Claims Quality Gate

This advanced scenario turns the existing dlt + dbt + Databricks examples into an
agent-ready operating pattern.

The idea: dlt lands fresh raw claims-related data in Unity Catalog, dbt builds and
tests the analytics layer, then a small quality gate creates a promotion packet
for an AI reviewer or human owner. The agent does not get direct write authority.
It receives evidence: dbt statuses, known claims warnings, simple mart metrics,
and suggested next actions.

## Why this fits this project

The repo already models a real handoff:

- dlt owns the `raw` schema.
- dbt owns the `analytics` schema.
- The claims marts include realistic warn-severity tests for reversals and
  negative amounts.
- Databricks Workflows or Asset Bundles can run ingestion before transformation.

That makes the agent useful at the boundary where teams usually ask: "Can we
trust this run enough to publish or alert from it?"

## Demo command

The example runs without a warehouse by using sample evidence shaped like the
claims models:

```bash
uv run python orchestration/agentic_quality_gate.py --sample
```

With real dbt artifacts after a build:

```bash
uv run python orchestration/agentic_quality_gate.py \
  --run-results transformation/dbt_databricks/target/run_results.json \
  --output reports/claims-quality-gate.md
```

For real runs, missing metrics stay missing so the gate blocks or reviews
conservatively instead of borrowing sample values. Pass a small metrics JSON file
when you want promotion decisions to include mart-level signals:

```json
{
  "claim_service_lines": 410000,
  "schemas_guarded": 2,
  "expected_warning_classes": 2,
  "freshness_minutes": 18,
  "max_allowed_ratio": 1.84
}
```

On the DuckDB lane the metrics file is produced automatically:
`orchestration/collect_gate_metrics.py` queries the built marts and
`orchestration/run_e2e.py --lane duckdb` chains it into the gate with
`--fail-on-block`, so CI fails on a `block` decision.

Two more flags:

- `--fail-on-block` — exit non-zero on `block`, so pipelines and CI stop.
- `--llm` — send the packet's prompt to Claude (`claude-opus-4-8`) and append the
  review to the packet. Needs `uv sync --extra llm` plus Anthropic credentials;
  degrades to a stderr note when either is missing. The LLM never owns the
  decision — it reviews the deterministic packet.

## Agent behavior

The gate returns one of three decisions:

- `promote` when tests and metrics are inside policy.
- `review` when the run completed but carries unexpected warnings, stale data,
  or suspicious mart ratios.
- `block` when dbt failed or critical claims output is empty.

Expected claims warnings are treated differently from generic failures. For
example, negative charge or allowed amounts can represent reversals, so the gate
records them as evidence instead of pretending real data is perfectly clean.

## Production: the gate is a job task

[`databricks.yml`](../databricks.yml) wires this in for real — the bundle job is now
three dependent tasks:

1. `dlt_ingest` — dlt lands raw data in Unity Catalog.
2. `dbt_build` — dbt builds and tests the analytics schema (test failures already
   fail the job here).
3. `quality_gate` — [`orchestration/gate_on_databricks.py`](../orchestration/gate_on_databricks.py)
   re-collects the mart metrics via Spark (dbt artifacts don't cross job-task
   boundaries), evaluates the same deterministic policy, prints the packet, and
   **fails the job on `block`**.

Send the Markdown packet to a reviewer, ticket, Slack channel, or LLM summary, and
promote downstream dashboards only when the decision is `promote`.

This is intentionally "AI with receipts": the model can summarize risk and next
actions, but the policy decision is traceable to deterministic evidence.
