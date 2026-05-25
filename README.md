# Galaxy Agent Harness

Galaxy Agent Harness is an agent-portable method layer for Galaxy analysis. It ships with a Codex plugin adapter today, but the reusable core is plain Markdown: a shared harness, slash-command prompts, command contracts, guides, templates, and an agent skill file that other coding agents can read.

The harness does not implement a second Galaxy backend. It gives the agent a shared method, then delegates real Galaxy operations to `galaxy-cli`.

Use it from Codex, Claude Code, OpenCode, or any coding agent that can read local instruction files. Codex currently has the most complete packaged adapter in this repository; other hosts can use the same files through project skills, custom slash commands, or a direct bootstrap prompt.

Workflow coverage is general by default. The named workflow families in the guides are validation profiles with stronger defaults, not the full set of workflows the plugin can attempt.

Public workflow site: https://qchiujunhao.github.io/galaxy-agent-harness/

## Status

The initial scaffold is finished and validated. A live `galaxy-cli` acceptance run has reproduced the `hbctraining/Intro-to-DGE` count-matrix DESeq2 workflow on usegalaxy.org.

Implemented:

- reusable agent harness
- agent skill instruction file
- all v1 `/galaxy-*` slash-command prompt files
- `/galaxy-*` command contracts
- task-family and validation guides
- report and workflow-submission templates
- Codex local plugin adapter and marketplace entry
- Codex plugin manifest
- static workflow-site generator
- reproduced-workflow website entries under `workflows/`
- workflow entry/package validator
- structure check script

Out of scope today:

- direct Galaxy backend code: the harness does not call the Galaxy API itself or replace `galaxy-cli`; agents should use `galaxy-cli` for live Galaxy work and record any fallback.
- full workflow export/diagram package generation: history-first website entries work now, but automatic generation of complete review bundles with `workflow.ga`, `workflow.svg`, thumbnails, and richer provenance is still roadmap work.

## Terminology

- Agent harness: the reusable instructions in `plugins/galaxy-analysis-plugin/HARNESS.md`, `commands/`, `guides/`, and `templates/`.
- Agent skill: `plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md`, a Markdown instruction entrypoint that tells an agent which harness and command files to load. This is not model training and not Galaxy code.
- Codex skill: the same skill file when it is discovered through Codex's plugin system. The name is host-specific; the file itself is reusable.
- Codex plugin adapter: the `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` packaging that lets Codex discover the harness automatically.
- Galaxy execution surface: `galaxy-cli`, which performs actual Galaxy uploads, history inspection, tool runs, output retrieval, and related operations.

## Quick Start

### Prerequisites

- a coding agent that can read project files, custom instructions, skills, or slash-command Markdown
- Codex Desktop or a Codex build that supports local plugins, only if you want native Codex plugin installation
- Python 3 for the validation script
- PyYAML for workflow metadata parsing by local validation and static-site scripts
- `galaxy-cli` if you want to run real Galaxy jobs
- Galaxy credentials or API configuration for the target instance, if required by those execution tools

### Step 1: Get the Repository

Clone or copy this repository, then enter the repo root:

```bash
git clone https://github.com/qchiujunhao/galaxy-agent-harness.git
cd galaxy-agent-harness
```

If you are already inside the repo root, continue to the next step.


### Step 2: Check the Plugin Layout

```bash
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
```

Expected output:

```text
Galaxy Analysis Plugin structure check passed.
```

### Step 3: Install for Your Agent

Use the installer from the repository root:

```bash
python3 install.py claude
```

Use the agent name you want:

```bash
python3 install.py claude
python3 install.py opencode
python3 install.py generic
python3 install.py codex
```

For Claude Code, the installer writes `.claude/skills/galaxy-analysis/` and `.claude/commands/galaxy-*.md` wrappers.

For OpenCode, the installer writes `.opencode/skills/galaxy-analysis/` and `.opencode/commands/galaxy-*.md` wrappers.

For generic agents, the installer writes `.agents/galaxy-agent-harness.md`, a portable bootstrap instruction file that points the agent to the harness, skill, and command files.

For Codex, the repository already includes the adapter files:

```text
.agents/plugins/marketplace.json
plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json
```

`python3 install.py codex` prints the local marketplace and config steps. Codex still requires enabling the local marketplace in the host, so that path has one host-level step outside the repository.

After installation, restart or reload the agent from the repository root and test:

