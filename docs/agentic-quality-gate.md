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

You can also pass a small metrics JSON file:

```json
{
  "claim_service_lines": 410000,
  "schemas_guarded": 2,
  "expected_warning_classes": 2,
  "freshness_minutes": 18,
  "max_allowed_ratio": 1.84
}
```

## Agent behavior

The gate returns one of three decisions:

- `promote` when tests and metrics are inside policy.
- `review` when the run completed but carries unexpected warnings, stale data,
  or suspicious mart ratios.
- `block` when dbt failed or critical claims output is empty.

Expected claims warnings are treated differently from generic failures. For
example, negative charge or allowed amounts can represent reversals, so the gate
records them as evidence instead of pretending real data is perfectly clean.

## Production sketch

In a Databricks Workflow or Asset Bundle:

1. Run dlt ingestion into the raw Unity Catalog schema.
2. Run dbt build against the analytics schema.
3. Run the quality gate against `target/run_results.json` and a metrics snapshot.
4. Send the Markdown packet to a reviewer, ticket, Slack channel, or LLM summary.
5. Promote downstream dashboards only when the decision is `promote`.

This is intentionally "AI with receipts": the model can summarize risk and next
actions, but the policy decision is traceable to deterministic evidence.
