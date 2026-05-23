#!/usr/bin/env python3
"""Check the Galaxy Analysis Plugin method-layer scaffold."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".codex-plugin/plugin.json",
    "HARNESS.md",
    "skills/galaxy-analysis/SKILL.md",
    "commands/galaxy-analyze.md",
    "commands/galaxy-reproduce.md",
    "commands/galaxy-explain.md",
    "commands/galaxy-validate.md",
    "commands/galaxy-upload-workflow.md",
    "commands/galaxy-submit-workflow.md",
    "commands/galaxy-list.md",
    "guides/task-families.md",
    "guides/validation.md",
    "guides/result-interpretation.md",
    "guides/galaxy-cli-execution.md",
    "guides/workflow-submission.md",
    "guides/workflow-site-format.md",
    "scripts/check_site_consistency.py",
    "scripts/create_workflow_entry.py",
    "scripts/generate_workflow_site.py",
    "scripts/validate_workflow_package.py",
    "templates/analysis-plan-template.md",
    "templates/reproduction-report-template.md",
    "templates/validation-report-template.md",
    "templates/workflow-readme-template.md",
    "templates/workflow-pr-template.md",
    "templates/workflow-metadata-template.yaml",
]

COMMAND_MARKERS = [
    "---",
    "description:",
    "$ARGUMENTS",
    "## Arguments",
    "## Invocation Instructions",
    "## Purpose",
    "## Accepted Inputs",
    "## Phase Workflow",
    "## Required Skill Use",
    "## Output Expectations",
    "## Failure Handling",
]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")

    command_files = [
        path
        for path in sorted((ROOT / "commands").glob("*.md"))
        if not path.name.startswith("_")
    ]

    for path in command_files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{path.relative_to(ROOT)} must start with YAML frontmatter")
        for marker in COMMAND_MARKERS:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)} missing marker: {marker}")
        if path.name != "galaxy-list.md" and "galaxy-cli" not in text:
            errors.append(f"{path.relative_to(ROOT)} must mention galaxy-cli execution skills")

    skill = ROOT / "skills/galaxy-analysis/SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        for rel in ["../../HARNESS.md", "../../commands/", "../../guides/", "../../templates/"]:
            if rel not in text:
                errors.append(f"skill does not reference {rel}")

    for script_name in [
        "scripts/check_site_consistency.py",
        "scripts/create_workflow_entry.py",
        "scripts/generate_workflow_site.py",
        "scripts/validate_workflow_package.py",
    ]:
        script = ROOT / script_name
        if script.is_file() and not script.stat().st_mode & 0o111:
            errors.append(f"{script_name} must be executable")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Galaxy Analysis Plugin structure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
