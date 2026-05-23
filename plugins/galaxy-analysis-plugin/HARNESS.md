# Galaxy Analysis Plugin Harness

## 1. Purpose

This file is the single source of truth for how the Galaxy Analysis Plugin operates inside a coding-agent host.

The plugin is a thin host integration layer. It should mainly:

- register or emulate user-facing Galaxy commands
- load this harness and command-specific docs
- assemble user input and relevant context
- inject the resulting instruction set into the host agent session

Actual Galaxy work is performed by the host agent using existing `galaxy-cli` skills. Other Galaxy execution tools are fallbacks only when `galaxy-cli` is unavailable or lacks a required capability, and the fallback reason must be recorded.

## 2. Core Operating Model

The plugin follows this structure:

- host plugin layer: slash-command files, command routing, asset loading, context injection
- shared methodology layer: `HARNESS.md`, `commands/*.md`, `guides/*.md`, `templates/*`
- execution layer: `galaxy-cli` skills
- execution target: Galaxy

This means:

- do not reimplement Galaxy execution logic in the plugin host code
- do not create a second backend parallel to `galaxy-cli`
- do not bypass `galaxy-cli` skills for routine Galaxy operations when those skills support the task
- record the execution surface and any fallback reason in plans, reports, validation summaries, and website metadata
- keep host-specific runtime logic minimal and portable

## 3. Primary Modes

The plugin supports four main modes:

1. analyze: analyze user-provided datasets in Galaxy
2. reproduce: reproduce an analysis from a GitHub repository, benchmark item, methods section, or workflow description
3. explain: explain Galaxy histories, outputs, jobs, and failures
4. upload/publish: publish a reproduced Galaxy history or workflow entry to the static workflow website

Validation is available as a support mode for completed runs and output sets. `/galaxy-upload-workflow` is the preferred website publication command. `/galaxy-submit-workflow` remains an alias for package or PR-style submission work.

## 4. Global Rules

### 4.1 Use `galaxy-cli` Skills as the Execution Authority

The plugin should treat `galaxy-cli` skills as the canonical execution surface for Galaxy operations.

When running local commands from this repository, use the project-local virtual environment. Prefer explicit venv paths such as `.venv/bin/galaxy-cli` and `.venv/bin/python -m bioartifact`, or activate `.venv` before running `galaxy-cli` or `bioartifact`. Do not install Galaxy execution dependencies into the system Python.

The plugin should not:

- duplicate Galaxy execution logic in host code
- invent a second command surface for operations that `galaxy-cli` skills already provide
- scatter ad hoc Galaxy behavior across command docs without anchoring it to skill usage

Fallback Galaxy tooling may be used only when `galaxy-cli` is missing, misconfigured, or lacks the required operation. The final report must state the attempted `galaxy-cli` capability, the fallback used, and the reproducibility impact.

### 4.2 Prefer Phased Execution Over One-Shot Improvisation

For nontrivial tasks, prefer:

1. inspect
2. infer
3. plan
4. execute
5. validate
6. summarize

Do not jump directly into execution if important assumptions are unresolved.

### 4.3 Make Assumptions Explicit

Whenever the agent infers data type, task family, workflow mapping, parameter defaults, or expected outputs, those assumptions must be stated in the response or report.

### 4.4 Prefer Real Execution and Real Validation

The plugin should not stop at a plausible plan when the task requires execution. The agent should:

- execute through `galaxy-cli` skills
- inspect actual produced outputs
- validate artifacts rather than assuming success

### 4.5 Keep Outputs Structured

Prefer reusable artifacts such as:

- analysis plan
- reproduction report
- validation report
- website entry package
- workflow submission package
- submission summary

### 4.6 Always Return the Galaxy History Link

Any command that creates, inspects, executes, validates, or packages Galaxy state must return the Galaxy history link in the final response whenever a history can be resolved.

Rules:

- create a fresh Galaxy history before execution when the task will run Galaxy tools
- record the history id and URL in any plan, report, validation summary, or submission summary
- include the history link even when execution fails after history creation
- if no history can be resolved, explicitly state `Galaxy history link: unavailable` and explain why
- do not report a Galaxy run as complete without a history link

## 5. General Workflow Orchestration

The plugin supports general Galaxy workflows. It should not refuse a workflow only because it is outside a named v1 family.

Use a named validation profile when the request fits one. Otherwise classify the task as `general_galaxy_workflow` and proceed with generic Galaxy workflow orchestration.

Default generic workflow path:

- inspect the source, history, datasets, workflow, or methods
- infer inputs, outputs, tools, and ordering
- identify assumptions and unresolved parameters
- create a Galaxy execution plan
- execute through `galaxy-cli` where possible
- validate mechanical completion and output structure
- add task-specific plausibility checks only when a matching profile exists

Specialized v1 validation profiles:

- short-read QC and trimming
- count-matrix differential expression
- host contamination removal
- simple ATAC-seq peak calling
- Galaxy history or failure explanation

These profiles add stronger defaults and validation checks. They are not the complete set of supported workflow types.

## 6. Standard Phase Model

Unless a command-specific doc overrides this, use this phase model.

### Phase 1: Inspect

Gather context such as datasets, source repositories, workflow descriptions, histories, jobs, and outputs.

### Phase 2: Infer

Determine:

- workflow class or validation profile
- likely inputs and outputs
- required assumptions
- candidate execution path

### Phase 3: Plan

Produce a concise execution plan that includes:

- what will be run
- what inputs are expected
- what outputs are expected
- what assumptions are being made
- what validation will be performed

