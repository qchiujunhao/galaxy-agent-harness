---
description: Publish or stage a reproduced Galaxy history or workflow entry for the static workflow website.
argument-hint: [history-link-report-or-workflow-target]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# `/galaxy-upload-workflow`

## Arguments

The user invoked this command with: $ARGUMENTS

## Invocation Instructions

When this slash command is invoked:

1. Treat `$ARGUMENTS` as the history, reproduction report, validation report, or workflow target to publish.
2. Read `../HARNESS.md`, this command file, `../guides/workflow-site-format.md`, `../guides/workflow-submission.md`, `../guides/validation.md`, and relevant templates.
3. Use `galaxy-cli` skills for Galaxy history inspection, workflow export, artifact retrieval, and public/importable checks.
4. Keep draft/local entries private unless the user explicitly asks for public access. If the user asks to publish an entry to the public website, make the Galaxy history public and importable before marking the website entry public.
5. Create or update a local website entry under `workflows/<entry_id>/` with `plugins/galaxy-analysis-plugin/scripts/create_workflow_entry.py` when enough metadata is available.
6. Regenerate static site data with `plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py`.
7. If `galaxy-cli` is unavailable or lacks a required operation, record the fallback reason.
8. Return the Galaxy history link whenever a history can be resolved.

## Purpose

Publish a reproduced Galaxy workflow or history entry to the static workflow website.

This command is the publication path for the simple IWC-like registry. The first-class public object is the reproduced Galaxy history. Workflow exports, images, README files, and validation artifacts should be attached when available, but the website can list a reproduced run with only a validated Galaxy history entry.

## Accepted Inputs

- Galaxy history id or history link
- reproduced workflow target from the current session
- local reproduction report or validation report
- source repository, benchmark item, methods section, or workflow description
- desired publication mode: local draft, website entry, or pull request
- optional explicit public-history request; public website publication counts as an explicit public-history request

## Phase Workflow

1. Resolve: identify the reproduced Galaxy history and source context.
2. Verify: confirm the history exists, has outputs, and has a validation status.
3. Gather: collect history link, title, task family/profile, tools, outputs, validation artifacts, and provenance.
4. Package: create or update a website entry under `workflows/<entry_id>/`.
5. Render data: update static site index data such as `site/index.json`, tags, and task-family/profile summaries.
6. Validate: check the entry is internally consistent and does not expose secrets or private local paths.
7. Publish: create a local draft, public website update, or PR only when explicitly requested. Public website updates require public/importable Galaxy histories.
8. Summarize: return website entry path, Galaxy history link, publication status, warnings, and PR link if created.

## Required Skill Use

Use `galaxy-cli` skills for Galaxy history inspection, workflow export, artifact retrieval, and public/importable checks. If `galaxy-cli` lacks a public/importable toggle, use the Galaxy API as a narrow fallback and record that fallback reason.

Use `plugins/galaxy-analysis-plugin/scripts/create_workflow_entry.py` to create draft website entries and `plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py` to regenerate static site metadata and pages. Use GitHub tooling only for PR creation after the entry passes validation or the user accepts draft status.

## Output Expectations

Static website entries should generally include:

- `metadata.yaml`
- `README.md`
- `validation_report.json`
- `provenance.json`
- optional `workflow.ga`
- optional `workflow.svg` or image fallback
- optional `thumbnail.png`

The metadata must include:

- title
- slug
- Galaxy history link
- public/importable status
- source type and source URL when known
- workflow class or validation profile
- validation status
- execution surface, preferably `galaxy-cli`
- summary
- tags

## Validation Expectations

Apply `guides/workflow-site-format.md`, `guides/workflow-submission.md`, and `guides/validation.md`.

Before publication, verify:

- the Galaxy history link is present
- the entry does not contain API keys, emails, private local absolute paths, or unignored run logs
- validation status is `pass`, `warning`, `draft`, or `fail`
- draft/private entries are clearly marked
- public website entries have `galaxy_history_public: true` and `galaxy_history_importable: true`, verified against Galaxy
- website index data can be regenerated from the entry metadata

## Failure Handling

If the history is private and the requested output is only a local draft, keep it private and mark the entry private. If the requested output is the public website, make the history public/importable first; if that cannot be done, stop and report that the website entry cannot be published publicly yet.

If workflow export or image generation is unavailable, publish a history-first entry with explicit missing-artifact warnings. Do not block the website entry solely because `workflow.ga` or `workflow.svg` is missing.

If required metadata is missing, write a draft entry only when useful and clearly list the missing fields.
