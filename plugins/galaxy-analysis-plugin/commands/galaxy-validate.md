# `/galaxy-validate`

## Purpose

Validate a completed Galaxy run, output set, or workflow submission package without rerunning the analysis.

## Accepted Inputs

- Galaxy history id or name
- output dataset or collection ids
- local output directory
- workflow submission package directory
- expected task family

## Phase Workflow

1. Resolve: identify the validation target and expected task family.
2. Gather: collect metadata, output lists, package files, and relevant logs.
3. Check: apply mechanical, structural, task-specific, and submission-readiness checks.
4. Report: produce a pass, warning, fail, or draft status with evidence.

## Required Skill Use

Use `galaxy-cli` skills when validation depends on Galaxy state. Use filesystem inspection for local packages. Do not mark validation as pass without inspecting real artifacts.

## Output Expectations

- validation status
- checks performed
- evidence for failures or warnings
- recommended fixes

## Validation Expectations

Use controlled statuses: `pass`, `warning`, `fail`, `draft`.

## Failure Handling

If the expected task family is unknown, perform generic mechanical and structural validation, then mark task-specific validation as `draft`.
