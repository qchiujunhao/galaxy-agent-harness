# Project To-Do

This file is maintained across chats for this project. See `TODO.md` for the longer Galaxy Analysis Plugin roadmap.

- [x] 2026-05-23: Add workflow/package validation checks and static-site consistency checks.
- [x] 2026-05-23: Add offline slash-command contract checks for all seven `/galaxy-*` command files.
- [x] 2026-05-23: Inspect `/galaxy-list` command-layer visibility without running live Galaxy jobs.
- [x] 2026-05-23: Record local-only availability checks for `galaxy-cli` and `bioartifact`.
- [x] 2026-05-23: Test the remaining six slash commands in fresh read-only Codex CLI sessions.
- [x] 2026-05-23: Expose `bioartifact` through the repo-local `.venv` without requiring manual `PYTHONPATH`.
- [x] 2026-05-23: Add live `galaxy-cli` metadata evidence for DESeq2 `/galaxy-explain` and `/galaxy-validate`.
- [x] 2026-05-23: Add a live `/galaxy-analyze` FASTQ/FastQC smoke test through `galaxy-cli`.
- [ ] Implement full strict package generation for `workflow.ga`, diagrams, thumbnails, and richer provenance.
- [ ] Verify native Codex Desktop slash-command autocomplete/host registration for all seven commands, if required.
- [ ] Add or reuse a failed-job fixture for `/galaxy-explain`.
- [ ] Continue adding external non-Galaxy reproduced workflow entries.