```text
/galaxy-list
```

You can also install the wrappers and `galaxy-cli` together:

```bash
python3 install.py claude --with-galaxy-cli
```

Use `--force` to overwrite previously generated wrapper files.

### Step 4: Install `galaxy-cli`

The harness is a method layer; live Galaxy runs use `galaxy-cli` as the canonical execution surface.

Use a repo-local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install galaxy-cli
```

This avoids system Python protections such as Homebrew's externally managed environment policy. Do not use `--break-system-packages`.

Local development installation when working from a Galaxy checkout, after activating the venv:

```bash
python -m pip install -e /path/to/cli-galaxy/galaxy-src/agent-harness
```

Verify the executable:

```bash
.venv/bin/galaxy-cli --version
```

If the venv is activated, this should also work:

```bash
galaxy-cli --version
```

Known compatibility note: `galaxy-cli` 1.0.2 may send older upload option values to current usegalaxy.org. If upload fails with `Parameter 'space_to_tab': an invalid option ('No')`, use a newer `galaxy-cli` build that contains the upload fix or apply the temporary venv-local patch described in Troubleshooting. Keep that patch out of committed source.

If `galaxy-cli` is unavailable or lacks a required operation, the plugin should stop at the planning boundary or record an explicit fallback reason.

### Step 5: Configure Galaxy Credentials

Set Galaxy credentials for the target instance:

```bash
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="your-galaxy-api-key"
```

Verify configuration:

```bash
galaxy-cli config test
```

Histories are private unless the user explicitly asks to make them public or importable. Publishing an entry to the public workflow website counts as an explicit request: the Galaxy history should be public and importable before the website entry is marked public. Final responses and reports must still include the Galaxy history link whenever a history can be resolved.

### Step 6: Configure Optional `bioartifact` Validation

Use `bioartifact` for deterministic local validation after Galaxy outputs are downloaded.

Preferred installation depends on where `bioartifact` is published in your environment. For local development from a sibling checkout, install it into the repo-local venv:

```bash
.venv/bin/python -m pip install -e ../bioartifact
.venv/bin/bioartifact --help
.venv/bin/python -m bioartifact --help
```

Use `PYTHONPATH=/path/to/bioartifact/src` only as a temporary fallback when an editable install is not possible.

`bioartifact` does not replace Galaxy job-state validation. Use it together with Galaxy metadata, output inventory, and task-specific checks.

### Step 7: Verify the Plugin Behavior

The harness ships slash-command markdown files under `plugins/galaxy-analysis-plugin/commands/`.

Start with a command that does not require a live Galaxy connection:

```text
/galaxy-list
```

If your host namespaces commands, use the command entry that resolves to `galaxy-list`. If your host does not expose plugin commands in autocomplete, use the manual fallback section below; the same command text is still routed by the `galaxy-analysis` skill.

Then test the planning path:

```text
/galaxy-reproduce https://github.com/hbctraining/Intro-to-DGE

Focus on reproducing the count-matrix differential expression workflow in Galaxy.
Use data/raw_counts_mouseKO.csv and data/Mov10_full_meta.txt if appropriate.
Start by inspecting the repo, inferring the workflow, and writing a Galaxy reproduction plan before execution.
```

If `galaxy-cli` is available and configured, the agent can continue into execution. If it is not available, it should stop at the planning boundary and report the missing execution capability.

For a live smoke test with a public example repository:

```text
Use the galaxy-analysis plugin.
Run /galaxy-reproduce https://github.com/hbctraining/Intro-to-DGE.
Focus on the count-matrix differential-expression workflow.
Create a fresh Galaxy history, run Galaxy tools if possible, and return the Galaxy history link.
```

## Static Workflow Website

`/galaxy-upload-workflow` publishes or stages reproduced histories for a small static website. The site is history-first: a Galaxy history link and metadata are enough for a draft entry; `workflow.ga`, `workflow.svg`, and thumbnails are optional improvements.

Workflow entries live under:

```text
workflows/<entry_id>/
  metadata.yaml
  README.md
  validation_report.json
  provenance.json
  workflow.ga
  workflow.svg
  thumbnail.png
```

Generate machine-readable site data and GitHub Pages-compatible HTML:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py
```

Validate workflow entries before publishing or submitting:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py
```

Validate slash-command prompt contracts:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/check_command_contracts.py
```

