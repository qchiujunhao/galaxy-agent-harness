---
description: Validate a completed Galaxy run, output set, or workflow package without rerunning the analysis.
argument-hint: [history-output-package-or-task-family]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# `/galaxy-validate`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as the validation target and any expected task family or profile.
2. Read `../HARNESS.md`, this command file, `../guides/validation.md`, and relevant task-family or submission guides.
3. Use `galaxy-cli` skills when validation depends on live Galaxy state.
4. Use local filesystem inspection for downloaded outputs and submission packages.
5. Apply generic structural validation when no named profile fits, and mark profile-specific validation as draft.
6. If `galaxy-cli` is unavailable or lacks a required operation, record the fallback reason.
7. Return the Galaxy history link whenever a history can be resolved.

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

Use `galaxy-cli` skills when validation depends on Galaxy state. Use filesystem inspection for local packages. Do not mark validation as pass without inspecting real artifacts. If a fallback is required, record the missing `galaxy-cli` capability and fallback used.

## Output Expectations

- validation status
- checks performed
- evidence for failures or warnings
- recommended fixes

## Validation Expectations

Use controlled statuses: `pass`, `warning`, `fail`, `draft`.

## Failure Handling

If the expected task family is unknown, perform generic mechanical and structural validation, then mark task-specific validation as `draft`.
