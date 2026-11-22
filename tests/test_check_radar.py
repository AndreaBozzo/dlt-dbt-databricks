"""Tests for check_radar.py: the radar record is checked against the lockfile and dbt config.

Each failing case edits a copy of the real repository files, so the tests exercise the same
parsers that the committed record goes through.
"""

import shutil
from pathlib import Path

import pytest
from check_radar import (
    ROOT,
    Materialization,
    check_record,
    effective_materializations,
    main,
    parse_requirement,
    parse_version,
    sql_config_materialization,
)

COPIED = ["pyproject.toml", "uv.lock", "databricks.yml", "updates/adoption.toml"]
DBT_DIR = "transformation/dbt_databricks"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway copy of the files the check reads."""
    for relative in COPIED:
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / relative, tmp_path / relative)
    shutil.copytree(
        ROOT / DBT_DIR,
        tmp_path / DBT_DIR,
        ignore=shutil.ignore_patterns("target", "dbt_packages", "local_data"),
    )
    return tmp_path


def edit(path: Path, old: str, new: str) -> None:
    """Replace exactly one occurrence, so a drifting fixture fails loudly."""
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"{old!r} found {text.count(old)} times in {path.name}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def problems(repo: Path) -> list[str]:
    return check_record(repo)[0]


def test_committed_record_passes():
    errors, lines = check_record(ROOT)
    assert errors == []
    assert any(
        line.startswith("dbt-databricks: available 1.13.0, adopted 1.13.0") for line in lines
    )


def test_floor_met_claim_fails_when_the_lock_is_below_the_floor(repo):
    # The October incident: a floor described as satisfied while the lockfile held an older one.
    edit(
        repo / "uv.lock",
        'name = "certifi"\nversion = "2026.10.23"',
        'name = "certifi"\nversion = "2026.7.22"',
    )
    found = problems(repo)
    assert any("floor 2026.10.23 is met but uv.lock holds 2026.7.22" in e for e in found)


def test_floor_met_claim_fails_when_the_claimed_floor_is_above_the_lock(repo):
    edit(repo / "updates/adoption.toml", 'floor = "2026.10.23"', 'floor = "2026.11.1"')
    assert any("floor 2026.11.1 is met" in e for e in problems(repo))


def test_stale_not_met_claim_fails_once_the_lock_catches_up(repo):
    edit(repo / "updates/adoption.toml", "met = true", "met = false")
    assert any("is not met but uv.lock holds" in e for e in problems(repo))


def test_adopted_version_must_equal_the_lock(repo):
    edit(
        repo / "updates/adoption.toml",
        '[dependency.adopted]\nversion = "1.32.0"',
        '[dependency.adopted]\nversion = "1.31.0"',
    )
    found = problems(repo)
    assert any("adopted.version 1.31.0 but uv.lock holds 1.32.0" in e for e in found)


def test_lock_below_a_declared_floor_fails(repo):
    edit(repo / "pyproject.toml", '"dbt-databricks>=1.13.0,<2"', '"dbt-databricks>=1.14.0,<2"')
    assert any(
        "pyproject.toml declares >=1.14.0 but uv.lock holds 1.13.0" in e for e in problems(repo)
    )


def test_bundle_floor_is_read_too(repo):
    edit(repo / "databricks.yml", '"dlt[databricks]>=1.32.0,<2"', '"dlt[databricks]>=1.33.0,<2"')
    assert any(
        "databricks.yml declares >=1.33.0 but uv.lock holds 1.32.0" in e for e in problems(repo)
    )


def test_newer_release_needs_a_reason_for_not_adopting(repo):
    edit(
        repo / "updates/adoption.toml",
        'version = "1.32.0"\nreleased',
        'version = "1.33.0"\nreleased',
    )
    assert any("1.33.0 is available but 1.32.0 is adopted" in e for e in problems(repo))


def test_observation_older_than_adoption_fails(repo):
    edit(repo / "updates/adoption.toml", 'version = "0.167.0"', 'version = "0.100.0"')
    assert any(
        "observed.version 0.100.0 is older than adopted.version" in e for e in problems(repo)
    )


def test_empty_validation_needs_a_note(repo):
    edit(
        repo / "updates/adoption.toml",
        'validation_note = "The stack refresh commit has no pull request and no retained CI run."',
        "",
    )
    assert any("adopted.validation is empty" in e for e in problems(repo))


def test_adoption_must_link_the_change(repo):
    edit(
        repo / "updates/adoption.toml",
        'change = "https://github.com/AndreaBozzo/dlt-dbt-databricks/commit/b361a3e088cd3aa8cb74d3b76f18b9e18feddf9e"',
        'change = "b361a3e"',
    )
    assert any("adopted.change must be an https URL" in e for e in problems(repo))


def test_wrong_materialization_claim_fails(repo):
    # The October incident: staging and intermediate models treated as tables.
    edit(repo / "updates/adoption.toml", 'materialized = "view"', 'materialized = "table"')
    found = problems(repo)
    assert any(
        "says stg_claims is table but the effective config is view "
        "(transformation/dbt_databricks/dbt_project.yml)" in e
        for e in found
    )


def test_model_override_is_what_the_check_follows(repo):
    # Dropping the override makes the mart a table, so the incremental claim goes stale.
    edit(
        repo / DBT_DIR / "models/marts/mart_post_engagement.sql",
        "materialized='incremental'",
        "tags=['x']",
    )
    assert any(
        "says mart_post_engagement is incremental but the effective config is table" in e
        for e in problems(repo)
    )


def test_materialization_claim_must_cite_the_deciding_file(repo):
    edit(
        repo / "updates/adoption.toml",
        'cites = ["transformation/dbt_databricks/models/marts/mart_post_engagement.sql"]',
        'cites = ["transformation/dbt_databricks/dbt_project.yml"]',
    )
    assert any(
        "decided by transformation/dbt_databricks/models/marts/mart_post_engagement.sql" in e
        for e in problems(repo)
    )


def test_materialization_claim_for_an_unknown_model_fails(repo):
    edit(repo / "updates/adoption.toml", '"mart_member_summary"', '"mart_missing"')
    assert any("model mart_missing not found" in e for e in problems(repo))


def test_properties_file_overrides_the_project_default(repo):
    (repo / DBT_DIR / "models/marts/_override.yml").write_text(
        "version: 2\nmodels:\n  - name: mart_claims_by_payer\n"
        "    config:\n      materialized: view\n",
        encoding="utf-8",
    )
    found = problems(repo)
    assert any(
        "says mart_claims_by_payer is table but the effective config is view" in e for e in found
    )


def test_sql_config_ignores_comments_and_reads_the_last_literal():
    commented = (
        "{{ config(materialized='view') }}\n"
        "{# config(materialized='table') #}\n"
        "-- {{ config(materialized='ephemeral') }}\n"
    )
    assert sql_config_materialization(commented) == (True, "view")
    two_calls = "{{ config(materialized='view') }}\n{{ config(materialized=\"ephemeral\") }}"
    assert sql_config_materialization(two_calls) == (True, "ephemeral")
    assert sql_config_materialization("select 1") == (False, None)
    assert sql_config_materialization("{{ config(materialized=var('m')) }}") == (True, None)


def test_model_config_overrides_the_project_folder_default():
    effective = effective_materializations(ROOT)
    assert effective["mart_post_engagement"] == Materialization(
        "incremental", f"{DBT_DIR}/models/marts/mart_post_engagement.sql"
    )
    assert effective["mart_claims_by_payer"] == Materialization(
        "table", f"{DBT_DIR}/dbt_project.yml"
    )


def test_requirement_and_version_parsing():
    assert parse_requirement("dlt[databricks]>=1.32.0,<2") == ("dlt", ["1.32.0"])
    assert parse_requirement("Databricks_SDK>=0.117.0 ; python_version>='3.12'") == (
        "databricks-sdk",
        ["0.117.0"],
    )
    assert parse_version("1.0") == parse_version("1.0.0") < parse_version("1.0.1")
    with pytest.raises(ValueError):
        parse_version("1.0rc1")


def test_main_exits_nonzero_with_a_message_on_a_bad_record(repo, capsys):
    edit(repo / "updates/adoption.toml", 'floor = "2026.10.23"', 'floor = "2026.11.1"')
    assert main(["--root", str(repo)]) == 1
    assert "FAIL" in capsys.readouterr().err
    assert main(["--root", str(ROOT)]) == 0
