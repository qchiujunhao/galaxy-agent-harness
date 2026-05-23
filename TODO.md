# Galaxy Analysis Plugin Long-Run Plan

Last updated: 2026-05-23

## Current Ground Truth

- The Codex plugin package loads as `galaxy-analysis-plugin:galaxy-analysis`.
- The shared method layer exists: `HARNESS.md`, slash-command docs, guides, templates, and a structure check.
- All seven v1 `/galaxy-*` commands have plugin-level `commands/*.md` prompt files with frontmatter and `$ARGUMENTS` handling.
- A static workflow-site generator now writes `site/*.json` and `docs/*.html` from `workflows/*/metadata.yaml`.
- A draft entry creator now writes `workflows/<entry_id>/` records from a GitHub/source URL plus Galaxy history URL and regenerates the website.
- The first reproduced-workflow website entry exists at `workflows/wf_20260523_intro-to-dge-deseq2-reproduction/`.
- The public GitHub repository is live at https://github.com/qchiujunhao/galaxy-agent-harness.
- GitHub Pages is enabled from `main` `/docs` and built at https://qchiujunhao.github.io/galaxy-agent-harness/.
- A live `/galaxy-reproduce` acceptance test ran DESeq2 on usegalaxy.org through `galaxy-cli` and passed.
- Live test evidence is stored under ignored `local/plugin_tests/` directories and should not be published.
- `galaxy-cli` 1.0.2 is installed in the repo-local `.venv`; use `.venv/bin/galaxy-cli` or activate the venv.
- The skill and harness instructions now explicitly require using the project-local `.venv` for `galaxy-cli` and `bioartifact` local commands.
- `galaxy-cli config test` succeeds against usegalaxy.org with the current environment credentials.
- A private `galaxy-cli` smoke history was created on 2026-05-23: https://usegalaxy.org/histories/view?id=bbd44e69cb8906b53497c24c3a2df506
- A private `galaxy-cli` DESeq2 acceptance history was created on 2026-05-23: https://usegalaxy.org/histories/view?id=bbd44e69cb8906b520c2ac86da470003
- The local `.venv` copy of `galaxy-cli` 1.0.2 has a temporary upload compatibility patch for current usegalaxy.org upload options (`space_to_tab` and `to_posix_lines`). Upstream or packaged `galaxy-cli` should carry this fix before broad release instructions are final.
- `bioartifact` exists in a sibling development checkout and can run from source with `PYTHONPATH=/path/to/bioartifact/src`.
- `bioartifact` is useful for artifact validation. The Galaxy DESeq2 raw table is headerless and includes rows with missing p-values; a normalized finite-row validation copy passes the current `de_table` contract.

## Direction Decision

Use `galaxy-cli` as the canonical Galaxy execution surface.

BioBlend should not be used directly by this plugin's acceptance tests or command workflows except as temporary investigation evidence while `galaxy-cli` support is missing. The plugin should remain a thin methodology and orchestration layer, while `galaxy-cli` performs Galaxy operations.

Use `bioartifact` as the deterministic local artifact-validation layer after Galaxy outputs are downloaded or exported.

## Definition of Done for v1

The plugin is v1-ready when all of the following are true:

- A fresh Codex session can load the plugin without manual cache repair.
- All seven v1 slash commands appear or route correctly in a fresh Codex session.
- `/galaxy-list`, `/galaxy-reproduce`, `/galaxy-validate`, and `/galaxy-explain` work through the plugin method layer.
- Live Galaxy execution goes through `galaxy-cli`, not direct BioBlend scripts.
- Every live Galaxy run returns a Galaxy history link.
- Histories are not made public unless the user explicitly asks.
- General Galaxy workflows are supported through a generic inspect, infer, plan, execute, validate, summarize path.
- Named workflow families are treated as validation profiles, not support limits.
- Reproduce mode has at least one passing acceptance run using `galaxy-cli`.
- Validation uses `bioartifact` where local artifacts fit an available contract.
- The README documents installation, `galaxy-cli` setup, Galaxy credentials, `bioartifact` setup, and the acceptance test path.
- The structure check passes.

## Phase 0: Clean Baseline

