# `/galaxy-reproduce`

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
