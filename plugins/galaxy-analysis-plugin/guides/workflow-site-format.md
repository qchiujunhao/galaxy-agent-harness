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
- regenerate static HTML pages under `docs/`
- optionally create a PR when requested

## Public History Policy

Local draft entries may point to private histories if they are clearly marked private.

Entries published to the public website must point to Galaxy histories that are both public and importable. Before setting `galaxy_history_public: true` and `galaxy_history_importable: true` in metadata, verify the real Galaxy history state. If `galaxy-cli` lacks the needed toggle, use the Galaxy API as a narrow fallback and record that fallback reason in the report.

Create or update a draft entry with:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/create_workflow_entry.py \
  --title "<title>" \
  --source-url "<github-url>" \
  --galaxy-history-url "<history-url>" \
  --summary "<summary>"
```

The entry creator writes `workflows/<entry_id>/metadata.yaml`, `README.md`, `validation_report.json`, and `provenance.json`. It does not make Galaxy histories public; make and verify the Galaxy history public/importable before using `--public --importable` for a public website entry.

Regenerate the website with:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/generate_workflow_site.py
```

The generator reads `workflows/*/metadata.yaml`, writes machine-readable data to `site/`, and writes GitHub Pages-compatible static HTML to `docs/`.

Generated outputs:

- `site/index.json`
- `site/tags.json`
- `site/validation_profiles.json`
- `site/build_report.json`
- `docs/index.html`
- `docs/styles.css`
- `docs/workflows/<slug>/index.html` for each entry

The generator supports history-first entries. A missing `workflow.ga`, `workflow.svg`, or `thumbnail.png` should produce a warning or missing download, not block site generation.

Validate website/package entries with:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/validate_workflow_package.py
```

Use default validation for public website entries. It requires metadata, README, validation report, and provenance, while allowing missing workflow export and diagram artifacts. Use `--strict-package` only when preparing a complete review package that must contain `workflow.ga`, `workflow.svg`, and `thumbnail.png`.

Check that committed generated outputs match the workflow metadata without rewriting the site:

```bash
python3 plugins/galaxy-analysis-plugin/scripts/check_site_consistency.py
```
