"""Agentic quality gate for the dlt -> dbt -> Databricks handoff.

The gate turns dbt test results and simple mart metrics into a promotion packet:
promote, review, or block. It is intentionally deterministic first, with an
LLM-ready prompt at the end of the report. That keeps the AI layer grounded in
evidence instead of giving it direct warehouse authority.

Run:
    uv run python orchestration/agentic_quality_gate.py --sample

With real dbt artifacts:
    uv run python orchestration/agentic_quality_gate.py \
      --run-results transformation/dbt_databricks/target/run_results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_RESULTS = (
    REPO_ROOT / "transformation" / "dbt_databricks" / "target" / "run_results.json"
)

Decision = Literal["promote", "review", "block"]

BLOCKING_STATUSES = {"error", "fail", "failed", "runtime error"}
REVIEW_STATUSES = {"skipped", "warn"}
EXPECTED_WARNING_HINTS = (
    "line_charge",
    "total_allowed",
    "negative",
    "reversal",
    "expect_column_values_to_be_between",
)

SAMPLE_METRICS: dict[str, int | float | str] = {
    "claim_service_lines": 410_000,
    "schemas_guarded": 2,
    "expected_warning_classes": 2,
    "freshness_minutes": 18,
    "max_allowed_ratio": 1.84,
}


@dataclass(frozen=True)
class DbtResult:
    """Small, stable subset of dbt's run_results.json result shape."""

    unique_id: str
    status: str
    message: str = ""
    failures: int | None = None
    execution_time: float | None = None

    @property
    def name(self) -> str:
        return self.unique_id.rsplit(".", maxsplit=1)[-1]

    @property
    def normalized_status(self) -> str:
        return self.status.lower().strip()


@dataclass(frozen=True)
class GateThresholds:
    """Policy knobs that keep the agent auditable."""

    max_expected_warnings: int = 3
    max_freshness_minutes: int = 60
    max_allowed_ratio: float = 5.0
    min_claim_service_lines: int = 1


@dataclass(frozen=True)
class GateReport:
    decision: Decision
    score: int
    summary: str
    evidence: list[str]
    actions: list[str]
    metrics: dict[str, int | float | str]
    results: list[DbtResult]
    generated_at: datetime
    sample_mode: bool

    def to_markdown(self, include_prompt: bool = True) -> str:
        mode = "sample evidence" if self.sample_mode else "dbt artifact evidence"
        lines = [
            "# Agentic Claims Quality Gate",
            "",
            f"Generated: {self.generated_at.isoformat(timespec='seconds')}",
            f"Mode: {mode}",
            f"Decision: {self.decision.upper()}",
            f"Confidence score: {self.score}/100",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Evidence",
            "",
            *[f"- {item}" for item in self.evidence],
            "",
            "## Recommended Actions",
            "",
            *[f"- {item}" for item in self.actions],
            "",
            "## Metrics Snapshot",
            "",
            *[f"- {key}: {value}" for key, value in self.metrics.items()],
        ]

        if include_prompt:
            lines.extend(
                [
                    "",
                    "## LLM Review Prompt",
                    "",
                    build_llm_prompt(self),
                ]
            )

        return "\n".join(lines).strip() + "\n"


def sample_dbt_results() -> list[DbtResult]:
    """Representative output from the claims models without needing a warehouse."""

    return [
        DbtResult("model.dbt_databricks.stg_claims", "success", "typed claim lines"),
        DbtResult("model.dbt_databricks.int_claims", "success", "claim headers rolled up"),
        DbtResult("model.dbt_databricks.mart_claims_by_payer", "success"),
        DbtResult("model.dbt_databricks.mart_member_summary", "success"),
        DbtResult(
            "test.dbt_databricks.expect_column_values_to_be_between_stg_claims_line_charge",
            "warn",
            "negative line_charge values found; expected claim reversals",
            failures=42,
        ),
        DbtResult(
            "test.dbt_databricks.expect_column_values_to_be_between_int_claims_total_allowed",
            "warn",
            "negative total_allowed values found; expected net reversals",
            failures=9,
        ),
    ]


def load_dbt_results(path: Path) -> list[DbtResult]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    results = payload.get("results", [])
    if not isinstance(results, list):
        raise ValueError(f"{path} does not look like a dbt run_results.json file")

    parsed: list[DbtResult] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        parsed.append(
            DbtResult(
                unique_id=str(item.get("unique_id", "unknown")),
                status=str(item.get("status", "unknown")),
                message=str(item.get("message") or ""),
                failures=_optional_int(item.get("failures")),
                execution_time=_optional_float(item.get("execution_time")),
            )
        )
    return parsed


