#!/usr/bin/env python3
"""Validate Galaxy Analysis slash-command prompt contracts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMON_SECTIONS = [
    "## Arguments",
    "## Invocation Instructions",
    "## Purpose",
    "## Accepted Inputs",
    "## Phase Workflow",
    "## Required Skill Use",
    "## Output Expectations",
    "## Failure Handling",
]

EXPECTED_COMMANDS: dict[str, dict[str, object]] = {
    "galaxy-analyze.md": {
        "command": "galaxy-analyze",
        "required": [
            "general_galaxy_workflow",
            "Use `galaxy-cli` skills as the execution authority",
            "Return the Galaxy history link whenever a history can be resolved",
            "If `galaxy-cli` is unavailable or lacks a required operation",
            "guides/validation.md",
            "guides/task-families.md",
        ],
    },
    "galaxy-explain.md": {
        "command": "galaxy-explain",
        "required": [
            "Use `galaxy-cli` skills for live Galaxy history, job, and dataset inspection",
            "Distinguish direct evidence from inference",
            "Return the Galaxy history link whenever a history can be resolved",
            "fallback reason",
            "Failure Handling",
        ],
    },
    "galaxy-list.md": {
        "command": "galaxy-list",
        "required": [
            "Do not run live Galaxy jobs",
            "local `galaxy-cli` availability",
            "local `bioartifact` availability",
            "general Galaxy workflow support",
            "specialized v1 validation profiles",
        ],
        "live_execution": False,
    },
    "galaxy-reproduce.md": {
        "command": "galaxy-reproduce",
        "required": [
            "Inspect the source before planning Galaxy execution",
            "Create a fresh Galaxy history before executing Galaxy tools",
            "Use `galaxy-cli` skills as the execution authority",
            "Do not refuse a workflow only because no specialized validation profile exists",
            "Return the Galaxy history link whenever a history can be resolved",
            "general_galaxy_workflow",
        ],
    },
    "galaxy-submit-workflow.md": {
        "command": "galaxy-submit-workflow",
        "required": [
            "Prefer `/galaxy-upload-workflow` when the user wants website publication",
            "Use `galaxy-cli` skills for Galaxy history inspection, workflow export, artifact retrieval",
            "Create a pull request only when explicitly requested",
            "Return the Galaxy history link whenever a history can be resolved",
            "guides/workflow-submission.md",
        ],
    },
    "galaxy-upload-workflow.md": {
        "command": "galaxy-upload-workflow",
        "required": [
            "Create or update a local website entry under `workflows/<entry_id>/`",
            "plugins/galaxy-analysis-plugin/scripts/create_workflow_entry.py",
            "plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py",
            "public and importable",
            "Public website updates require public/importable Galaxy histories",
            "Return the Galaxy history link whenever a history can be resolved",
        ],
    },
    "galaxy-validate.md": {
        "command": "galaxy-validate",
        "required": [
            "Use `galaxy-cli` skills when validation depends on live Galaxy state",
            "Use local filesystem inspection for downloaded outputs and submission packages",
            "Apply generic structural validation when no named profile fits",
            "Use controlled statuses: `pass`, `warning`, `fail`, `draft`",
            "Return the Galaxy history link whenever a history can be resolved",
        ],
    },
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body


def require_contains(path: Path, text: str, needle: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{path.relative_to(ROOT)} missing required text: {needle}")


def validate_frontmatter(path: Path, frontmatter: dict[str, str], errors: list[str]) -> None:
    for key in ["description", "argument-hint", "allowed-tools"]:
        if key not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)} missing frontmatter field: {key}")
    allowed_tools = frontmatter.get("allowed-tools", "")
    if not allowed_tools.startswith("[") or not allowed_tools.endswith("]"):
        errors.append(f"{path.relative_to(ROOT)} allowed-tools must be a bracketed list")
    if "Bash" not in allowed_tools:
        errors.append(f"{path.relative_to(ROOT)} allowed-tools must include Bash for local checks and galaxy-cli")


def validate_command(path: Path, spec: dict[str, object]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    command = str(spec["command"])

    validate_frontmatter(path, frontmatter, errors)
    require_contains(path, body, f"# `/{command}`", errors)
    require_contains(path, body, "$ARGUMENTS", errors)

    for section in COMMON_SECTIONS:
        require_contains(path, body, section, errors)

    for required in spec.get("required", []):
        require_contains(path, body, str(required), errors)

    if spec.get("live_execution", True):
        for required in ["galaxy-cli", "fallback", "history link"]:
            require_contains(path, body.lower(), required.lower(), errors)

    if re.search(r"\bBioBlend\b", body):
        errors.append(f"{path.relative_to(ROOT)} should not mention BioBlend as a command execution path")

    return errors


def main() -> int:
    commands_dir = ROOT / "commands"
    errors: list[str] = []

    actual = {path.name for path in commands_dir.glob("*.md") if not path.name.startswith("_")}
    expected = set(EXPECTED_COMMANDS)
    for missing in sorted(expected - actual):
        errors.append(f"missing command file: commands/{missing}")
    for extra in sorted(actual - expected):
        errors.append(f"unexpected command file: commands/{extra}")

    for filename, spec in sorted(EXPECTED_COMMANDS.items()):
        path = commands_dir / filename
        if path.is_file():
            errors.extend(validate_command(path, spec))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Galaxy Analysis Plugin command contract check passed for {len(EXPECTED_COMMANDS)} commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
