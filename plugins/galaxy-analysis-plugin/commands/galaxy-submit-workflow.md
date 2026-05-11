# `/galaxy-submit-workflow`

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

Use `galaxy-cli` skills for workflow export and Galaxy artifact retrieval. Use GitHub tooling only for PR creation and only after the package passes readiness checks or the user accepts draft status.

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
