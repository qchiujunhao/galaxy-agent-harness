#!/usr/bin/env python3
"""Install local agent adapters for the Galaxy Agent Harness."""

from __future__ import annotations

import argparse
import getpass
import os
import shlex
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


def runtime_root() -> Path:
    return Path.home() / ".agents/galaxy-analysis"


def credentials_path() -> Path:
    return runtime_root() / "env"


def instances_root() -> Path:
    return runtime_root() / "instances"


def instance_credentials_path(name: str) -> Path:
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name.strip())
    if not safe_name:
        raise SystemExit("ERROR: instance name cannot be empty.")
    return instances_root() / f"{safe_name}.env"


def ask_yes_no(prompt: str, *, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    answer = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


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


def galaxy_cli_path(root: Path) -> Path:
    return runtime_root() / ".venv" / ("Scripts/galaxy-cli.exe" if sys.platform.startswith("win") else "bin/galaxy-cli")


def python_path(root: Path) -> Path:
    return runtime_root() / ".venv" / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")


def command_wrapper(command: str, root: Path) -> str:
    skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    contract = root / f"plugins/galaxy-analysis-plugin/commands/{command}.md"
    cli = galaxy_cli_path(root)
    env = credentials_path()
    return f"""---
description: Run /{command} through the Galaxy Agent Harness.
argument-hint: [arguments]
---

Harness root: {root}
Pinned galaxy-cli: {cli}
Credential env file: {env}

Read and follow {skill}.
Then read {contract}.
For live Galaxy work, source the credential env file if it exists, then use the pinned galaxy-cli above.
Do not install into or modify the current analysis project's `.venv` just to run galaxy-cli.
Treat the user arguments as:

$ARGUMENTS
"""


def umbrella_command_wrapper(root: Path) -> str:
    skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    cli = galaxy_cli_path(root)
    env = credentials_path()
    return """---
description: Run a Galaxy Agent Harness task.
argument-hint: [galaxy-task]
---

""" + f"""Harness root: {root}
Pinned galaxy-cli: {cli}
Credential env file: {env}

Use the galaxy-analysis skill if it is available.
Read and follow {skill}.
For live Galaxy work, source the credential env file if it exists, then use the pinned galaxy-cli above.
Do not install into or modify the current analysis project's `.venv` just to run galaxy-cli.
Treat the user arguments as:

$ARGUMENTS
"""


def skill_wrapper(root: Path) -> str:
    skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    harness = root / "plugins/galaxy-analysis-plugin/HARNESS.md"
    commands = root / "plugins/galaxy-analysis-plugin/commands"
    guides = root / "plugins/galaxy-analysis-plugin/guides"
    templates = root / "plugins/galaxy-analysis-plugin/templates"
    cli = galaxy_cli_path(root)
    env = credentials_path()
    installer = root / "install.py"
    return f"""---
name: galaxy-analysis
description: Use the Galaxy Agent Harness for Galaxy analysis, reproduction, explanation, validation, and workflow publication tasks.
---

Harness root: {root}

Read and follow:
- {skill}
- {harness}

For /galaxy-* command text, route to:
- {commands}

Load only the relevant guides and templates:
- {guides}
- {templates}

Galaxy CLI:
- Pinned executable: {cli}
- Credential env file: {env}
- For live Galaxy work, source `{env}` if it exists, then run `{cli}`.
- Keep galaxy-cli in the harness runtime. Do not install into or modify a target analysis project's virtual environment just to run galaxy-cli.
- If {cli} is missing, tell the user to run: python3 {installer}
- If GALAXY_URL or GALAXY_API_KEY are missing, ask the user to run: python3 {installer} --configure-galaxy --instance <name>
- If the user pastes an API key into chat and explicitly asks to save it, do not echo it. Save it to `{env}` with mode 600, or guide the user to run the configure command locally.
- Record any fallback explicitly when galaxy-cli is unavailable or lacks the required operation.
"""


def generic_bootstrap(root: Path) -> str:
    skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    harness = root / "plugins/galaxy-analysis-plugin/HARNESS.md"
    commands = root / "plugins/galaxy-analysis-plugin/commands"
    cli = galaxy_cli_path(root)
    env = credentials_path()
    installer = root / "install.py"
    return f"""---
name: galaxy-analysis
description: Use the Galaxy Agent Harness for Galaxy analysis, reproduction, explanation, validation, and workflow publication tasks.
---

# Galaxy Agent Harness Bootstrap

Harness root: {root}

1. Read `{skill}`.
2. Use `{harness}` as the operating contract.
3. Route `/galaxy-*` commands to `{commands}`.
4. For live Galaxy work, source `{env}` if it exists, then run `{cli}`.
5. Keep galaxy-cli in the harness runtime. Do not install into or modify a target analysis project's virtual environment just to run galaxy-cli.
6. If `{cli}` is missing, ask the user to run `python3 {installer}`.
7. If GALAXY_URL or GALAXY_API_KEY are missing, ask the user to run `python3 {installer} --configure-galaxy --instance <name>`.
8. If the user pastes an API key into chat and explicitly asks to save it, do not echo it. Save it to `{env}` with mode 600, or guide the user to run the configure command locally.
9. Record any execution fallback explicitly.
"""


def adapter_base(root: Path, agent: str, scope: str) -> Path:
    home = Path.home()
    if scope == "project":
        if agent == "claude":
            return root / ".claude"
        if agent == "opencode":
            return root / ".opencode"
        if agent == "generic":
            return root / ".agents"
        if agent == "codex":
            return root / ".codex"
    else:
        if agent == "claude":
            return home / ".claude"
        if agent == "opencode":
            return home / ".config/opencode"
        if agent == "generic":
            return home / ".agents"
        if agent == "codex":
            return Path.home() / ".codex"
    raise ValueError(f"unsupported adapter target: {agent} {scope}")


def install_claude(root: Path, *, force: bool, dry_run: bool, scope: str) -> list[str]:
    base = adapter_base(root, "claude", scope)
    messages = [
        write_file(base / "skills/galaxy-analysis/SKILL.md", skill_wrapper(root), force=force, dry_run=dry_run),
        write_file(base / "commands/galaxy-analysis.md", umbrella_command_wrapper(root), force=force, dry_run=dry_run),
    ]
    for command in COMMANDS:
        messages.append(
            write_file(base / f"commands/{command}.md", command_wrapper(command, root), force=force, dry_run=dry_run)
        )
    return messages


def install_opencode(root: Path, *, force: bool, dry_run: bool, scope: str) -> list[str]:
    base = adapter_base(root, "opencode", scope)
    messages = [
        write_file(base / "skills/galaxy-analysis/SKILL.md", skill_wrapper(root), force=force, dry_run=dry_run),
        write_file(base / "commands/galaxy-analysis.md", umbrella_command_wrapper(root), force=force, dry_run=dry_run),
    ]
    for command in COMMANDS:
        messages.append(
            write_file(base / f"commands/{command}.md", command_wrapper(command, root), force=force, dry_run=dry_run)
        )
    return messages


def install_generic(root: Path, *, force: bool, dry_run: bool, scope: str) -> list[str]:
    base = adapter_base(root, "generic", scope)
    return [
        write_file(base / "skills/galaxy-analysis/SKILL.md", generic_bootstrap(root), force=force, dry_run=dry_run),
    ]


def install_codex(root: Path, *, force: bool, dry_run: bool, scope: str) -> list[str]:
    base = adapter_base(root, "codex", scope)
    messages = [
        write_file(base / "skills/galaxy-analysis/SKILL.md", skill_wrapper(root), force=force, dry_run=dry_run),
        "Optional Codex plugin adapter files are already present:",
        f"  {root / '.agents/plugins/marketplace.json'}",
        f"  {root / 'plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json'}",
        "For Codex plugin mode, run this from the repo root if Codex has not registered the local marketplace yet:",
        '  codex plugin marketplace add "$(pwd)"',
        "Then enable:",
        '  [plugins."galaxy-analysis-plugin@galaxy-agent-harness"]',
        "  enabled = true",
    ]
    return messages


def install_galaxy_cli(root: Path, *, dry_run: bool) -> list[str]:
    venv = runtime_root() / ".venv"
    python = python_path(root)
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


def shell_source_line() -> str:
    return '[ -f "$HOME/.agents/galaxy-analysis/env" ] && . "$HOME/.agents/galaxy-analysis/env"'


def configure_galaxy_credentials(*, instance: str, dry_run: bool, write_shell_profile: bool) -> list[str]:
    path = instance_credentials_path(instance)
    active_path = credentials_path()
    default_url = os.environ.get("GALAXY_URL", "https://usegalaxy.org")

    if dry_run:
        messages = [
            f"would write private Galaxy credentials to {path}",
            f"would set active Galaxy instance env file at {active_path}",
        ]
        if write_shell_profile:
            messages.append("would append source line to the active shell profile")
        return messages

    if sys.stdin.isatty():
        entered_url = input(f"Galaxy URL [{default_url}]: ").strip()
        galaxy_url = entered_url or default_url
        galaxy_api_key = os.environ.get("GALAXY_API_KEY") or getpass.getpass("Galaxy API key (input hidden): ").strip()
    else:
        galaxy_url = default_url
        galaxy_api_key = os.environ.get("GALAXY_API_KEY", "").strip()

    if not galaxy_api_key:
        raise SystemExit("ERROR: GALAXY_API_KEY is missing. Run interactively or export GALAXY_API_KEY before --configure-galaxy.")

    path.parent.mkdir(parents=True, exist_ok=True)
    env_lines = [
        "# Galaxy Agent Harness credentials",
        "# Generated by install.py. Keep this file private.",
        f"export GALAXY_INSTANCE={shlex.quote(instance)}",
        f"export GALAXY_URL={shlex.quote(galaxy_url)}",
        f"export GALAXY_API_KEY={shlex.quote(galaxy_api_key)}",
        "",
    ]
    path.write_text("\n".join(env_lines), encoding="utf-8")
    path.chmod(0o600)
    active_path.write_text("\n".join(env_lines), encoding="utf-8")
    active_path.chmod(0o600)

    messages = [
        f"wrote private Galaxy credentials to {path}",
        f"set active Galaxy instance env file at {active_path}",
        "set file modes to 600",
    ]
    if write_shell_profile:
        profile = Path.home() / (".zshrc" if os.environ.get("SHELL", "").endswith("zsh") else ".bash_profile")
        line = shell_source_line()
        existing = profile.read_text(encoding="utf-8") if profile.exists() else ""
        if line not in existing:
            with profile.open("a", encoding="utf-8") as handle:
                if existing and not existing.endswith("\n"):
                    handle.write("\n")
                handle.write(f"\n# Galaxy Agent Harness credentials\n{line}\n")
            messages.append(f"appended source line to {profile}")
        else:
            messages.append(f"source line already present in {profile}")
    return messages


def configure_galaxy_credentials_interactive(*, dry_run: bool, write_shell_profile: bool) -> list[str]:
    messages: list[str] = []
    while True:
        instance = input("Galaxy profile name [default]: ").strip() or "default"
        messages.extend(
            configure_galaxy_credentials(
                instance=instance,
                dry_run=dry_run,
                write_shell_profile=write_shell_profile,
            )
        )
        if dry_run or not sys.stdin.isatty() or not ask_yes_no("Add another Galaxy instance?", default=False):
            break
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Galaxy Agent Harness adapters for local coding agents.")
    parser.add_argument(
        "agent",
        nargs="?",
        default="all",
        choices=["claude", "opencode", "codex", "generic", "all"],
        help="agent adapter to install; defaults to all global adapters",
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing generated adapter files")
    parser.add_argument("--dry-run", action="store_true", help="show what would be written")
    parser.add_argument("--skip-galaxy-cli", action="store_true", help="only install agent adapters; do not install galaxy-cli")
    parser.add_argument("--configure-galaxy", action="store_true", help="prompt for one or more Galaxy URL/API key profiles")
    parser.add_argument("--instance", help="named Galaxy instance profile for scripted --configure-galaxy setup")
    parser.add_argument("--no-prompt", action="store_true", help="do not ask optional interactive setup questions")
    parser.add_argument("--write-shell-profile", action="store_true", help="also source the private credential env file from ~/.zshrc or ~/.bash_profile")
    parser.add_argument(
        "--scope",
        choices=["global", "project"],
        default="global",
        help="install adapters globally for all projects or only in this repository; defaults to global",
    )
    args = parser.parse_args()

    root = repo_root()
    plugin_skill = root / "plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md"
    if not plugin_skill.is_file():
        print(f"ERROR: expected plugin skill at {plugin_skill}", file=sys.stderr)
        return 1

    messages: list[str] = []
    agents = ["claude", "opencode", "codex", "generic"] if args.agent == "all" else [args.agent]
    for agent in agents:
        if agent == "claude":
            messages.extend(install_claude(root, force=args.force, dry_run=args.dry_run, scope=args.scope))
        elif agent == "opencode":
            messages.extend(install_opencode(root, force=args.force, dry_run=args.dry_run, scope=args.scope))
        elif agent == "generic":
            messages.extend(install_generic(root, force=args.force, dry_run=args.dry_run, scope=args.scope))
        elif agent == "codex":
            messages.extend(install_codex(root, force=args.force, dry_run=args.dry_run, scope=args.scope))

    if not args.skip_galaxy_cli:
        messages.append("galaxy-cli install commands:")
        messages.extend(install_galaxy_cli(root, dry_run=args.dry_run))

    should_configure = args.configure_galaxy
    if (
        not should_configure
        and not args.no_prompt
        and not args.dry_run
        and sys.stdin.isatty()
        and ask_yes_no("Configure Galaxy server/API credentials now?", default=True)
    ):
        should_configure = True

    if should_configure:
        messages.append("Galaxy credential setup:")
        if args.instance:
            messages.extend(
                configure_galaxy_credentials(
                    instance=args.instance,
                    dry_run=args.dry_run,
                    write_shell_profile=args.write_shell_profile,
                )
            )
        else:
            messages.extend(
                configure_galaxy_credentials_interactive(
                    dry_run=args.dry_run,
                    write_shell_profile=args.write_shell_profile,
                )
            )

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
