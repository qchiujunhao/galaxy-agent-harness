# Galaxy Agent Harness

Make Galaxy analyses easier for coding agents to run, explain, validate, and publish.

Galaxy Agent Harness is a portable instruction layer for agents. It gives agents a shared operating method, slash-command prompts, validation guides, and report templates for Galaxy work. It does not replace Galaxy or implement a second Galaxy API backend. Live Galaxy execution goes through `galaxy-cli`.

Use it with Claude Code, OpenCode, Codex, or any agent that can read project files.

Public workflow site: https://qchiujunhao.github.io/galaxy-agent-harness/

## Quick Start

```bash
git clone https://github.com/qchiujunhao/galaxy-agent-harness.git
cd galaxy-agent-harness
python3 install.py
```

This installs the agent adapters and `galaxy-cli` into:

```text
~/.agents/galaxy-analysis/.venv/bin/galaxy-cli
```

At the end of installation, the script offers to save Galaxy server/API credentials. A typical first install looks like this:

```text
Configure Galaxy server/API credentials now? [Y/n]: y
Galaxy profile name [default]: usegalaxy
Galaxy URL [https://usegalaxy.org]:
Galaxy API key (input hidden):
Add another Galaxy instance? [y/N]: n
```

`[default]` means that if you press Enter without typing a profile name, the profile will be named `default`. In the example above, the user typed `usegalaxy`, so the saved profile is named `usegalaxy`.

If you answer `n` to `Add another Galaxy instance?`, setup ends and the last configured profile becomes active.

If you answer `y`, the installer repeats the same questions so you can add another server or another API key:

```text
Add another Galaxy instance? [y/N]: y
Galaxy profile name [default]: eu
Galaxy URL [https://usegalaxy.org]: https://usegalaxy.eu
Galaxy API key (input hidden):
Add another Galaxy instance? [y/N]: n
```

You can also configure credentials later:

```bash
python3 install.py --configure-galaxy
. "$HOME/.agents/galaxy-analysis/env"
$HOME/.agents/galaxy-analysis/.venv/bin/galaxy-cli config test
```

`--configure-galaxy` can add multiple profiles one by one. For each profile it asks for:

- profile name, for example `usegalaxy`, `usegalaxy-lab`, `eu`, `eu-backup-key`, or `private-lab`
- Galaxy URL, for example `https://usegalaxy.org`
- Galaxy API key

On usegalaxy.org, create an API key from the Galaxy web UI:

1. Log in to Galaxy.
2. Open User -> Preferences.
3. Open Manage API key.
4. Create or copy the key.
5. Paste it when `python3 install.py --configure-galaxy` asks for it.

The key is saved to `~/.agents/galaxy-analysis/instances/<profile>.env` with file mode `600`. The active profile is also written to `~/.agents/galaxy-analysis/env`, which agents source before running `galaxy-cli`.

For scripted setup, provide a single instance name:

```bash
python3 install.py --configure-galaxy --instance usegalaxy
```

Each profile is stored separately:

```text
~/.agents/galaxy-analysis/instances/usegalaxy.env
~/.agents/galaxy-analysis/instances/usegalaxy-main.env
~/.agents/galaxy-analysis/instances/usegalaxy-collab.env
~/.agents/galaxy-analysis/instances/eu.env
~/.agents/galaxy-analysis/instances/private-lab.env
```

Multiple API keys for the same Galaxy server are supported. Give each key a different profile name, even if the URL is the same:

```text
Configure Galaxy server/API credentials now? [Y/n]: y
Galaxy profile name [default]: usegalaxy-main
Galaxy URL [https://usegalaxy.org]:
Galaxy API key (input hidden):
Add another Galaxy instance? [y/N]: y
Galaxy profile name [default]: usegalaxy-collab
Galaxy URL [https://usegalaxy.org]:
Galaxy API key (input hidden):
Add another Galaxy instance? [y/N]: n
```

The most recently configured profile becomes active by updating:

```text
~/.agents/galaxy-analysis/env
```

Restart or reload your agent from any project folder, then try:

```text
/galaxy-list
```

If you only want command wrappers and do not want to install `galaxy-cli`, use the lighter install:

```bash
python3 install.py --skip-galaxy-cli
```

For unattended installs that should not ask setup questions:

```bash
python3 install.py --no-prompt
```

## What Install Does

`python3 install.py` writes user-level adapter files by default, so the harness works when your agent is opened in another analysis project.

| Agent | Installed files |
| --- | --- |
| Claude Code | `~/.claude/skills/galaxy-analysis/` and `~/.claude/commands/galaxy-*.md` |
| OpenCode | `~/.config/opencode/skills/galaxy-analysis/` and `~/.config/opencode/commands/galaxy-*.md` |
| Codex | `~/.codex/skills/galaxy-analysis/SKILL.md` |
| Generic agents | `~/.agents/skills/galaxy-analysis/SKILL.md` |

