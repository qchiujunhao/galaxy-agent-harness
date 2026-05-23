#!/usr/bin/env python3
"""Validate reproduced Galaxy workflow website/package entries."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

VALIDATION_STATUSES = {"pass", "warning", "fail", "draft", "unknown"}
REQUIRED_METADATA_KEYS = [
    "id",
    "title",
    "slug",
    "task_family",
    "workflow_class",
    "validation_profile",
    "source_type",
    "galaxy_instance",
    "galaxy_history_url",
    "galaxy_history_public",
    "galaxy_history_importable",
    "submission_date",
    "status",
    "review_status",
    "validation_status",
    "execution_surface",
    "readme_file",
    "validation_file",
    "provenance_file",
    "tags",
    "summary",
]
VALUE_REQUIRED_KEYS = [
    "id",
    "title",
    "slug",
    "task_family",
    "workflow_class",
    "validation_profile",
    "source_type",
    "galaxy_history_url",
    "validation_status",
    "execution_surface",
    "summary",
]
SOURCE_KEYS = ["source_url", "source_ref"]
REQUIRED_ARTIFACT_KEYS = ["readme_file", "validation_file", "provenance_file"]
OPTIONAL_ARTIFACT_KEYS = ["workflow_file", "workflow_image", "thumbnail_image"]
STRICT_PACKAGE_ARTIFACT_KEYS = ["workflow_file", "workflow_image", "thumbnail_image"]

SECRET_PATTERNS = [
    re.compile(r"(?i)\bGALAXY_API_KEY\b\s*[:=]"),
    re.compile(r"(?i)\bapi[_-]?key\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)\bAuthorization\b\s*:\s*Bearer\s+"),
]
PRIVATE_PATH_PATTERNS = [
    re.compile(r"/Users/[^\s\"']+"),
    re.compile(r"/private/tmp/[^\s\"']+"),
    re.compile(r"/tmp/galaxy_eval_runs/[^\s\"']+"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--workflows-dir", default="workflows", help="Workflow entry directory under root")
    parser.add_argument(
        "--entry",
        action="append",
        default=[],
        help="Entry id or entry directory to validate. Repeatable. Defaults to all entries.",
    )
    parser.add_argument(
        "--strict-package",
        action="store_true",
        help="Require workflow.ga, workflow.svg, and thumbnail.png references.",
    )
    parser.add_argument("--json-output", type=Path, help="Optional machine-readable validation output path")
    return parser.parse_args()


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key:
            data.setdefault(current_list_key, []).append(parse_scalar(stripped[2:]))
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if value.strip() == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = parse_scalar(value)
            current_list_key = None

    return data


def load_metadata(path: Path) -> tuple[dict[str, Any], list[str]]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return dict(loaded), []
        return {}, [f"{path}: metadata did not parse as a mapping"]
    except ModuleNotFoundError:
        return parse_simple_yaml(text), []
    except Exception as exc:
        return parse_simple_yaml(text), [f"{path}: PyYAML parse failed, used simple parser: {exc}"]


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "y"}
    return False


def relative_file(entry_dir: Path, raw: dict[str, Any], key: str) -> Path | None:
    value = raw.get(key)
    if is_blank(value):
        return None
    rel = Path(str(value))
    return entry_dir / rel


def artifact_reference_error(entry_name: str, key: str, value: Any) -> str | None:
    if is_blank(value):
        return None
    rel = Path(str(value))
    if rel.is_absolute():
        return f"{entry_name}: {key} must be a relative path inside the entry, not {rel}"
    if ".." in rel.parts:
        return f"{entry_name}: {key} must not escape the entry directory: {rel}"
    return None


def parse_json_file(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(loaded, dict):
        errors.append(f"{path}: JSON artifact must be an object")
        return None
    return loaded


def scan_public_text(entry_dir: Path, errors: list[str], warnings: list[str]) -> None:
    for path in sorted(entry_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings.append(f"{path}: could not scan non-UTF-8 text artifact")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{path}: possible secret or API credential found")
                break
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                warnings.append(f"{path}: contains a local absolute path; avoid publishing private machine paths")
                break


def validate_artifacts(
    entry_dir: Path,
    raw: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    strict_package: bool,
) -> dict[str, str]:
    artifact_status: dict[str, str] = {}

    for key in REQUIRED_ARTIFACT_KEYS:
        reference_error = artifact_reference_error(entry_dir.name, key, raw.get(key))
        if reference_error:
            errors.append(reference_error)
        path = relative_file(entry_dir, raw, key)
        if path is None:
            errors.append(f"{entry_dir.name}: missing required artifact reference {key}")
            artifact_status[key] = "missing_reference"
            continue
        if not path.is_file():
            errors.append(f"{entry_dir.name}: {key} does not exist: {path}")
            artifact_status[key] = "missing_file"
            continue
        artifact_status[key] = "ok"

        if key in {"validation_file", "provenance_file"}:
            parsed = parse_json_file(path, errors)
            if key == "validation_file" and parsed:
                report_status = str(parsed.get("status") or "").lower()
                metadata_status = str(raw.get("validation_status") or "").lower()
                if report_status and report_status != metadata_status:
                    warnings.append(
                        f"{entry_dir.name}: validation_report status '{report_status}' "
                        f"does not match metadata validation_status '{metadata_status}'"
                    )

    for key in OPTIONAL_ARTIFACT_KEYS:
        reference_error = artifact_reference_error(entry_dir.name, key, raw.get(key))
        if reference_error:
            errors.append(reference_error)
        path = relative_file(entry_dir, raw, key)
        if path is None:
            artifact_status[key] = "not_referenced"
            if strict_package and key in STRICT_PACKAGE_ARTIFACT_KEYS:
                errors.append(f"{entry_dir.name}: strict package requires {key}")
            continue
        if not path.is_file():
            errors.append(f"{entry_dir.name}: {key} does not exist: {path}")
            artifact_status[key] = "missing_file"
            continue
        artifact_status[key] = "ok"

    return artifact_status


def validate_entry(entry_dir: Path, strict_package: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    metadata_path = entry_dir / "metadata.yaml"
    if not metadata_path.is_file():
        errors.append(f"{entry_dir}: missing metadata.yaml")
        return {
            "entry": entry_dir.name,
            "status": "fail",
            "errors": errors,
            "warnings": warnings,
            "artifact_status": {},
        }

    raw, parse_warnings = load_metadata(metadata_path)
    warnings.extend(parse_warnings)

    for key in REQUIRED_METADATA_KEYS:
        if key not in raw:
            errors.append(f"{entry_dir.name}: missing metadata key {key}")
    for key in VALUE_REQUIRED_KEYS:
        if is_blank(raw.get(key)):
            errors.append(f"{entry_dir.name}: metadata key {key} must not be blank")
    if all(is_blank(raw.get(key)) for key in SOURCE_KEYS):
        errors.append(f"{entry_dir.name}: one of source_url or source_ref must be present")

    entry_id = str(raw.get("id") or "")
    if entry_id and entry_id != entry_dir.name:
        errors.append(f"{entry_dir.name}: metadata id '{entry_id}' does not match directory name")

    slug = str(raw.get("slug") or "")
    if slug and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        warnings.append(f"{entry_dir.name}: slug should contain only lowercase letters, numbers, and hyphens")

    validation_status = str(raw.get("validation_status") or "").lower()
    if validation_status and validation_status not in VALIDATION_STATUSES:
        errors.append(
            f"{entry_dir.name}: validation_status '{validation_status}' is not one of {sorted(VALIDATION_STATUSES)}"
        )

    history_url = str(raw.get("galaxy_history_url") or "")
    if history_url and not history_url.startswith(("http://", "https://")):
        errors.append(f"{entry_dir.name}: galaxy_history_url must be an HTTP(S) URL")
    elif history_url and "/histories/" not in history_url:
        warnings.append(f"{entry_dir.name}: galaxy_history_url does not look like a Galaxy history link")

    source_url = str(raw.get("source_url") or "")
    if source_url and not source_url.startswith(("http://", "https://")):
        warnings.append(f"{entry_dir.name}: source_url is not an HTTP(S) URL")

    public = normalize_bool(raw.get("galaxy_history_public"))
    importable = normalize_bool(raw.get("galaxy_history_importable"))
    if public and not importable:
        warnings.append(f"{entry_dir.name}: public histories should normally also be importable for website use")
    if (public or importable) and is_blank(raw.get("galaxy_history_id")):
        warnings.append(f"{entry_dir.name}: public/importable history should record galaxy_history_id")

    tags = raw.get("tags")
    if not isinstance(tags, list):
        warnings.append(f"{entry_dir.name}: tags should be a YAML list")
    elif not tags:
        warnings.append(f"{entry_dir.name}: tags list is empty")

    artifact_status = validate_artifacts(entry_dir, raw, errors, warnings, strict_package)
    scan_public_text(entry_dir, errors, warnings)

    return {
        "entry": entry_dir.name,
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
        "artifact_status": artifact_status,
    }


def resolve_entry_dirs(root: Path, workflows_dir: Path, requested: list[str]) -> list[Path]:
    if not requested:
        return sorted(path for path in workflows_dir.iterdir() if (path / "metadata.yaml").is_file())

    entry_dirs: list[Path] = []
    for item in requested:
        path = Path(item)
        if not path.is_absolute():
            candidate = workflows_dir / item
            path = candidate if candidate.exists() else root / item
        entry_dirs.append(path)
    return entry_dirs


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    workflows_dir = root / args.workflows_dir

    if not workflows_dir.is_dir():
        print(f"ERROR: workflow directory does not exist: {workflows_dir}", file=sys.stderr)
        return 1

    entry_dirs = resolve_entry_dirs(root, workflows_dir, args.entry)
    results = [validate_entry(path, args.strict_package) for path in entry_dirs]
    error_count = sum(len(result["errors"]) for result in results)
    warning_count = sum(len(result["warnings"]) for result in results)
    summary = {
        "entry_count": len(results),
        "error_count": error_count,
        "warning_count": warning_count,
        "strict_package": args.strict_package,
    }
    report = {"summary": summary, "entries": results}

    if args.json_output:
        output_path = args.json_output if args.json_output.is_absolute() else root / args.json_output
        write_json(output_path, report)

    for result in results:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in result["warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)

    print(
        f"Validated {summary['entry_count']} workflow entries "
        f"({summary['error_count']} errors, {summary['warning_count']} warnings)."
    )
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
