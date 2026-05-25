#!/usr/bin/env python3
"""Install local agent adapters for the Galaxy Agent Harness."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


COMMANDS = [
    "galaxy-analyze",
    "galaxy-reproduce",
    "galaxy-explain",
    "galaxy-validate",
    "galaxy-upload-workflow",
    "galaxy-submit-workflow",
    "galaxy-list",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def write_file(path: Path, text: str, *, force: bool, dry_run: bool) -> str:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return f"unchanged {path}"
    if path.exists() and not force:
        return f"kept existing {path} (use --force to overwrite)"
    if dry_run:
        return f"would write {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"wrote {path}"


def command_wrapper(command: str) -> str:
    return f"""---
description: Run /{command} through the Galaxy Agent Harness.
argument-hint: [arguments]
---

Read and follow plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md.
Then read plugins/galaxy-analysis-plugin/commands/{command}.md.
Treat the user arguments as:

$ARGUMENTS
"""


def umbrella_command_wrapper() -> str:
    return """---
description: Run a Galaxy Agent Harness task.
argument-hint: [galaxy-task]
---

Use the galaxy-analysis skill if it is available.
Read and follow plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md.
Treat the user arguments as:

$ARGUMENTS
"""


def skill_wrapper() -> str:
    return """---
name: galaxy-analysis
description: Use the Galaxy Agent Harness for Galaxy analysis, reproduction, explanation, validation, and workflow publication tasks.
---

Read and follow plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md.
For /galaxy-* command text, route to plugins/galaxy-analysis-plugin/commands/.
Use galaxy-cli for live Galaxy execution when available, and record any fallback explicitly.
"""


def generic_bootstrap() -> str:
    return """# Galaxy Agent Harness Bootstrap

Use the Galaxy Agent Harness in this repository.

1. Read `plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md`.
2. Use `plugins/galaxy-analysis-plugin/HARNESS.md` as the operating contract.
3. Route `/galaxy-*` commands to `plugins/galaxy-analysis-plugin/commands/`.
4. Use `galaxy-cli` for live Galaxy execution when available.
5. Record any execution fallback explicitly.
"""


def install_claude(root: Path, *, force: bool, dry_run: bool) -> list[str]:
    messages = [
        write_file(root / ".claude/skills/galaxy-analysis/SKILL.md", skill_wrapper(), force=force, dry_run=dry_run),
        write_file(root / ".claude/commands/galaxy-analysis.md", umbrella_command_wrapper(), force=force, dry_run=dry_run),
    ]
    for command in COMMANDS:
        messages.append(
            write_file(root / f".claude/commands/{command}.md", command_wrapper(command), force=force, dry_run=dry_run)
        )
    return messages


def install_opencode(root: Path, *, force: bool, dry_run: bool) -> list[str]:
    messages = [
        write_file(root / ".opencode/skills/galaxy-analysis/SKILL.md", skill_wrapper(), force=force, dry_run=dry_run),
        write_file(root / ".opencode/commands/galaxy-analysis.md", umbrella_command_wrapper(), force=force, dry_run=dry_run),
    ]
    for command in COMMANDS:
        messages.append(
            write_file(root / f".opencode/commands/{command}.md", command_wrapper(command), force=force, dry_run=dry_run)
        )
    return messages


def install_generic(root: Path, *, force: bool, dry_run: bool) -> list[str]:
    return [
        write_file(root / ".agents/galaxy-agent-harness.md", generic_bootstrap(), force=force, dry_run=dry_run),
    ]


def install_codex(root: Path) -> list[str]:
    return [
        "Codex adapter files are already present:",
        f"  {root / '.agents/plugins/marketplace.json'}",
        f"  {root / 'plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json'}",
        "Run this from the repo root if Codex has not registered the local marketplace yet:",
        '  codex plugin marketplace add "$(pwd)"',
        "Then enable:",
        '  [plugins."galaxy-analysis-plugin@galaxy-agent-harness"]',
        "  enabled = true",
    ]


def install_galaxy_cli(root: Path, *, dry_run: bool) -> list[str]:
    venv = root / ".venv"
    python = venv / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")
    commands = [[sys.executable, "-m", "venv", str(venv)]]
    requirements = root / "requirements.txt"
    if requirements.exists():
        commands.append([str(python), "-m", "pip", "install", "-r", str(requirements)])
    commands.append([str(python), "-m", "pip", "install", "galaxy-cli"])

    messages = []
    for command in commands:
        messages.append(" ".join(command))
        if not dry_run:
            subprocess.run(command, check=True)
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Galaxy Agent Harness adapters for local coding agents.")
    parser.add_argument("agent", choices=["claude", "opencode", "codex", "generic", "all"])
    parser.add_argument("--force", action="store_true", help="overwrite existing generated adapter files")
    parser.add_argument("--dry-run", action="store_true", help="show what would be written")
    parser.add_argument("--with-galaxy-cli", action="store_true", help="also create .venv and install galaxy-cli")
    args = parser.parse_args()

    root = repo_root()
    plugin_skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    if not plugin_skill.is_file():
        print(f"ERROR: expected plugin skill at {plugin_skill}", file=sys.stderr)
        return 1

    messages: list[str] = []
    agents = ["claude", "opencode", "generic"] if args.agent == "all" else [args.agent]
    for agent in agents:
        if agent == "claude":
            messages.extend(install_claude(root, force=args.force, dry_run=args.dry_run))
        elif agent == "opencode":
            messages.extend(install_opencode(root, force=args.force, dry_run=args.dry_run))
        elif agent == "generic":
            messages.extend(install_generic(root, force=args.force, dry_run=args.dry_run))
        elif agent == "codex":
            messages.extend(install_codex(root))

    if args.with_galaxy_cli:
        messages.append("galaxy-cli install commands:")
        messages.extend(install_galaxy_cli(root, dry_run=args.dry_run))

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
