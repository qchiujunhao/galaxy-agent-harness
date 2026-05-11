---
description: List Galaxy Analysis Plugin commands, workflow support, validation profiles, templates, and local capabilities.
argument-hint: [optional-filter]
allowed-tools: [Read, Glob, Grep, Bash]
---

# `/galaxy-list`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as an optional filter such as `commands`, `profiles`, `templates`, `packages`, `galaxy-cli`, or `bioartifact`.
2. Read `../HARNESS.md`, this command file, and the relevant guide/template index files.
3. Inspect local availability for `galaxy-cli` and `bioartifact` when the filter asks for capability status.
4. Do not run live Galaxy jobs.
5. Summarize the available slash commands and recommend the next command for the user's goal.

## Purpose

List supported modes, general workflow support, validation profiles, templates, and known submittable workflow packages.

## Accepted Inputs

- no input
- optional filter: modes, workflow support, validation profiles, templates, local packages, submittable items

## Phase Workflow

1. Inspect: read the plugin harness, command docs, guides, templates, and requested local package paths.
2. Summarize: list available capabilities and artifacts.
3. Recommend: identify the command or mode that best matches the user's apparent next action.

## Required Skill Use

This command normally does not require Galaxy execution skills unless listing live Galaxy histories or remote workflow state.

## Output Expectations

- supported commands
- general Galaxy workflow support
- specialized v1 validation profiles
- available templates
- local submission packages if requested

## Failure Handling

If a local package path cannot be read, list plugin capabilities and report the unreadable path separately.
