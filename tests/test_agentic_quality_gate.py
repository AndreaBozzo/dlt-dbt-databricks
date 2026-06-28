from agentic_quality_gate import (
    SAMPLE_METRICS,
    DbtResult,
    evaluate_gate,
    load_metrics,
    sample_dbt_results,
)


def test_sample_claims_warnings_are_promotable() -> None:
    report = evaluate_gate(sample_dbt_results(), dict(SAMPLE_METRICS), sample_mode=True)

    assert report.decision == "promote"
    assert report.score == 100
    assert "known claims-domain reversals" in report.summary
    assert any("line_charge" in item for item in report.evidence)
    assert any("total_allowed" in item for item in report.evidence)


def test_load_metrics_without_path_returns_no_defaults() -> None:
    assert load_metrics(None) == {}


def test_real_run_without_metrics_blocks_conservatively() -> None:
    results = [DbtResult("model.dbt_databricks.stg_claims", "success")]

    report = evaluate_gate(results, {})

    assert report.decision == "block"
    assert any("claim_service_lines=0" in item for item in report.evidence)


def test_blocks_on_failed_dbt_result() -> None:
    results = [
        DbtResult("model.dbt_databricks.stg_claims", "success"),
        DbtResult("test.dbt_databricks.not_null_claim_id", "fail", "claim_id nulls", failures=12),
    ]

    report = evaluate_gate(results, dict(SAMPLE_METRICS))

    assert report.decision == "block"
    assert any("not_null_claim_id" in item for item in report.evidence)


def test_reviews_unexpected_warning() -> None:
    results = [
        DbtResult("model.dbt_databricks.stg_claims", "success"),
        DbtResult("test.dbt_databricks.accepted_values_payer_type", "warn", "new payer type"),
    ]

    report = evaluate_gate(results, dict(SAMPLE_METRICS))

    assert report.decision == "review"
    assert any("accepted_values_payer_type" in item for item in report.evidence)


def test_markdown_includes_llm_review_prompt() -> None:
    report = evaluate_gate(sample_dbt_results(), dict(SAMPLE_METRICS), sample_mode=True)

    markdown = report.to_markdown()

    assert "## LLM Review Prompt" in markdown
    assert "Use only the evidence below" in markdown