Check that committed `site/` and `docs/` outputs still match `workflows/` metadata:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/check_site_consistency.py
```

For a strict review package that must include `workflow.ga`, `workflow.svg`, and `thumbnail.png`:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py \
  --entry workflows/<entry_id> \
  --strict-package
```

Create a draft website entry from a reproduced GitHub-to-Galaxy run:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/create_workflow_entry.py \
  --title "Intro to DGE reproduction" \
  --source-url "https://github.com/hbctraining/Intro-to-DGE" \
  --galaxy-history-url "https://usegalaxy.org/histories/..." \
  --summary "Draft reproduction of the count-matrix differential expression workflow." \
  --validation-status draft \
  --tag rnaseq \
  --tag differential-expression
```

This creates `workflows/<entry_id>/`, keeps the history private unless `--public` is supplied, and regenerates `site/` plus `docs/`. For public website entries, first make and verify the Galaxy history public/importable, then pass `--public --importable` so the metadata matches the real Galaxy state.

Generated outputs:

```text
site/index.json
site/tags.json
site/validation_profiles.json
site/build_report.json
docs/index.html
docs/styles.css
docs/workflows/<slug>/index.html
```

To host the website on GitHub Pages after the repository is public:

1. Push the generated `docs/` directory to `main`.
2. In GitHub, open Settings -> Pages.
3. Set Source to `Deploy from a branch`.
4. Select branch `main` and folder `/docs`.
5. Save and wait for GitHub Pages to publish the site.

The committed `docs/.nojekyll` file keeps GitHub Pages from applying Jekyll processing.

Current public site:

```text
https://qchiujunhao.github.io/galaxy-agent-harness/
```

## Manual Agent Fallback

If native plugin, skill, or command discovery is not available in your agent host, you can still test the method layer from this repository by asking the agent to use the skill file directly:

```text
Use the Galaxy Agent Harness in plugins/galaxy-analysis-plugin.
Follow plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md.
Run /galaxy-list.
```

This does not install a host-native adapter, but it exercises the same harness, slash-command docs, guides, and templates.

## Commands

All v1 commands are implemented as Markdown command prompts with frontmatter and `$ARGUMENTS` handling. Codex can discover them through the plugin adapter; Claude Code, OpenCode, and other agents can use wrapper commands that point to these files.

### `/galaxy-analyze`

Analyze user-provided datasets in Galaxy.

Example:

```text
/galaxy-analyze these paired-end FASTQs with standard QC and trimming
```

### `/galaxy-reproduce`

Reproduce an analysis from a repository, benchmark item, methods section, or workflow description.

Example:

```text
/galaxy-reproduce https://github.com/hbctraining/Intro-to-DGE in Galaxy
```

### `/galaxy-explain`

Explain a Galaxy history, job, output, or failure.

Example:

```text
/galaxy-explain history 123abc and identify the failure boundary
```

### `/galaxy-validate`

Validate a completed run, output set, or workflow submission package.

Example:

```text
/galaxy-validate ./workflows/wf_2026_0001
```

### `/galaxy-submit-workflow`

Package a reproduced Galaxy workflow for review or publication.

Example:

```text
/galaxy-submit-workflow the latest reproduced workflow as a draft package
```

### `/galaxy-upload-workflow`

Publish or stage a reproduced Galaxy history/workflow entry for the static workflow website.

Example:

```text
/galaxy-upload-workflow the latest reproduced history as a draft website entry
```

### `/galaxy-list`

List supported modes, general workflow support, validation profiles, templates, and local package capabilities.

Example:

```text
/galaxy-list
```

## What a Request Does

For nontrivial tasks, the harness follows this phase model:

1. Inspect the source, datasets, Galaxy history, or package.
2. Infer task family, inputs, outputs, assumptions, and likely Galaxy mapping.
3. Plan the run and validation checks.
4. Execute through `galaxy-cli` when available.
5. Validate real outputs or package files.
6. Summarize artifacts, status, assumptions, and warnings.

## Repository Layout

```text
.
  .agents/plugins/marketplace.json
  docs/
  site/
  workflows/
  plugins/
    galaxy-analysis-plugin/
      .codex-plugin/plugin.json
      DESIGN.md
      HARNESS.md
      commands/
      guides/
      templates/
      skills/galaxy-analysis/SKILL.md
      scripts/check_structure.py
      scripts/create_workflow_entry.py
      scripts/generate_workflow_site.py
