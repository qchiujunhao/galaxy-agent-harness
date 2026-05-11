# `/galaxy-analyze`

## Purpose

Analyze user-provided datasets in Galaxy using an inferred or user-provided goal.

## Accepted Inputs

- Galaxy history, dataset, or collection identifiers
- local files intended for upload
- a natural-language analysis goal
- optional metadata such as sample groups, reference genome, paired-end layout, or expected contrasts

## Phase Workflow

1. Inspect: identify input datasets, datatypes, collections, sample names, and available metadata.
2. Infer: choose the task family and identify missing assumptions.
3. Plan: create a concise analysis plan with expected tools, inputs, outputs, and validation checks.
4. Execute: run through available `galaxy-cli` skills.
5. Validate: check mechanical completion, output structure, and task-specific plausibility.
6. Summarize: report outputs, validation status, assumptions, and useful next steps.

## Required Skill Use

Use existing `galaxy-cli` skills or Galaxy execution tools for uploads, history inspection, tool submission, job tracking, and output retrieval. Do not implement Galaxy API calls directly in this command doc.

## Output Expectations

- analysis plan
- list of histories, jobs, and outputs touched
- concise result summary
- validation report or validation summary

## Validation Expectations

Apply `guides/validation.md` and the relevant task-family checks in `guides/task-families.md`.

## Failure Handling

If inputs are ambiguous, state the ambiguity and ask only for the minimum missing metadata needed to avoid a risky run. If Galaxy execution skills are unavailable, stop after the plan and report the missing execution capability.
