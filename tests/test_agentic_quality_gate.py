from agentic_quality_gate import (
    SAMPLE_METRICS,
    DbtResult,
    evaluate_gate,
    sample_dbt_results,
)


def test_sample_claims_warnings_are_promotable() -> None:
    report = evaluate_gate(sample_dbt_results(), dict(SAMPLE_METRICS), sample_mode=True)

    assert report.decision == "promote"
    assert report.score == 100
    assert "known claims-domain reversals" in report.summary


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
