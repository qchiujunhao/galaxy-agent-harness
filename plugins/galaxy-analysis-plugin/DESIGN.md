# Design Summary

Galaxy Analysis Plugin is best implemented as a thin host integration that injects shared Galaxy methodology into an agent session. It should not become a second Galaxy backend.

## Architecture

- host layer: plugin manifest, skill discovery, slash-command files, command routing, context injection
- method layer: `HARNESS.md`, command contracts, guides, templates
- execution layer: existing `galaxy-cli` skills, with documented fallbacks only when needed
- target: Galaxy histories, tools, datasets, workflows, and exports

## Why This Is a Good Shape

- It keeps workflow knowledge portable across Codex, Claude Code, and future hosts.
- It avoids duplicating Galaxy API behavior that should stay in Galaxy execution skills.
- It gives agents an operational method: inspect, infer, plan, execute, validate, summarize.
- It makes workflow submission a first-class artifact, not just a final chat response.

## Main Risk

Codex plugin-level slash-command discovery can vary by host build. The current v1 ships `commands/*.md` prompt files for every `/galaxy-*` mode, and keeps skill-based routing as the fallback path. Future host integrations should reuse the same method layer instead of duplicating command behavior.

## V1 Scope

- analyze
- reproduce
- explain
- validate
- upload/publish reproduced histories to a static workflow website
- submit workflow packages when package or PR review is needed

V1 workflow coverage:

- general Galaxy workflows by default
- named validation profiles for common workflows

- short-read QC and trimming
- count-matrix differential expression
- host contamination removal
- simple ATAC-seq peak calling
- history and failure explanation

The named profiles are not support limits. They add stronger defaults and validation checks. Workflows outside those profiles should still use the generic inspect, infer, plan, execute, validate, summarize path.

## Roadmap

1. Stabilize the shared method layer.
2. Test and harden host-specific command loading where the host supports it.
3. Add `/galaxy-upload-workflow` for publishing reproduced Galaxy history entries to the static site.
4. Add package generation helpers for workflow submissions.
5. Add GitHub Pages/static registry generation from `workflows/*/metadata.yaml`.
6. Expand validation profiles and validation depth for more workflow families.