def load_metrics(path: Path | None) -> dict[str, int | float | str]:
    if path is None:
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object of metric names to values")

    metrics: dict[str, int | float | str] = {}
    for key, value in payload.items():
        if isinstance(value, str | int | float):
            metrics[str(key)] = value
    return metrics


def evaluate_gate(
    results: list[DbtResult],
    metrics: dict[str, int | float | str],
    thresholds: GateThresholds | None = None,
    sample_mode: bool = False,
) -> GateReport:
    thresholds = thresholds or GateThresholds()
    blockers = [result for result in results if result.normalized_status in BLOCKING_STATUSES]
    reviewable = [result for result in results if result.normalized_status in REVIEW_STATUSES]
    warnings = [result for result in reviewable if result.normalized_status == "warn"]
    expected_warnings = [result for result in warnings if is_expected_claims_warning(result)]
    unexpected_warnings = [result for result in warnings if result not in expected_warnings]
    skipped = [result for result in reviewable if result.normalized_status == "skipped"]

    evidence = [
        f"dbt results inspected: {len(results)}",
        f"blocking statuses: {len(blockers)}",
        f"expected claims warnings: {len(expected_warnings)}",
        f"unexpected warnings: {len(unexpected_warnings)}",
    ]
    if expected_warnings:
        evidence.extend(
            f"expected warning: {format_result(result)}" for result in expected_warnings[:4]
        )
    actions: list[str] = []
    score = 100
    decision: Decision = "promote"

    claim_lines = _metric_number(metrics, "claim_service_lines")
    freshness_minutes = _metric_number(metrics, "freshness_minutes")
    max_allowed_ratio = _metric_number(metrics, "max_allowed_ratio")

    if blockers:
        decision = "block"
        score -= 55
        evidence.extend(format_result(result) for result in blockers[:4])
        actions.append("Stop promotion and inspect the failing dbt model or test first.")

    if claim_lines < thresholds.min_claim_service_lines:
        decision = "block"
        score -= 35
        evidence.append(
            f"claim_service_lines={claim_lines:g}, below {thresholds.min_claim_service_lines}"
        )
        actions.append("Verify the dlt load completed before dbt built the claims marts.")

    if unexpected_warnings or skipped:
        decision = "review" if decision != "block" else decision
        score -= 25
        evidence.extend(format_result(result) for result in [*unexpected_warnings, *skipped][:4])
        actions.append("Ask the owner to classify unexpected warnings before publishing marts.")

    if len(expected_warnings) > thresholds.max_expected_warnings:
        decision = "review" if decision != "block" else decision
        score -= 15
        actions.append("Check whether claim reversal volume changed materially.")

    if freshness_minutes > thresholds.max_freshness_minutes:
        decision = "review" if decision != "block" else decision
        score -= 12
        evidence.append(
            f"freshness_minutes={freshness_minutes:g}, above {thresholds.max_freshness_minutes}"
        )
        actions.append("Confirm the latest dlt load package landed in Unity Catalog.")

    if max_allowed_ratio > thresholds.max_allowed_ratio:
        decision = "review" if decision != "block" else decision
        score -= 18
        evidence.append(
            f"max_allowed_ratio={max_allowed_ratio:g}, above {thresholds.max_allowed_ratio:g}"
        )
        actions.append("Sample payer/state groups with unusually high allowed ratios.")

    if not actions:
        actions.append("Promote analytics outputs and retain the packet with the run artifacts.")

    score = max(0, min(100, score))
    summary = summarize_decision(decision, expected_warnings, unexpected_warnings, blockers)

    return GateReport(
        decision=decision,
        score=score,
        summary=summary,
        evidence=evidence,
        actions=actions,
        metrics=metrics,
        results=results,
        generated_at=datetime.now(tz=UTC),
        sample_mode=sample_mode,
    )


def is_expected_claims_warning(result: DbtResult) -> bool:
    haystack = f"{result.unique_id} {result.message}".lower()
    return any(hint in haystack for hint in EXPECTED_WARNING_HINTS)


def summarize_decision(
    decision: Decision,
    expected_warnings: list[DbtResult],
    unexpected_warnings: list[DbtResult],
    blockers: list[DbtResult],
) -> str:
    if decision == "block":
        return (
            "The run has blocking failures or empty critical claims output. The agent should "
            "stop promotion until the failing evidence is resolved."
        )
    if decision == "review":
        return (
            "The run built enough evidence for analysis, but it carries signals that need "
            "human review before promotion."
        )
    if expected_warnings:
        return (
            "The run is promotable. The only warnings match known claims-domain reversals, "
            "so the packet records them without failing the release."
        )
    if unexpected_warnings or blockers:
        return "The run needs review."
    return "The run is promotable: dbt results and mart metrics are inside policy."


