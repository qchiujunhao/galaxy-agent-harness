---
description: Explain a Galaxy history, job, dataset, output, warning, or failure.
argument-hint: [history-job-dataset-or-failure]
allowed-tools: [Read, Glob, Grep, Bash, WebFetch]
---

# `/galaxy-explain`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as the Galaxy object, output file, failure text, or explanation question.
2. Read `../HARNESS.md`, this command file, and only the relevant result interpretation or validation guides.
3. Use `galaxy-cli` skills for live Galaxy history, job, and dataset inspection.
4. Distinguish direct evidence from inference when explaining failures.
5. Return the Galaxy history link whenever a history can be resolved.

## Purpose

Explain Galaxy histories, outputs, jobs, or failures.

## Accepted Inputs

- Galaxy history id or name
- job id
- dataset id
- output file
- failure message or traceback
- user question about an existing Galaxy run

## Phase Workflow

1. Inspect: gather history, job, tool, parameter, dataset, and stderr/stdout context.
2. Infer: identify what was attempted, what completed, and where the explanation boundary lies.
3. Explain: summarize completed work, interpret outputs, or identify likely failure causes.
4. Recommend: provide concrete next steps, rerun suggestions, or validation actions.

## Required Skill Use

Use `galaxy-cli` skills for history, job, and dataset inspection. For local output files, inspect the file structure directly when available.

## Output Expectations

- short summary of what ran
- key outputs or failure boundary
- likely cause when explaining a failure
- recommended next action

## Validation Expectations

For successful outputs, validate readability and expected structure where possible. For failures, distinguish root cause evidence from inference.

## Failure Handling

If the target object cannot be resolved, report which identifier failed and what alternative identifiers would work.