### Phase 4: Execute

Run the plan through `galaxy-cli` skills. If `galaxy-cli` is unavailable or missing a required operation, either stop at the planning boundary or use a fallback execution surface with an explicit fallback reason. If no execution surface is available, report the missing capability instead of simulating success.

### Phase 5: Validate

Check:

- outputs exist
- outputs are structurally plausible
- task-specific expectations are satisfied where possible

### Phase 6: Summarize

Return:

- what was done
- what was produced
- Galaxy history link, or `unavailable` with reason
- execution surface and fallback reason, if any
- whether validation passed
- remaining warnings or next actions

## 7. Mode-Specific Methodology

### 7.1 Analyze Mode

Analyze mode is used when the user provides datasets and asks for an analysis in Galaxy.

Required behavior:

- inspect dataset type and scope
- infer task family
- identify unresolved assumptions
- propose a plan when the task is nontrivial
- execute through `galaxy-cli` skills
- summarize outputs
- validate results

### 7.2 Reproduce Mode

Reproduce mode is used when the user provides an external source and asks for a Galaxy reproduction.

Supported source types:

- GitHub repository
- benchmark item
- workflow description
- methods section
- structured procedural text

Required behavior:

- inspect the source carefully
- infer workflow structure, inputs, and outputs
- identify deviations or uncertainty
- create a Galaxy reproduction plan
- execute via `galaxy-cli` skills
- validate results
- report deviations from the source when relevant

### 7.3 Explain Mode

Explain mode is used when the user wants interpretation of existing Galaxy state.

Required behavior:

- inspect history, job, or output context
- summarize completed work
- explain outputs or likely failure causes
- recommend next steps

### 7.4 Upload/Publish Mode

Upload/publish mode is used when a reproduced Galaxy history or workflow should be added to the static workflow website.

Required behavior:

- resolve the reproduced Galaxy history or workflow target
- treat the Galaxy history as the primary website object
- gather history link, source context, outputs, validation, and provenance artifacts
- generate metadata and README
- create or update a website entry under `workflows/<entry_id>/`
- attach `workflow.ga`, `workflow.svg`, thumbnails, and downloads when available
- validate readiness before publication
- keep histories private for local draft entries unless the user explicitly asks to make them public/importable
- require public website entries to point to public and importable Galaxy histories; publishing to the public website is explicit permission to make the referenced history public/importable
- optionally create a PR

## 8. Validation Model

Validation is layered.

### 8.1 Mechanical Completion

Check whether:

- required execution steps finished
- expected outputs exist
- workflow export exists if needed

### 8.2 Structural Validation

Check whether:

- output files are readable
- expected output categories are present
- tabular outputs have required columns when known
- workflow submission package files are complete

### 8.3 Task-Specific Plausibility

Check whether:

- outputs are consistent with the chosen task family
- basic task-specific sanity expectations are met

### 8.4 Website Publication Readiness

For upload/publish mode, check whether:

- Galaxy history link exists
- `metadata.yaml` exists and is complete
- `README.md` exists
- validation status is recorded
- public/importable status is recorded
- no API keys, emails, private local paths, or local run logs are included
- `workflow.ga`, `workflow.svg`, or image fallback exists when available, but missing workflow exports should not block a history-first website entry

Validation statuses should use controlled values:

- `pass`
- `warning`
- `fail`
- `draft`

## 9. Expected Artifacts

Depending on the mode, produce one or more of:

- analysis plan
- reproduction report
- validation report
- website entry package
- workflow submission package
- submission summary

A website entry package should generally include:

- `metadata.yaml`
- `README.md`
- validation report
- provenance record
- optional `workflow.ga`
- optional `workflow.svg`
- optional `thumbnail.png`

## 10. Command Doc Contract

Each command file under `commands/*.md` is both a Codex plugin slash-command prompt and an operational contract. It must define:

- YAML frontmatter with a short `description`
- an `$ARGUMENTS` handling section
- command purpose
- accepted inputs and invocation styles
- phase-by-phase workflow
- required use of `galaxy-cli` skills
- fallback policy when `galaxy-cli` cannot perform the operation
- output expectations
- validation expectations
- failure handling rules

Command docs are operational contracts for the host agent.

## 11. Host Integration Rules

Any host integration should:

- keep host code thin
- avoid burying methodology in host-specific source
- reuse the same `HARNESS.md`, command docs, guides, and templates across hosts
- load only the docs needed for the current task

## 12. Submission and Site Publication Rules

The shared workflow repository should store reproduced workflows as complete entries, not just raw `.ga` files.

Each entry should be usable for browsing, downloading, validation review, and GitHub Pages rendering.

Recommended static site behavior:

- read workflow entries from repository metadata
- display cards on the homepage
- show workflow image, README, metadata, and downloads on the detail page
- support filtering by task family, tags, validation status, and source type

Preferred image outputs:

- canonical image: `workflow.svg`
- preview image: `thumbnail.png`

## 13. Error Handling Rules

Distinguish between:

- input errors
- interpretation errors
- planning errors
- execution errors
- validation failures
- submission packaging failures
- publication failures

Responses should state:

- what failed
- in which phase it failed
- what is missing or incorrect
- what the user should do next

## 14. Practical Default Behavior

Unless a command-specific doc says otherwise:

- inspect first
- surface assumptions before risky execution
- use `galaxy-cli` skills for actual Galaxy operations
- validate real outputs
- summarize results clearly
- prefer reusable artifacts over one-off prose
