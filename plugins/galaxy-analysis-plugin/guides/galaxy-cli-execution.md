# Galaxy CLI Execution Guide

`galaxy-cli` is the canonical execution surface for this plugin.

The plugin should use `galaxy-cli` for routine Galaxy operations and record the execution surface in plans, reports, validation summaries, and website metadata. Fallback Galaxy APIs or BioBlend scripts are acceptable only when `galaxy-cli` lacks a needed capability or is unavailable in the current environment, and the fallback reason must be recorded.

## Required Preflight

Before a live Galaxy run:

```bash
command -v galaxy-cli
galaxy-cli --version
galaxy-cli config test
```

The environment should provide:

```bash
GALAXY_URL
GALAXY_API_KEY
```

Do not print API key values in logs, reports, or summaries.

## Expected Command Patterns

Create a fresh history before running tools:

```bash
galaxy-cli history create "galaxy-analysis-plugin <task>"
```

Upload local files:

```bash
galaxy-cli dataset upload --history-id <history_id> --file <path> --name <name>
```

Create collections when the Galaxy tool expects a collection:

```bash
galaxy-cli collection create --history-id <history_id> --inputs-json <collection_inputs.json>
```

Run a Galaxy tool with structured inputs:

```bash
galaxy-cli tool run --history-id <history_id> --tool-id <tool_id> --inputs-json <tool_inputs.json>
```

Track jobs and inspect outputs:

```bash
galaxy-cli job show <job_id>
galaxy-cli history show <history_id>
galaxy-cli dataset show <dataset_id>
```

Download outputs for local validation:

```bash
galaxy-cli dataset download <dataset_id> --output <path>
```

Export workflow artifacts when available:

```bash
galaxy-cli workflow export --history-id <history_id> --output workflow.ga
```

## Fallback Rules

Use fallback Galaxy tooling only when one of these is true:

- `galaxy-cli` is not installed in the active environment.
- `galaxy-cli config test` fails and the user asks for a non-executing plan.
- `galaxy-cli` does not expose the required operation.
- A direct Galaxy API check is needed to diagnose a `galaxy-cli` failure.

When a fallback is used, reports must include:

- attempted `galaxy-cli` command or capability
- failure or missing capability
- fallback tool used
- whether fallback changed reproducibility risk

## Output Requirements

Every Galaxy-backed command summary should include:

- Galaxy instance URL
- Galaxy history id and link, or `Galaxy history link: unavailable`
- execution surface: `galaxy-cli` or explicit fallback
- command JSON paths or trace paths when saved
- job ids and output dataset ids when available
- validation status