- [x] Keep only the root `README.md`; do not recreate a plugin-level README.
- [x] Keep test artifacts under `local/plugin_tests/`.
- [x] Keep generated caches, `__pycache__`, and credentials out of the repo.
- [x] Add or verify `.gitignore` entries for Python caches, local virtualenvs, Galaxy run outputs, and downloaded datasets.
- [x] Re-run:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/galaxy-analysis-plugin/.codex-plugin/plugin.json >/dev/null
cd plugins/galaxy-analysis-plugin
python3 scripts/check_structure.py
```

## Phase 1: Install and Prove `galaxy-cli`

Goal: make `galaxy-cli` the real execution path.

- [x] Decide install source:
  - current: repo-local venv with `python -m pip install galaxy-cli`
  - local development option: `python -m pip install -e /path/to/cli-galaxy/galaxy-src/agent-harness`
- [x] Verify the executable:

```bash
.venv/bin/galaxy-cli --version
```

- [x] Configure Galaxy credentials through environment variables:

```bash
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="..."
.venv/bin/galaxy-cli config test
```

- [ ] Copy or install the `galaxy-cli` skill so future Codex sessions can see it:

```text
/path/to/cli-galaxy/galaxy-src/agent-harness/galaxy_cli/skills/SKILL.md
```

- [x] Add a short repo guide, `plugins/galaxy-analysis-plugin/guides/galaxy-cli-execution.md`, with the exact command patterns this plugin expects.
- [x] Update `HARNESS.md` from "galaxy-cli or equivalent" to stricter behavior:
  - use `galaxy-cli` for routine Galaxy actions
  - use fallback tools only when `galaxy-cli` lacks a required capability
  - record fallback reason in the report
- [x] Update command docs to make `galaxy-cli` the explicit execution path.
- [x] Update skill and harness instructions to require the repo-local `.venv` for local `galaxy-cli` and `bioartifact` command execution.

Acceptance check:

```bash
.venv/bin/galaxy-cli history create "galaxy-analysis-plugin cli smoke 2026-05-23"
```

Status: passed. The command returned history id `bbd44e69cb8906b53497c24c3a2df506`.

Galaxy history link: https://usegalaxy.org/histories/view?id=bbd44e69cb8906b53497c24c3a2df506

## Phase 2: Re-run the DESeq2 Acceptance Test Through `galaxy-cli`

Goal: replace the BioBlend acceptance evidence with `galaxy-cli` evidence.

- [x] Recreate the `Intro-to-DGE` test using `galaxy-cli`.
- [x] Generate the same normalized inputs:
  - `KO1.tsv`
  - `KO2.tsv`
  - `KO3.tsv`
  - `KO4.tsv`
  - `WT1.tsv`
  - `WT2.tsv`
  - `WT3.tsv`
  - `WT4.tsv`
  - `ko_wt_sample_sheet.tsv`
- [x] Create a fresh Galaxy history with `galaxy-cli history create`.
- [x] Upload all nine inputs with `galaxy-cli dataset upload`.
- [x] Create the list collection with `galaxy-cli collection create`.
- [x] Run DESeq2 with `galaxy-cli tool run --inputs-json`.
- [x] Confirm the tool result JSON includes final output states.
- [x] Save all command JSON under:

```text
local/plugin_tests/fair_cli_session/
```

- [x] Save:
  - `history_link.txt`
  - `run_summary.json`
  - `galaxy-reproduce-test-report.md`
  - `tool_inputs.json`
  - `tool_result.json`
  - any downloaded result files used for local validation

Acceptance criteria:

- [x] `galaxy-cli` is the only Galaxy execution mechanism used.
- [x] DESeq2 job finishes `ok`.
- [x] Result table output is `ok`.
- [x] Plot output is `ok`.
- [x] Final answer and saved report include the Galaxy history link.
- [x] History is not made public by default.

Status: passed on 2026-05-23.

Galaxy history link: https://usegalaxy.org/histories/view?id=bbd44e69cb8906b520c2ac86da470003

## Phase 3: Integrate `bioartifact` Validation

Goal: make validation deterministic and machine-readable.

Use `bioartifact` for local output files after Galaxy downloads or exports.

Useful existing contracts:

- `de_table` for differential-expression tables
- `fastq` and `paired_fastq` for read inputs
- `sorted_bam` and `indexed_bam` for alignments
- `narrowpeak` for ATAC/ChIP-style peak calls
- `valid_vcf` for variant outputs

Current finding:

- `bioartifact inspect local/plugin_tests/fair_codex_session_after_cache_fix/de_results_preview.tsv` passes as a valid TSV.
- `bioartifact validate ... --contract de_table` fails because the saved Galaxy DESeq2 preview does not have the exact required columns `gene`, `log2FoldChange`, `pvalue`, and `padj`.
- Galaxy DESeq2 reports columns as metadata or display labels such as `GeneID`, `Base mean`, `log2(FC)`, `StdErr`, `Wald-Stats`, `P-value`, and `P-adj`.

Required work:

- [x] Download the full DESeq2 result table in the `galaxy-cli` acceptance run.
- [x] Determine whether the raw Galaxy file includes a header row.
- [x] If the raw file has no header, create a normalized validation copy with explicit columns:

```text
gene
baseMean
log2FoldChange
lfcSE
stat
pvalue
padj
```

- [x] If the raw file has no header or Galaxy-specific headers, either:
  - normalize a copy before validation, or
  - add alias support to `bioartifact`'s `de_table` contract.
- [x] Save `bioartifact` JSON results in the run trace:

```text
local/plugin_tests/fair_cli_session/bioartifact_de_table_contract.json
```

- [x] Update `plugins/galaxy-analysis-plugin/guides/validation.md` to say:
  - use `bioartifact` for downloaded local artifacts
  - do not use it as the only validation layer
  - combine it with Galaxy job state and output metadata

Acceptance criteria:

- [x] The DESeq2 acceptance run has a passing `bioartifact` validation artifact, or a documented warning explaining why only structural table inspection was possible.
- [x] The report includes `bioartifact` command, exit status, and JSON path.

Status: `bioartifact inspect` passes on the raw Galaxy TSV. The strict `de_table` contract passes on `local/plugin_tests/fair_cli_session/deseq2_results.de_table_contract.tsv`, a normalized finite-row validation copy.

## Phase 4: Improve Plugin Documentation and Harness Rules

Goal: remove ambiguity from future runs.

- [x] README must clearly separate:
  - plugin installation
  - `galaxy-cli` installation
  - Galaxy credentials
  - `bioartifact` validation setup
  - live acceptance testing
- [x] README must say that histories are private unless the user asks to publish/import.
- [x] HARNESS must require the Galaxy history link for all Galaxy-backed runs.
- [x] HARNESS must not require public histories.
- [x] HARNESS must require reports to name the execution surface:
  - `galaxy-cli`
  - fallback reason, if any
  - `bioartifact`, if used
- [x] Update `README.md` troubleshooting:
  - `galaxy-cli: command not found`
  - missing `click`
  - `GALAXY_URL` or `GALAXY_API_KEY` missing
  - plugin cache layout warning
  - `bioartifact` not installed

## Phase 5: Mode Completion

Goal: make all v1 modes useful, not just documented.

General workflow requirement:

- [x] Add a generic `general_galaxy_workflow` path to the task-family guide.
- [x] Make `/galaxy-reproduce` and `/galaxy-analyze` avoid refusing workflows only because no specialized profile exists.
- [x] Reports must distinguish generic structural validation from specialized task-family validation.
- [ ] Add at least one acceptance test outside the current named profiles.

### Slash Command Files

- [x] `/galaxy-analyze` command prompt exists.
- [x] `/galaxy-reproduce` command prompt exists.
- [x] `/galaxy-explain` command prompt exists.
- [x] `/galaxy-validate` command prompt exists.
- [x] `/galaxy-submit-workflow` command prompt exists.
- [x] `/galaxy-upload-workflow` command prompt exists.
- [x] `/galaxy-list` command prompt exists.
- [x] Structure check validates command frontmatter and `$ARGUMENTS` handling.
- [ ] Test all seven in a fresh Codex session.

### `/galaxy-list`

- [x] Command prompt exists.
- [x] Test in fresh Codex session.
- [x] Include general workflow support, named validation profiles, and whether `galaxy-cli` and `bioartifact` are available.

### `/galaxy-reproduce`

- [x] Command prompt exists.
- [x] BioBlend-backed DESeq2 test passed.
- [x] `galaxy-cli`-backed DESeq2 test passed.
- [ ] Add at least one non-DESeq2 reproduce test.

### `/galaxy-analyze`

- [x] Command prompt exists.
- [ ] Add a small live or simulated FASTQ analysis test.
- [ ] Use `bioartifact fastq` or `paired_fastq` before upload where local files exist.

### `/galaxy-explain`

- [x] Command prompt exists.
- [ ] Test against the public DESeq2 history.
- [ ] Ensure it can explain:
  - job state
  - inputs
  - outputs
  - warnings
  - failed jobs

### `/galaxy-validate`

- [x] Command prompt exists.
- [ ] Validate the DESeq2 history using Galaxy metadata.
- [x] Validate downloaded DESeq2 output using `bioartifact`.
- [x] Save a validation report and machine-readable validation JSON.

### `/galaxy-submit-workflow`

- [x] Command prompt exists.
- [ ] Implement local package generation.
- [ ] Export or reconstruct `workflow.ga`.
- [ ] Export or generate `workflow.svg`.
- [ ] Generate `metadata.yaml`.
- [ ] Generate workflow README.
- [ ] Generate validation report.
- [ ] Support draft-only package mode before PR mode.

## Phase 6: Workflow Package Generator

Goal: produce reviewable workflow packages.

Required package layout:

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

Tasks:

- [ ] Define package id allocation.
- [ ] Define metadata schema and validation script.
- [ ] Generate package from a completed Galaxy history.
- [ ] Include the Galaxy history link and publication status.
- [ ] Include execution surface metadata:
  - `galaxy-cli` version
  - Galaxy URL
  - tool ids and versions
  - job ids
  - dataset ids
- [ ] Include validation metadata:
  - Galaxy job/output validation
  - `bioartifact` contract results where available
- [ ] Add package validation to `scripts/check_structure.py` or a new script.

Acceptance criteria:

- A reproduced workflow can be packaged locally without a PR.
- Package validation can fail with actionable messages.

## Phase 7: Static Reproduced Workflow Website

Goal: implement a simple static website, similar in spirit to IWC but much smaller, for browsing reproduced Galaxy workflows and histories.

The website should be history-first. A reproduced Galaxy history is enough to create an entry. Workflow exports, diagrams, thumbnails, and downloadable packages improve the entry but should not be mandatory for initial publication.

`/galaxy-upload-workflow` is the command that publishes a reproduced workflow/history to this website. `/galaxy-submit-workflow` can remain as an alias for package/PR-oriented submission, but the product-facing command should be `/galaxy-upload-workflow`.

- [x] Generate `site/index.json` from `workflows/*/metadata.yaml`.
- [x] Generate `site/tags.json`.
- [x] Generate `site/task_families.json` or `site/validation_profiles.json`.
- [x] Generate simple static pages under `docs/`.
- [x] Render workflow cards with:
  - title
  - Galaxy history link
  - public/private/importable status
  - workflow class or validation profile
  - validation badge
  - source URL
  - thumbnail when available
- [x] Render workflow detail pages with:
  - Galaxy history link as the primary action
  - public/private/importable status
  - full workflow image when available
  - README content
  - metadata
  - validation summary
  - download links
- [x] Add `/galaxy-upload-workflow` local website-entry generation support:
  - resolve completed Galaxy history
  - collect source, validation, and provenance metadata
  - create or update `workflows/<entry_id>/`
  - regenerate static site index data
- [x] Publish the static site through GitHub Pages from `/docs`.
- [ ] Add `/galaxy-upload-workflow` PR publishing support when requested.
- [x] Define minimum website entry metadata:
  - id
  - title
  - slug
  - Galaxy history URL
  - public/importable status
  - source URL or source description
  - workflow class or validation profile
  - validation status
  - summary
  - tags
  - created/updated date

Acceptance criteria:

- [x] A local static website can be generated from one reproduced Galaxy history entry.
- [x] The website can show entries even when `workflow.ga` or `workflow.svg` is missing.
- [x] `/galaxy-upload-workflow` can create a draft website entry without making the Galaxy history public.

Status: the first generated entry is `workflows/wf_20260523_intro-to-dge-deseq2-reproduction/`.

## Phase 8: Test Matrix

Goal: make regressions obvious.

Tests to keep:

- [x] Structure check for plugin files.
- [x] Plugin load check in fresh Codex session.
- [x] `galaxy-cli` availability check.
- [x] `bioartifact` availability check.
- [ ] Offline docs consistency check.
- [x] Live `galaxy-cli` DESeq2 acceptance test.
- [ ] Public-history toggle test only when explicitly requested.
- [ ] Package generation test.
- [x] Registry generation test.

Evidence policy:

- Store live-run evidence under `local/plugin_tests/<run_name>/`.
- Every live Galaxy test must write `history_link.txt`.
- Every run report must say whether the history is public or private.
- Do not expose API keys in logs or reports.

## Phase 9: Design Completion Estimate

Current completion against the original `design.md`: about 75%.

Target completion after Phase 3: done.

Target completion after Phase 6: about 80%.

Target completion after Phase 7: about 90%.

The last 10% is polish, broader task-family coverage, deeper validation, and host-native command support where Codex exposes it.

## Immediate Next Tasks

1. Decide whether the current DESeq2 Galaxy history should be made public/importable for the website.
2. Add a generic workflow acceptance test outside the current named profiles.
3. Add upstream/package work for the `galaxy-cli` upload option compatibility fix.
4. Add workflow package generation for `workflow.ga`, diagrams, thumbnails, and richer provenance.
5. Test the remaining slash commands in a fresh Codex CLI/Desktop session.
6. Add more website entries once additional reproductions pass validation.
