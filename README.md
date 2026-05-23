# Galaxy Agent Harness

Galaxy Agent Harness contains the `galaxy-analysis-plugin`, a thin Codex plugin for agent-operated Galaxy analysis.

The plugin does not implement a second Galaxy backend. It gives the agent a shared method, slash-command prompts, command contracts, guides, and templates, then delegates real Galaxy operations to `galaxy-cli`.

Workflow coverage is general by default. The named workflow families in the guides are validation profiles with stronger defaults, not the full set of workflows the plugin can attempt.

## Status

The initial scaffold is finished and validated.

Implemented:

- local Codex plugin marketplace entry
- plugin manifest
- Codex skill
- shared harness
- all v1 `/galaxy-*` slash-command prompt files
- `/galaxy-*` command contracts
- task-family and validation guides
- report and workflow-submission templates
- static workflow-site generator
- structure check script

Not implemented yet:

- direct Galaxy backend code
- automated workflow package generator

## Quick Start

### Prerequisites

- Codex Desktop or a Codex build that supports local plugins
- a Codex build that supports plugin-level `commands/` for native slash invocation, or the manual fallback below
- Python 3 for the validation script
- `galaxy-cli` if you want to run real Galaxy jobs
- Galaxy credentials or API configuration for the target instance, if required by those execution tools

### Step 1: Get the Repository

Clone or copy this repository, then enter the repo root:

```bash
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

### Step 3: Enable the Local Plugin in Codex

This repository is laid out as a local Codex plugin marketplace:

```text
.agents/plugins/marketplace.json
plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json
```

The marketplace entry points to:

```text
./plugins/galaxy-analysis-plugin
```

Add the repository as a local Codex marketplace:

```bash
codex plugin marketplace add "$(pwd)"
```

Enable the plugin in `~/.codex/config.toml`:

```toml
[plugins."galaxy-analysis-plugin@galaxy-agent-harness"]
enabled = true
```

Open or restart Codex from the repository root after enabling the plugin.

To verify that the plugin skill is visible in a fresh CLI session:

```bash
codex exec --cd "$(pwd)" --skip-git-repo-check \
  'Check whether the galaxy-analysis plugin skill is available. Do not run Galaxy.'
```

Expected response:

```text
galaxy-analysis-plugin:galaxy-analysis
```

If your Codex build exposes local plugin installation in the UI, you can also install or enable `galaxy-analysis-plugin` from the local marketplace there, then reload the session.

### Step 4: Install `galaxy-cli`

The plugin is a method layer; live Galaxy runs use `galaxy-cli` as the canonical execution surface.

Preferred installation:

```bash
python3 -m pip install galaxy-cli
```

Local development installation when working from a Galaxy checkout:

```bash
python3 -m pip install -e /path/to/cli-galaxy/galaxy-src/agent-harness
```

Verify the executable:

```bash
command -v galaxy-cli
galaxy-cli --version
```

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

Histories are private unless the user explicitly asks to make them public or importable. Final responses and reports must still include the Galaxy history link whenever a history can be resolved.

### Step 6: Configure Optional `bioartifact` Validation

Use `bioartifact` for deterministic local validation after Galaxy outputs are downloaded.

Preferred installation depends on where `bioartifact` is published in your environment. For local development:

```bash
export PYTHONPATH="/path/to/bioartifact/src:$PYTHONPATH"
python3 -m bioartifact --help
```

`bioartifact` does not replace Galaxy job-state validation. Use it together with Galaxy metadata, output inventory, and task-specific checks.

### Step 7: Verify the Plugin Behavior

The plugin ships slash-command markdown files under `plugins/galaxy-analysis-plugin/commands/`.

Start with a command that does not require a live Galaxy connection:

```text
/galaxy-list
```

If your host namespaces plugin commands, use the command entry that resolves to `galaxy-list`. If your Codex build does not expose plugin commands in autocomplete, use the manual fallback section below; the same command text is still routed by the `galaxy-analysis` skill.

Then test the planning path:

```text
/galaxy-reproduce https://github.com/hbctraining/Intro-to-DGE

Focus on reproducing the count-matrix differential expression workflow in Galaxy.
Use data/raw_counts_mouseKO.csv and data/Mov10_full_meta.txt if appropriate.
Start by inspecting the repo, inferring the workflow, and writing a Galaxy reproduction plan before execution.
```

If Galaxy execution skills are available, the agent can continue into execution. If they are not available, it should stop at the planning boundary and report the missing execution capability.

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

This creates `workflows/<entry_id>/`, keeps the history private unless `--public` is supplied, and regenerates `site/` plus `docs/`.

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

## Manual Development Fallback

If the plugin is not visible in your Codex plugin UI yet, you can still test the method layer from this repository by asking Codex to use the skill file directly:

```text
Use the Galaxy Analysis Plugin in plugins/galaxy-analysis-plugin.
Follow plugins/galaxy-analysis-plugin/skills/galaxy-analysis/SKILL.md.
Run /galaxy-list.
```

This does not install the plugin globally, but it exercises the same harness, slash-command docs, guides, and templates.

## Commands

All v1 commands are implemented as plugin-level markdown slash commands with frontmatter and `$ARGUMENTS` handling.

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

For nontrivial tasks, the plugin follows the harness phase model:

1. Inspect the source, datasets, Galaxy history, or package.
2. Infer task family, inputs, outputs, assumptions, and likely Galaxy mapping.
3. Plan the run and validation checks.
4. Execute through Galaxy execution skills when available.
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

This plugin does not include a Galaxy backend. Install `galaxy-cli`, configure Galaxy credentials, then rerun the request.

If `galaxy-cli` is missing:

```bash
python3 -m pip install galaxy-cli
```

If a source checkout fails with `ModuleNotFoundError: No module named 'click'`, install the checkout's Python dependencies or install the package in editable mode from the correct project directory:

```bash
python3 -m pip install -e /path/to/cli-galaxy/galaxy-src/agent-harness
```

If credentials are missing, set `GALAXY_URL` and `GALAXY_API_KEY`, then run:

```bash
galaxy-cli config test
```

### `bioartifact` is unavailable

Install or expose `bioartifact` before local artifact validation. If using a source checkout:

```bash
export PYTHONPATH="/path/to/bioartifact/src:$PYTHONPATH"
python3 -m bioartifact --help
```

### Validation fails

Run the scaffold check:

```bash
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
```

If a workflow package fails validation, inspect the missing files listed by the validation report. A publishable package generally needs `workflow.ga`, `workflow.svg` or image fallback, `metadata.yaml`, `README.md`, and recorded validation status.

## Next Steps

1. Add a workflow package generator for `workflow.ga`, `metadata.yaml`, `README.md`, and validation reports.
2. Test all slash commands in a fresh Codex CLI/Desktop session.
3. Add `/galaxy-upload-workflow` draft entry creation from a completed history.
4. Expand task-family guides and validation depth.
