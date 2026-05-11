---
name: galaxy-analysis
description: Use when a user asks to analyze data in Galaxy, reproduce an analysis in Galaxy, explain Galaxy histories/jobs/outputs/failures, validate Galaxy results, package reproduced Galaxy workflows, or invokes /galaxy-* commands.
---

# Galaxy Analysis

This skill routes Galaxy analysis requests through the shared Galaxy Analysis Plugin harness. It is a thin orchestration layer, not a Galaxy execution backend.

## Required Reading

For every task:

1. Read `../../HARNESS.md`.
2. Select and read exactly one command prompt/contract from `../../commands/` unless the request spans multiple modes.
3. Read only the relevant guide files from `../../guides/`.
4. Use templates from `../../templates/` when producing durable plans, reports, validation summaries, or workflow submission packages.

## Command Routing

- `/galaxy-analyze` or natural-language data analysis request: `../../commands/galaxy-analyze.md`
- `/galaxy-reproduce` or request to reproduce a workflow/source: `../../commands/galaxy-reproduce.md`
- `/galaxy-explain` or request to explain a history, job, output, or failure: `../../commands/galaxy-explain.md`
- `/galaxy-validate` or request to validate completed outputs: `../../commands/galaxy-validate.md`
- `/galaxy-upload-workflow` or request to publish a reproduction to the static workflow website: `../../commands/galaxy-upload-workflow.md`
- `/galaxy-submit-workflow` or request to package/submit a reproduction package: `../../commands/galaxy-submit-workflow.md`
- `/galaxy-list` or request for capabilities/submittable items: `../../commands/galaxy-list.md`

## Operating Rules

- Use the harness phase model: inspect, infer, plan, execute, validate, summarize.
- Classify the task family before choosing Galaxy tools.
- Make assumptions explicit.
- Use existing `galaxy-cli` skills for real Galaxy operations.
- Use fallback Galaxy execution tools only when `galaxy-cli` is unavailable or lacks the required capability, and record the fallback reason.
- If no Galaxy execution capability is available, stop at the planning or explanation boundary and clearly state what capability is missing.
- Validate real outputs. Do not mark success from a plausible plan alone.
- Keep host-specific behavior thin; workflow methodology belongs in the shared docs.

## Output Style

For nontrivial work, produce a concise plan before execution. Final summaries should include:

- what was inspected
- what was inferred
- what was executed or why execution was not possible
- what artifacts were produced
- validation status
- remaining assumptions or warnings
