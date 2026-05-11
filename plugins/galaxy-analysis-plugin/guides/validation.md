# Validation Guide

Validation should inspect real artifacts and produce a controlled status.

## Status Values

- `pass`: required checks passed
- `warning`: usable result with caveats
- `fail`: required checks failed
- `draft`: insufficient evidence for full validation

## Layers

### Mechanical Completion

Check whether jobs finished, expected outputs exist, and required package files are present.

### Structural Validation

Check whether outputs are readable, non-empty, and shaped as expected for their datatype.

Examples:

- tabular files have expected columns
- FASTQ/BAM outputs are present and readable by available tools
- YAML and JSON metadata parse successfully
- workflow package files use expected names

Use `bioartifact` for downloaded local artifacts when an available contract fits the artifact type. `bioartifact` is a deterministic local validation layer, not the only validation layer. Combine it with Galaxy job state, dataset metadata, output inventory, and task-specific expectations.

Record the command, exit status, and JSON output path when `bioartifact` is used.

### Task-Specific Plausibility

Apply task-family expectations from `guides/task-families.md`.

If no named validation profile fits, use `general_galaxy_workflow` and clearly separate:

- generic mechanical and structural validation that was actually performed
- specialized task-family validation that is unavailable or marked `draft`
- assumptions needed before stronger scientific validation can be claimed

### Submission Readiness

For workflow package directories, require:

- `workflow.ga`
- `metadata.yaml`
- `README.md`
- `workflow.svg` or documented image fallback
- recorded validation status

## Reporting

Validation reports should include:

- target
- task family
- status
- checks performed
- warnings
- failures
- evidence
- recommended fixes
