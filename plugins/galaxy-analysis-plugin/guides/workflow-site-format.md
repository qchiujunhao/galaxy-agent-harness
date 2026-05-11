# Workflow Site Format

The static site should render reproduced Galaxy histories and optional workflow artifacts from metadata.

This site is intentionally simpler than IWC. It is a lightweight registry of reproduced Galaxy analyses. The primary user-facing object is the Galaxy history link; workflow exports and diagrams are secondary attachments when available.

## Data Source

Read workflow entries from `workflows/*/metadata.yaml`.

Each entry directory represents one reproduced Galaxy history or workflow:

```text
workflows/
  <entry_id>/
    metadata.yaml
    README.md
    validation_report.json
    provenance.json
    workflow.ga optional
    workflow.svg optional
    thumbnail.png optional
```

## Homepage Cards

Cards should show:

- title
- Galaxy history link
- public/private/importable status
- thumbnail if available, otherwise a plain history card
- workflow class or validation profile
- validation badge
- source type
- summary
- tool count or key tools when available

## Detail Pages

Detail pages should show:

- title
- Galaxy history link as the primary action
- public/private/importable status
- workflow image when available
- rendered README
- metadata
- download links
- validation summary
- reproduced outputs summary
- provenance summary

## Filters

Recommended filters:

- workflow class or validation profile
- tags
- validation status
- source type
- public/importable status

## Image Policy

Use `thumbnail.png` on list pages and `workflow.svg` on detail pages when available. SVG is the preferred workflow image because it scales better for detailed diagrams.

Do not require an image to publish a history-first entry.

## Publication Command

`/galaxy-upload-workflow` publishes or stages entries for this site. It should:

- resolve a completed Galaxy history
- gather validation and provenance
- write or update `workflows/<entry_id>/metadata.yaml`
- write or update a human-readable `README.md`
- regenerate static index data under `site/`
- optionally create a PR when requested
