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

At minimum, a history-first website entry must also record:

- `galaxy_history_url`
- `galaxy_history_public`
- `galaxy_history_importable`
- `execution_surface`
- `validation_profile`
- `validation_file`
- `provenance_file`

`workflow_file`, `workflow_image`, and `thumbnail_image` may be `null` for a history-first entry. They are required only for a strict review package.

## Readiness Checks

Before publication or PR creation:

- package directory exists
- required files exist
- YAML metadata parses
- metadata file references existing files
- validation status is present
- README explains source, Galaxy mapping, assumptions, and outputs

Run the package validator from the repository root:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py
```

Validate one entry:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py \
  --entry workflows/<entry_id>
```

Require a complete strict package with `workflow.ga`, `workflow.svg`, and `thumbnail.png`:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py \
  --entry workflows/<entry_id> \
  --strict-package
```

The validator checks metadata shape, relative artifact references, JSON artifacts, public/importable metadata consistency, and obvious secret or private-path leaks. Website publication can proceed with a history-first entry that passes the default validator. PR-oriented package submission should pass `--strict-package` unless the user explicitly asks for a draft package.

## Publication Modes

- draft: create the package only
- local-only: create the package in a local output directory
- PR: create the package and open a pull request after readiness checks
