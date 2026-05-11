---
description: Reproduce an external analysis source in Galaxy and report the resulting history, outputs, and validation status.
argument-hint: [repository-methods-workflow-or-benchmark]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# `/galaxy-reproduce`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as the source to reproduce and any user constraints.
2. Read `../HARNESS.md`, this command file, and only the relevant task-family, validation, and template files.
3. Inspect the source before planning Galaxy execution.
4. Use a named validation profile when one fits; otherwise use `general_galaxy_workflow`.
5. Create a fresh Galaxy history before executing Galaxy tools.
6. Use `galaxy-cli` skills as the execution authority for uploads, collections, tool runs, job tracking, and output retrieval.
7. If no Galaxy execution surface is available, stop after the reproduction plan and state the missing capability.
8. Return the Galaxy history link whenever a history can be resolved, including failed or partial runs.

## Purpose

Reproduce an external analysis in Galaxy.

## Accepted Inputs

- GitHub repository or commit
- benchmark item
- methods section
- workflow description
- existing script or notebook
- expected input and output artifacts

## Phase Workflow

1. Inspect: read the source artifact, identify workflow steps, tools, versions, inputs, outputs, and references.
2. Infer: map source operations to a Galaxy task family and candidate Galaxy tools.
3. Plan: produce a Galaxy reproduction plan with assumptions, deviations, and validation checks.
4. Execute: run the reproduction using `galaxy-cli` skills.
5. Validate: compare produced artifacts against expected structure and source semantics.
6. Summarize: generate a reproduction report with deviations and validation status.

## Required Skill Use

Use `galaxy-cli` skills for Galaxy operations. Use repository or file inspection tools for source analysis. Do not translate source workflows into unvalidated Galaxy steps without recording assumptions.

## Output Expectations

- reproduction plan
- executed Galaxy history or workflow reference
- output inventory
- reproduction report
- validation summary

## Validation Expectations

Validation must cover both Galaxy completion and fidelity to the source workflow. Record deviations when the Galaxy equivalent is approximate.

## Failure Handling

If the source lacks required inputs, versions, or parameters, mark the reproduction as draft and state what is missing. If a Galaxy mapping is unavailable, propose the closest supported mapping and identify the scientific impact.