The installer also uses one user-level runtime for Galaxy control-plane tooling:

```text
~/.agents/galaxy-analysis/
  .venv/bin/galaxy-cli
  env
  instances/<name>.env
```

Agents source `~/.agents/galaxy-analysis/env` when it exists, then run `~/.agents/galaxy-analysis/.venv/bin/galaxy-cli`.

This is intentional. Analysis projects often have their own Python environments for notebooks, pipelines, or local tooling. The harness keeps Galaxy control-plane tooling separate so running a Galaxy analysis does not mutate the target project's environment.

Credential handling:

- `python3 install.py --configure-galaxy --instance <profile>` asks for Galaxy URL and API key.
- Each profile is stored in `~/.agents/galaxy-analysis/instances/<profile>.env`.
- The active profile is copied to `~/.agents/galaxy-analysis/env`.
- To keep multiple API keys for the same Galaxy server, create multiple profile names with the same Galaxy URL.
- Credential env files are created with mode `600`.
- Use `python3 install.py --configure-galaxy --write-shell-profile` only if you want new terminals to source it automatically.
- If a user pastes an API key into chat and explicitly asks an agent to save it, the agent should not echo it. It should save it to `~/.agents/galaxy-analysis/env` with mode `600`, or guide the user to run the configure command locally.

Specific installs are available when you want only one adapter:

```bash
python3 install.py claude
python3 install.py opencode
python3 install.py codex
python3 install.py generic
```

To write adapters only into this repository instead of user-level folders:

```bash
python3 install.py --scope project
```

Codex plugin support is also included through the local plugin adapter committed in this repository. `python3 install.py codex` prints the optional Codex marketplace setup steps.

## Use

List capabilities:

```text
/galaxy-list
```

Reproduce an analysis from a repository:

```text
/galaxy-reproduce https://github.com/hbctraining/Intro-to-DGE
```

Analyze provided datasets:

```text
/galaxy-analyze these paired-end FASTQs with standard QC and trimming
```

Explain a Galaxy history or failure:

```text
/galaxy-explain history <history-id-or-url>
```

Validate a completed run or package:

```text
/galaxy-validate workflows/<entry-id>
```

Publish or stage a reproduced history for the static workflow site:

```text
/galaxy-upload-workflow the latest reproduced history as a draft website entry
```

## Why This Exists

Galaxy work has a lot of operational detail: histories, datasets, collections, tool states, provenance, validation, and public sharing rules. Agents need a deterministic contract for that work.

This harness gives the agent that contract:

- inspect before planning
- map inputs and methods to Galaxy tools
- execute through the pinned harness `galaxy-cli` when live Galaxy work is required
- validate real outputs instead of assuming success
- return Galaxy history links
- record fallbacks and unresolved assumptions
- produce reusable reports and website entries

## What Works Now

- Agent-readable harness, skill, commands, guides, and templates
- Global installer for Claude Code, OpenCode, Codex, and generic agents
- Optional Codex local plugin adapter
- Seven `/galaxy-*` command prompts
- General Galaxy workflow orchestration
- Stronger validation profiles for common workflow families
- Static workflow-site generator
- Workflow entry/package validation
- Live `galaxy-cli` acceptance evidence for a DESeq2 reproduction on usegalaxy.org

## Repository Layout

```text
.
  install.py
  .agents/plugins/marketplace.json
  plugins/galaxy-analysis-plugin/
    .codex-plugin/plugin.json
    HARNESS.md
    commands/
    guides/
    skills/galaxy-analysis/SKILL.md
    templates/
    scripts/
  workflows/
  site/
  docs/
```

## Development Checks

Run the core scaffold checks after editing command docs, guides, templates, the manifest, or installer:

```bash
python3 -m py_compile install.py
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json >/dev/null
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
python3 scripts/check_command_contracts.py
```

Regenerate the static workflow site after editing `workflows/*/metadata.yaml`:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py
```

Validate workflow entries:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py
```

## Troubleshooting

If commands do not appear, restart or reload the agent, then run:

```bash
python3 install.py --force
```

If live Galaxy execution does not run, install and configure `galaxy-cli`:

```bash
python3 install.py
python3 install.py --configure-galaxy --instance default
. "$HOME/.agents/galaxy-analysis/env"
$HOME/.agents/galaxy-analysis/.venv/bin/galaxy-cli config test
```

If your host cannot load skills or commands, use the generic bootstrap file:

```text
.agents/galaxy-agent-harness.md
```

Tell the agent to read that file before handling Galaxy tasks.

## License

MIT
