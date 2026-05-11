# Workflow Submission Guide

Workflow submissions are complete reproduction packages, not only Galaxy workflow files.

## Package Layout

```text
workflows/
  wf_YYYY_NNNN/
    workflow.ga
    workflow.svg
    thumbnail.png
    metadata.yaml
    README.md
    validation_report.json
    provenance.json
```

`thumbnail.png`, `validation_report.json`, and `provenance.json` are optional unless required by the target repository.

## Required Metadata

`metadata.yaml` should include:

- `id`
- `title`
- `slug`
- `task_family`
- `source_type`
- `source_ref`
- `source_url`
- `galaxy_instance`
- `submitted_by`
- `submission_date`
- `status`
- `review_status`
- `validation_status`
- `workflow_file`
- `workflow_image`
- `readme_file`
- `tags`
- `summary`

## Readiness Checks

Before publication or PR creation:

- package directory exists
- required files exist
- YAML metadata parses
- metadata file references existing files
- validation status is present
- README explains source, Galaxy mapping, assumptions, and outputs

## Publication Modes

- draft: create the package only
- local-only: create the package in a local output directory
- PR: create the package and open a pull request after readiness checks
