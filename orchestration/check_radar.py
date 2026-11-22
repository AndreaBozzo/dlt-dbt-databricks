"""Check the radar evidence record (updates/adoption.toml) against the repository.

The radar writes prose about upstream releases. This script keeps the facts behind that prose
honest: an available release and an adopted version are recorded separately, a "floor is met"
claim is compared with uv.lock, and a materialization claim is compared with the effective dbt
configuration. It reads files only: no network, no Databricks credentials, no dbt run, and it
never edits pyproject.toml, uv.lock or databricks.yml.

    uv run python orchestration/check_radar.py          # or: make radar-check

Exit status 0 when every check passes, 1 with one message per failed check otherwise.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RECORD = Path("updates/adoption.toml")
PYPROJECT = Path("pyproject.toml")
LOCKFILE = Path("uv.lock")
BUNDLE = Path("databricks.yml")
DBT_PROJECT = Path("transformation/dbt_databricks/dbt_project.yml")
# What dbt uses when neither the project, a properties file nor the model sets a materialization.
DBT_DEFAULT_MATERIALIZATION = "view"


# --- versions ---------------------------------------------------------------------------------


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_version(text: str) -> tuple[int, ...]:
    """Parse a plain dotted release number. Pre-releases and suffixes are rejected, not guessed."""
    if not re.fullmatch(r"\d+(\.\d+)*", text):
        raise ValueError(f"unsupported version {text!r}: only plain dotted numbers are compared")
    parts = [int(p) for p in text.split(".")]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


# --- repository facts -------------------------------------------------------------------------


def locked_versions(lock_path: Path) -> dict[str, list[str]]:
    """Every version of each package that uv.lock holds."""
    data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    found: dict[str, list[str]] = {}
    for package in data.get("package", []):
        found.setdefault(normalize(package["name"]), []).append(package["version"])
    return found


_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*([^;]*)")
_FLOOR = re.compile(r"^\s*>=\s*(\S+)\s*$")


def parse_requirement(text: str) -> tuple[str, list[str]]:
    """Return the normalized name and every `>=` floor of one requirement string."""
    match = _REQUIREMENT.match(text)
    if not match:
        raise ValueError(f"cannot parse requirement {text!r}")
    floors = []
    for clause in match.group(2).split(","):
        floor = _FLOOR.match(clause)
        if floor:
            floors.append(floor.group(1))
    return normalize(match.group(1)), floors


def _requirement_strings_in_pyproject(data: dict) -> list[str]:
    strings = list(data.get("project", {}).get("dependencies", []))
    for extra in data.get("project", {}).get("optional-dependencies", {}).values():
        strings.extend(extra)
    for group in data.get("dependency-groups", {}).values():
        strings.extend(item for item in group if isinstance(item, str))
    return strings


def _requirement_strings_in_bundle(node: object) -> list[str]:
    """Every list under a `dependencies` key, wherever the bundle nests it."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "dependencies" and isinstance(value, list):
                found.extend(item for item in value if isinstance(item, str))
            else:
                found.extend(_requirement_strings_in_bundle(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_requirement_strings_in_bundle(item))
    return found


def declared_floors(root: Path) -> dict[str, list[tuple[str, str]]]:
    """Map package -> [(floor, file)] from pyproject.toml and the Asset Bundle."""
    sources = {
        str(PYPROJECT): _requirement_strings_in_pyproject(
            tomllib.loads((root / PYPROJECT).read_text(encoding="utf-8"))
        ),
        str(BUNDLE): _requirement_strings_in_bundle(
            yaml.safe_load((root / BUNDLE).read_text(encoding="utf-8"))
        ),
    }
    floors: dict[str, list[tuple[str, str]]] = {}
    for file, strings in sources.items():
        for text in strings:
            name, found = parse_requirement(text)
            for floor in found:
                floors.setdefault(name, []).append((floor, file))
    return floors


# --- dbt materializations ---------------------------------------------------------------------


@dataclass(frozen=True)
class Materialization:
    value: str | None  # None when the config is not a plain string literal
    source: str | None  # repo-relative file that decides it; None for the dbt default


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"\{#.*?#\}", "", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", "", sql)


def _config_call_bodies(sql: str) -> list[str]:
    """The argument text of every `config(...)` call, with balanced parentheses."""
    bodies = []
    for match in re.finditer(r"\bconfig\s*\(", sql):
        depth, start = 1, match.end()
        for index in range(start, len(sql)):
            if sql[index] == "(":
                depth += 1
            elif sql[index] == ")":
                depth -= 1
                if depth == 0:
                    bodies.append(sql[start:index])
                    break
    return bodies


def sql_config_materialization(sql: str) -> tuple[bool, str | None]:
    """(set, value) from the model's own config() calls; the last call that sets it wins."""
    is_set, value = False, None
    for body in _config_call_bodies(_strip_comments(sql)):
        match = re.search(r"\bmaterialized\s*=\s*([^,]+)", body)
        if not match:
            continue
        literal = re.fullmatch(r"\s*(['\"])([^'\"]*)\1\s*", match.group(1))
        is_set, value = True, literal.group(2) if literal else None
    return is_set, value


def _project_level(tree: dict, parts: list[str]) -> str | None:
    """Walk dbt_project.yml folder config; the deepest `+materialized` wins."""
    current: str | None = None
    node = tree
    for part in [None, *parts]:
        if part is not None:
            nested = node.get(part)
            if not isinstance(nested, dict):
                break
            node = nested
        for key in ("+materialized", "materialized"):
            if key in node and not isinstance(node[key], dict):
                current = node[key]
    return current


def effective_materializations(root: Path) -> dict[str, Materialization]:
    """Resolve each model's materialization the way dbt orders it.

    Precedence, lowest to highest: dbt default, dbt_project.yml folder config, a properties file
    (`models: - name: x, config: {materialized: ...}`), the model's own `config()` call.
    """
    project_file = root / DBT_PROJECT
    project = yaml.safe_load(project_file.read_text(encoding="utf-8"))
    project_dir = project_file.parent
    project_tree = project.get("models", {}).get(project["name"], {})
    project_rel = DBT_PROJECT.as_posix()

    result: dict[str, Materialization] = {}
    for model_path in project.get("model-paths", ["models"]):
        base = project_dir / model_path
        properties: dict[str, tuple[str, str]] = {}
        for yml in sorted(list(base.rglob("*.yml")) + list(base.rglob("*.yaml"))):
            document = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
            for entry in document.get("models", []) or []:
                config = entry.get("config") or {}
                if "materialized" in config:
                    properties[entry["name"]] = (
                        config["materialized"],
                        yml.relative_to(root).as_posix(),
                    )
        for sql_file in sorted(base.rglob("*.sql")):
            name = sql_file.stem
            relative = sql_file.relative_to(base)
            folders = list(relative.parent.parts) + [name]
            value = _project_level(project_tree, folders)
            decision = Materialization(
                value or DBT_DEFAULT_MATERIALIZATION, project_rel if value else None
            )
            if name in properties:
                decision = Materialization(*properties[name])
            is_set, literal = sql_config_materialization(sql_file.read_text(encoding="utf-8"))
            if is_set:
                decision = Materialization(literal, sql_file.relative_to(root).as_posix())
            result[name] = decision
    return result


# --- the record -------------------------------------------------------------------------------


def _is_date(value: object) -> bool:
    try:
        dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def _is_url(value: object) -> bool:
    return isinstance(value, str) and value.startswith("https://")


def _version(errors: list[str], where: str, value: object) -> tuple[int, ...] | None:
    try:
        return parse_version(str(value))
    except ValueError as error:
        errors.append(f"{where}: {error}")
        return None


def check_dependency(
    entry: dict,
    locked: dict[str, list[str]],
    floors: dict[str, list[tuple[str, str]]],
) -> tuple[list[str], str]:
    errors: list[str] = []
    name = entry.get("name", "<unnamed>")
    where = f"dependency {name}"
    observed = entry.get("observed") or {}
    adopted = entry.get("adopted") or {}

    for field in ("version", "released", "seen", "source"):
        if not observed.get(field):
            errors.append(f"{where}: observed.{field} is missing")
    for field in ("version", "date", "change"):
        if not adopted.get(field):
            errors.append(f"{where}: adopted.{field} is missing")
    for field in ("released", "seen"):
        if observed.get(field) and not _is_date(observed[field]):
            errors.append(f"{where}: observed.{field} is not an ISO date")
    if adopted.get("date") and not _is_date(adopted["date"]):
        errors.append(f"{where}: adopted.date is not an ISO date")
    if _is_date(observed.get("released")) and _is_date(observed.get("seen")):
        if observed["seen"] < observed["released"]:
            errors.append(f"{where}: observed.seen is earlier than observed.released")
    if observed.get("source") and not _is_url(observed["source"]):
        errors.append(f"{where}: observed.source must be an https URL")
    if adopted.get("change") and not _is_url(adopted["change"]):
        errors.append(f"{where}: adopted.change must be an https URL")

    validation = adopted.get("validation")
    if not isinstance(validation, list):
        errors.append(f"{where}: adopted.validation must be a list, possibly empty")
    else:
        if not all(_is_url(link) for link in validation):
            errors.append(f"{where}: every adopted.validation entry must be an https URL")
        if not validation and not adopted.get("validation_note"):
            errors.append(
                f"{where}: adopted.validation is empty; say why in adopted.validation_note"
            )

    lock_versions = locked.get(normalize(name))
    if not lock_versions:
        errors.append(f"{where}: not found in uv.lock")
        return errors, f"{name}: not in uv.lock"
    shown = ", ".join(lock_versions)

    if adopted.get("version") and adopted["version"] not in lock_versions:
        errors.append(
            f"{where}: adopted.version {adopted['version']} but uv.lock holds {shown}. "
            "Record an adoption only in the change that updates the lockfile."
        )
    lock_parsed = [v for v in (_version(errors, f"{where} lock", v) for v in lock_versions) if v]
    for floor, file in floors.get(normalize(name), []):
        parsed = _version(errors, f"{where} floor in {file}", floor)
        if parsed and lock_parsed and min(lock_parsed) < parsed:
            errors.append(f"{where}: {file} declares >={floor} but uv.lock holds {shown}")

    seen = _version(errors, f"{where} observed.version", observed.get("version"))
    taken = _version(errors, f"{where} adopted.version", adopted.get("version"))
    if seen and taken:
        if seen < taken:
            errors.append(
                f"{where}: observed.version {observed['version']} is older than adopted.version "
                f"{adopted['version']}; update the observation"
            )
        if seen > taken and not adopted.get("adoption_note"):
            errors.append(
                f"{where}: {observed['version']} is available but {adopted['version']} is "
                "adopted; say why in adopted.adoption_note"
            )
    summary = f"{name}: available {observed.get('version')}, adopted {adopted.get('version')}"
    return errors, f"{summary}, uv.lock {shown}"


def check_floor_claim(claim: dict, locked: dict[str, list[str]]) -> tuple[list[str], str]:
    where = f"claim {claim.get('id', '<no id>')}"
    errors: list[str] = []
    name, floor, met = claim.get("dependency"), claim.get("floor"), claim.get("met")
    if not name or not floor or not isinstance(met, bool):
        return [f"{where}: floor_met needs dependency, floor and met = true/false"], ""
    lock_versions = locked.get(normalize(name))
    if not lock_versions:
        return [f"{where}: {name} is not in uv.lock"], ""
    parsed_floor = _version(errors, f"{where} floor", floor)
    parsed_lock = [_version(errors, f"{where} lock", v) for v in lock_versions]
    if errors or parsed_floor is None or None in parsed_lock:
        return errors, ""
    satisfied = all(v >= parsed_floor for v in parsed_lock if v)
    shown = ", ".join(lock_versions)
    if met and not satisfied:
        errors.append(f"{where}: says the {name} floor {floor} is met but uv.lock holds {shown}")
    if not met and satisfied:
        errors.append(
            f"{where}: says the {name} floor {floor} is not met but uv.lock holds {shown}; "
            "update the claim"
        )
    return errors, f"{claim['id']}: {name} floor {floor}, uv.lock {shown}, met={satisfied}"


def check_materialization_claim(
    claim: dict, effective: dict[str, Materialization], root: Path
) -> tuple[list[str], list[str]]:
    where = f"claim {claim.get('id', '<no id>')}"
    errors: list[str] = []
    expected, models, cites = claim.get("materialized"), claim.get("models"), claim.get("cites")
    if not expected or not models or not isinstance(models, list):
        return [f"{where}: materialization needs materialized and a models list"], []
    if not isinstance(cites, list) or not cites:
        errors.append(f"{where}: cites must name the configuration files that decide the models")
        cites = []
    for cite in cites:
        if not (root / cite).is_file():
            errors.append(f"{where}: cited file {cite} does not exist")
    lines = []
    for model in models:
        found = effective.get(model)
        if found is None:
            errors.append(f"{where}: model {model} not found in the dbt project")
            continue
        origin = found.source or "dbt default"
        lines.append(f"{claim['id']}: {model} -> {found.value} ({origin})")
        if found.value is None:
            errors.append(f"{where}: {model} sets materialized with a non-literal value")
        elif found.value != expected:
            errors.append(
                f"{where}: says {model} is {expected} but the effective config is "
                f"{found.value} ({origin})"
            )
        if found.source and found.source not in cites:
            errors.append(
                f"{where}: {model} is decided by {found.source}, which the claim does not cite"
            )
    return errors, lines


def check_record(root: Path, record_path: Path | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, report lines) for the record under `root`."""
    record = tomllib.loads((root / (record_path or RECORD)).read_text(encoding="utf-8"))
    locked = locked_versions(root / LOCKFILE)
    floors = declared_floors(root)
    errors: list[str] = []
    lines: list[str] = []

    dependencies = record.get("dependency", [])
    if not dependencies:
        errors.append("no [[dependency]] entries in the record")
    for entry in dependencies:
        found, line = check_dependency(entry, locked, floors)
        errors.extend(found)
        lines.append(line)

    claims = record.get("claim", [])
    ids = [claim.get("id") for claim in claims]
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errors.append(f"claim id {duplicate} is used more than once")
    effective = None
    for claim in claims:
        if not claim.get("statement"):
            errors.append(f"claim {claim.get('id', '<no id>')}: statement is missing")
        kind = claim.get("type")
        if kind == "floor_met":
            found, line = check_floor_claim(claim, locked)
            errors.extend(found)
            if line:
                lines.append(line)
        elif kind == "materialization":
            if effective is None:
                effective = effective_materializations(root)
            found, claim_lines = check_materialization_claim(claim, effective, root)
            errors.extend(found)
            lines.extend(claim_lines)
        else:
            errors.append(f"claim {claim.get('id', '<no id>')}: unknown type {kind!r}")
    return errors, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--record", type=Path, default=RECORD, help="record path under the root")
    args = parser.parse_args(argv)

    errors, lines = check_record(args.root, args.record)
    for line in lines:
        print(f"ok    {line}")
    for error in errors:
        print(f"FAIL  {error}", file=sys.stderr)
    if errors:
        print(f"radar check failed: {len(errors)} problem(s)", file=sys.stderr)
        return 1
    print("radar check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
