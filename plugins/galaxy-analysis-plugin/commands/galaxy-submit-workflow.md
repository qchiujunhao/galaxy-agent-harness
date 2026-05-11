---
description: Package a reproduced Galaxy workflow or history for review, local submission, or an explicitly requested PR.
argument-hint: [history-workflow-package-or-source]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# `/galaxy-submit-workflow`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as the reproduced workflow/history target and desired submission mode.
2. Read `../HARNESS.md`, this command file, `../guides/workflow-submission.md`, `../guides/validation.md`, and relevant templates.
3. Prefer `/galaxy-upload-workflow` when the user wants website publication.
4. Use `galaxy-cli` skills for Galaxy history inspection, workflow export, artifact retrieval, and public/importable checks.
5. Generate a local draft package when artifacts are incomplete but useful to review.
6. Create a pull request only when explicitly requested and supported.
7. If `galaxy-cli` is unavailable or lacks a required operation, record the fallback reason.
8. Return the Galaxy history link whenever a history can be resolved.

## Purpose

Package a reproduced Galaxy workflow and submit or stage it for review.

For publishing a reproduced Galaxy history/workflow entry to the static workflow website, prefer `/galaxy-upload-workflow`. This command remains useful for package-centric or PR-centric submission workflows.

## Accepted Inputs

- reproduced workflow target
- Galaxy history or workflow id
- local output directory
- source repository or benchmark reference
- desired mode: draft package, local-only package, or pull request

## Phase Workflow

1. Resolve: identify the reproduced workflow and source context.
2. Gather: export `workflow.ga`, workflow image, validation information, and provenance where available.
3. Generate: create `metadata.yaml`, `README.md`, and optional `validation_report.json`.
4. Package: build a complete workflow entry directory.
5. Validate: check submission readiness.
6. Publish: create a PR only when explicitly requested and supported.
7. Summarize: report package path, status, warnings, and PR link if created.

## Required Skill Use

Use `galaxy-cli` skills for workflow export and Galaxy artifact retrieval. Use GitHub tooling only for PR creation and only after the package passes readiness checks or the user accepts draft status. If a fallback is required, record the missing `galaxy-cli` capability and fallback used.

## Output Expectations

Submission packages should generally include:

- `workflow.ga`
- `workflow.svg` or image fallback
- `metadata.yaml`
- `README.md`
- optional `thumbnail.png`
- optional `validation_report.json`
- optional `provenance.json`

## Validation Expectations

Apply `guides/workflow-submission.md` and `guides/validation.md`. Record `validation_status` and `review_status` in metadata.

## Failure Handling

If required artifacts are missing, generate a draft package only when useful and clearly list missing files. Do not create a PR for an internally inconsistent package unless the user explicitly asks for a draft PR.