```

## Development

Run checks after editing command docs, guides, templates, the manifest, or the marketplace entry:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json >/dev/null
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
```

Regenerate the static workflow site after editing `workflows/*/metadata.yaml`:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py
```

## Troubleshooting

### Plugin is not visible in Codex

Check that the marketplace entry exists and points to the plugin directory:

```bash
cat .agents/plugins/marketplace.json
ls plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json
```

Then reload or restart the Codex session.

If a CLI session logs a warning like this:

```text
failed to load plugin: missing or invalid plugin.json ... galaxy-analysis-plugin/templates
```

the local plugin cache is one level too shallow. Rebuild the local cache with a version directory:

```bash
cache_root="$HOME/.codex/plugins/cache/galaxy-agent-harness"
plugin_cache="$cache_root/galaxy-analysis-plugin"
backup="$cache_root/galaxy-analysis-plugin.backup.$(date +%Y%m%d%H%M%S)"

mkdir -p "$cache_root"
if [ -d "$plugin_cache" ]; then
  mv "$plugin_cache" "$backup"
fi

mkdir -p "$plugin_cache/0.1.0"
rsync -a --exclude '__pycache__' \
  plugins/galaxy-analysis-plugin/ \
  "$plugin_cache/0.1.0/"
```

Then restart the Codex session and rerun the plugin visibility check.

### `/galaxy-*` commands do not appear in autocomplete

Verify that the plugin is installed or enabled, then restart the Codex session. The command files live in:

```text
plugins/galaxy-analysis-plugin/commands/
```

Some hosts namespace plugin commands or do not expose plugin `commands/` yet. In that case, use the manual fallback prompt from this README; the `galaxy-analysis` skill still routes `/galaxy-*` text to the same command contracts.

### Galaxy execution does not run

This harness does not include a Galaxy backend. Install `galaxy-cli`, configure Galaxy credentials, then rerun the request.

If `galaxy-cli` is missing:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install galaxy-cli
```

If a source checkout fails with `ModuleNotFoundError: No module named 'click'`, install the checkout's Python dependencies or install the package in editable mode from the correct project directory:

```bash
python3 -m pip install -e /path/to/cli-galaxy/galaxy-src/agent-harness
```

If credentials are missing, set `GALAXY_URL` and `GALAXY_API_KEY`, then run:

```bash
galaxy-cli config test
```

If uploads to usegalaxy.org fail with this error:

```text
Parameter 'space_to_tab': an invalid option ('No') was selected
```

you are likely using `galaxy-cli` 1.0.2 against a Galaxy server that now requires different upload form values. Until a fixed `galaxy-cli` release is installed, a temporary repo-local workaround is to patch only the installed package inside `.venv`:

```bash
python - <<'PY'
from pathlib import Path
target = next(Path(".venv").glob("lib/python*/site-packages/galaxy_cli/utils/galaxy_backend.py"))
text = target.read_text()
text = text.replace('"files_0|space_to_tab": "No"', '"files_0|space_to_tab": "Yes"')
text = text.replace('"files_0|to_posix_lines": "No"', '"files_0|to_posix_lines": "Yes"')
target.write_text(text)
print(target)
PY
```

This modifies only the ignored local venv. Do not commit `.venv/`.

### `bioartifact` is unavailable

Install `bioartifact` into the repo-local venv before local artifact validation. If using a sibling source checkout:

```bash
.venv/bin/python -m pip install -e ../bioartifact
.venv/bin/bioartifact --help
.venv/bin/python -m bioartifact --help
```

If an editable install is not possible, temporarily expose the source checkout with `PYTHONPATH=/path/to/bioartifact/src`.

### Validation fails

Run the scaffold check:

```bash
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
python3 scripts/check_command_contracts.py
```

If a workflow package fails validation, inspect the missing files listed by the validation report. A publishable package generally needs `workflow.ga`, `workflow.svg` or image fallback, `metadata.yaml`, `README.md`, and recorded validation status.

## Next Steps

1. Add a workflow package generator for `workflow.ga`, `workflow.svg`, thumbnails, and richer provenance.
2. Test all slash commands in fresh Codex, Claude Code, and OpenCode sessions.
3. Add more reproduced workflows beyond the DESeq2 acceptance run.
4. Publish the repository and enable GitHub Pages from `/docs`.