def build_llm_prompt(report: GateReport) -> str:
    evidence = "\n".join(f"- {item}" for item in report.evidence)
    actions = "\n".join(f"- {item}" for item in report.actions)
    metrics = "\n".join(f"- {key}: {value}" for key, value in report.metrics.items())
    return "\n".join(
        [
            "You are reviewing a dlt + dbt Databricks claims analytics run.",
            "Use only the evidence below. Do not invent warehouse facts.",
            f"Gate decision: {report.decision.upper()}",
            f"Confidence score: {report.score}/100",
            "",
            "Evidence:",
            evidence,
            "",
            "Metrics:",
            metrics,
            "",
            "Recommended actions:",
            actions,
            "",
            "Return three bullets: business impact, data-quality risk, next action.",
        ]
    )


def run_llm_review(report: GateReport) -> str | None:
    """Send the packet's prompt to Claude and return its review, or None if unavailable.

    The deterministic gate decision is already made — the LLM adds a grounded narrative
    (business impact, risk, next action) on top of it, never authority over it. Degrades
    gracefully: missing SDK or credentials produce a note on stderr, not a failure.
    """
    try:
        import anthropic
    except ImportError:
        print(
            "LLM review skipped: anthropic SDK not installed (uv sync --extra llm).",
            file=sys.stderr,
        )
        return None

    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY / CLI login profile
    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=(
                "You are reviewing data-quality gate packets for an insurance claims "
                "analytics pipeline (dlt ingestion -> dbt models on Databricks)."
            ),
            messages=[{"role": "user", "content": build_llm_prompt(report)}],
        )
    except (anthropic.AuthenticationError, TypeError):
        # TypeError is the SDK's "no credential source at all" failure mode.
        print(
            "LLM review skipped: no Anthropic credentials (set ANTHROPIC_API_KEY).",
            file=sys.stderr,
        )
        return None
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as error:
        print(f"LLM review skipped: API error ({error}).", file=sys.stderr)
        return None

    text = "".join(block.text for block in response.content if block.type == "text")
    return text.strip() or None


def format_result(result: DbtResult) -> str:
    failures = "" if result.failures is None else f", failures={result.failures}"
    message = "" if not result.message else f": {result.message}"
    return f"{result.name} status={result.status}{failures}{message}"


def _metric_number(metrics: dict[str, int | float | str], key: str) -> float:
    value = metrics.get(key, 0)
    if isinstance(value, int | float):
        return float(value)
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return 0.0


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an agent-ready quality gate packet from dbt run results."
    )
    parser.add_argument(
        "--run-results",
        type=Path,
        default=DEFAULT_RUN_RESULTS,
        help="Path to dbt target/run_results.json.",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        help="Optional JSON object with mart metrics such as claim_service_lines.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use built-in claims evidence so the example runs without Databricks.",
    )
    parser.add_argument("--output", type=Path, help="Write the Markdown packet to this path.")
    parser.add_argument("--json", action="store_true", help="Print a compact JSON decision.")
    parser.add_argument(
        "--fail-on-block",
        action="store_true",
        help="Exit non-zero when the decision is 'block', so pipelines/CI stop on bad runs.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help=(
            "Also send the packet's prompt to Claude and append the review "
            "(needs `uv sync --extra llm` and Anthropic credentials)."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample_mode = args.sample
    if sample_mode:
        results = sample_dbt_results()
        metrics = load_metrics(args.metrics) if args.metrics else dict(SAMPLE_METRICS)
    else:
        if not args.run_results.exists():
            print(
                f"Missing dbt run results: {args.run_results}\n"
                "Run dbt build first, pass --run-results, or use --sample for the offline demo.",
                file=sys.stderr,
            )
            return 2
        results = load_dbt_results(args.run_results)
        metrics = load_metrics(args.metrics)
    report = evaluate_gate(results, metrics, sample_mode=sample_mode)
    llm_review = run_llm_review(report) if args.llm else None

    if args.json:
        payload = {
            "decision": report.decision,
            "score": report.score,
            "summary": report.summary,
            "sample_mode": report.sample_mode,
            "actions": report.actions,
        }
        if llm_review:
            payload["llm_review"] = llm_review
        print(json.dumps(payload, indent=2))
    else:
        markdown = report.to_markdown()
        if llm_review:
            markdown += f"\n## LLM Review (claude-opus-4-8)\n\n{llm_review}\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(markdown, encoding="utf-8")
            print(f"Wrote {args.output}")
            print(f"Decision: {report.decision.upper()} (score {report.score}/100)")
        else:
            print(markdown)

    if args.fail_on_block and report.decision == "block":
        print(f"Gate decision is BLOCK (score {report.score}/100) — failing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
