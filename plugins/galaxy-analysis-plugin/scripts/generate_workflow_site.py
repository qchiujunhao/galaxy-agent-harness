#!/usr/bin/env python3
"""Generate a small static website for reproduced Galaxy workflow entries."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_STATUSES = {"pass", "warning", "fail", "draft", "unknown"}
ARTIFACT_FIELDS = {
    "workflow_file": "workflow",
    "workflow_image": "workflow image",
    "thumbnail_image": "thumbnail",
    "validation_file": "validation report",
    "provenance_file": "provenance",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--workflows-dir", default="workflows", help="Workflow entry directory under root")
    parser.add_argument("--site-dir", default="site", help="Machine-readable site data directory under root")
    parser.add_argument("--docs-dir", default="docs", help="Static HTML output directory under root")
    parser.add_argument("--generated-at", help="Override generated_at timestamp for deterministic checks")
    parser.add_argument("--strict", action="store_true", help="Fail when an entry has validation warnings")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "workflow"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key:
            data.setdefault(current_list_key, []).append(parse_scalar(stripped[2:]))
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if value.strip() == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = parse_scalar(value)
            current_list_key = None

    return data


def load_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return dict(loaded)
    except Exception:
        pass
    return parse_simple_yaml(text)


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "y"}
    return False


def normalize_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def entry_from_metadata(entry_dir: Path, metadata_path: Path) -> tuple[dict[str, Any], list[str]]:
    raw = load_metadata(metadata_path)
    warnings: list[str] = []

    entry_id = str(raw.get("id") or entry_dir.name)
    title = str(raw.get("title") or entry_id)
    slug = slugify(str(raw.get("slug") or title or entry_id))
    validation_status = str(raw.get("validation_status") or raw.get("status") or "unknown").lower()
    if validation_status not in VALIDATION_STATUSES:
        warnings.append(f"{entry_id}: validation_status '{validation_status}' is not one of {sorted(VALIDATION_STATUSES)}")
        validation_status = "unknown"

    galaxy_history_url = str(raw.get("galaxy_history_url") or "").strip()
    if not galaxy_history_url:
        warnings.append(f"{entry_id}: missing galaxy_history_url")

    workflow_class = str(
        raw.get("workflow_class")
        or raw.get("task_family")
        or raw.get("validation_profile")
        or "general_galaxy_workflow"
    )

    summary = str(raw.get("summary") or "").strip()
    if not summary:
        warnings.append(f"{entry_id}: missing summary")

    source_url = str(raw.get("source_url") or "").strip()
    source_ref = str(raw.get("source_ref") or raw.get("source_description") or "").strip()
    if not source_url and not source_ref:
        warnings.append(f"{entry_id}: missing source_url or source_ref")

    entry = {
        "id": entry_id,
        "title": title,
        "slug": slug,
        "summary": summary,
        "entry_dir": entry_dir.name,
        "workflow_class": workflow_class,
        "task_family": raw.get("task_family") or workflow_class,
        "validation_profile": raw.get("validation_profile") or workflow_class,
        "validation_status": validation_status,
        "review_status": raw.get("review_status") or "draft",
        "source_type": raw.get("source_type") or "unknown",
        "source_ref": source_ref,
        "source_url": source_url,
        "galaxy_instance": raw.get("galaxy_instance") or "",
        "galaxy_history_url": galaxy_history_url,
        "galaxy_history_id": raw.get("galaxy_history_id") or "",
        "galaxy_history_public": normalize_bool(raw.get("galaxy_history_public")),
        "galaxy_history_importable": normalize_bool(raw.get("galaxy_history_importable")),
        "execution_surface": raw.get("execution_surface") or "unknown",
        "created": raw.get("created") or raw.get("submission_date") or "",
        "updated": raw.get("updated") or "",
        "tags": normalize_tags(raw.get("tags")),
        "readme_file": raw.get("readme_file") or "README.md",
        "metadata_file": "metadata.yaml",
    }

    for field in ARTIFACT_FIELDS:
        entry[field] = raw.get(field)

    return entry, warnings


def load_entries(workflows_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not workflows_dir.exists():
        return entries, warnings

    for metadata_path in sorted(workflows_dir.glob("*/metadata.yaml")):
        entry, entry_warnings = entry_from_metadata(metadata_path.parent, metadata_path)
        entries.append(entry)
        warnings.extend(entry_warnings)

    entries.sort(key=lambda item: (str(item.get("title", "")).lower(), str(item.get("id", ""))))
    return entries, warnings


def relative_artifact(entry: dict[str, Any], field: str) -> str | None:
    value = entry.get(field)
    if not value:
        return None
    return str(value)


def copy_entry_artifacts(workflows_dir: Path, docs_dir: Path, entry: dict[str, Any]) -> dict[str, str]:
    source_dir = workflows_dir / str(entry["entry_dir"])
    files_dir = docs_dir / "workflows" / str(entry["slug"]) / "files"
    copied: dict[str, str] = {}

    for field in ["metadata_file", "readme_file", *ARTIFACT_FIELDS.keys()]:
        rel = relative_artifact(entry, field)
        if not rel:
            continue
        src = source_dir / rel
        if not src.is_file():
            continue
        files_dir.mkdir(parents=True, exist_ok=True)
        dst = files_dir / src.name
        shutil.copy2(src, dst)
        copied[field] = f"files/{dst.name}"

    return copied


def md_to_html(markdown: str) -> str:
    parts: list[str] = []
    in_list = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        if line.startswith("### "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{html.escape(line)}</p>")

    if in_list:
        parts.append("</ul>")
    return "\n".join(parts)


def load_json_artifact(source_dir: Path, entry: dict[str, Any], field: str) -> dict[str, Any] | None:
    value = entry.get(field)
    if not value:
        return None
    path = source_dir / str(value)
    if not path.is_file():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(loaded, dict):
        return loaded
    return None


def link_or_text(value: Any) -> str:
    text = str(value or "")
    escaped = html.escape(text)
    if text.startswith(("http://", "https://")):
        return f'<a href="{escaped}">{escaped}</a>'
    return escaped


def compact_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def has_display_value(value: Any) -> bool:
    return value is not None and value != ""


def validation_summary_html(data: dict[str, Any] | None) -> str:
    if not data:
        return "<p>No validation report was parsed for this entry.</p>"

    status = html.escape(str(data.get("status") or "unknown"))
    profile = html.escape(str(data.get("profile") or "unknown"))
    checks = data.get("checks") if isinstance(data.get("checks"), list) else []
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []

    parts = [
        '<table class="summary-table">',
        f"<tr><th>Status</th><td>{status}</td></tr>",
        f"<tr><th>Profile</th><td>{profile}</td></tr>",
        f"<tr><th>Checks</th><td>{len(checks)}</td></tr>",
        "</table>",
    ]

    if checks:
        rows = []
        for check in checks:
            if isinstance(check, dict):
                name = html.escape(str(check.get("name") or "check"))
                check_status = html.escape(str(check.get("status") or "unknown"))
                details = {
                    key: value
                    for key, value in check.items()
                    if key not in {"name", "status"} and has_display_value(value)
                }
                detail_text = html.escape(compact_json(details)) if details else ""
                rows.append(f"<tr><td>{name}</td><td>{check_status}</td><td>{detail_text}</td></tr>")
        parts.append("<h3>Checks</h3>")
        parts.append("<table><tr><th>Name</th><th>Status</th><th>Details</th></tr>")
        parts.extend(rows)
        parts.append("</table>")

    if warnings:
        parts.append("<h3>Warnings</h3>")
        parts.append("<ul>")
        for warning in warnings:
            parts.append(f"<li>{html.escape(str(warning))}</li>")
        parts.append("</ul>")

    return "\n".join(parts)


def provenance_summary_html(data: dict[str, Any] | None) -> str:
    if not data:
        return "<p>No provenance report was parsed for this entry.</p>"

    rows = []
    for key in ["execution_surface", "created", "source_url", "source_ref", "galaxy_history_url"]:
        value = data.get(key)
        if has_display_value(value):
            rows.append(f"<tr><th>{html.escape(key)}</th><td>{link_or_text(value)}</td></tr>")
    parts = ["<table class=\"summary-table\">", *rows, "</table>"] if rows else []

    tool_ids = data.get("tool_ids")
    if isinstance(tool_ids, dict) and tool_ids:
        parts.append("<h3>Galaxy Tools</h3>")
        parts.append("<table><tr><th>Name</th><th>Tool ID</th></tr>")
        for name, tool_id in sorted(tool_ids.items()):
            parts.append(f"<tr><td>{html.escape(str(name))}</td><td>{html.escape(str(tool_id))}</td></tr>")
        parts.append("</table>")

    fallbacks = data.get("fallbacks")
    if isinstance(fallbacks, list) and fallbacks:
        parts.append("<h3>Fallbacks</h3>")
        parts.append("<ul>")
        for fallback in fallbacks:
            parts.append(f"<li>{html.escape(str(fallback))}</li>")
        parts.append("</ul>")

    input_urls = data.get("input_urls")
    if isinstance(input_urls, dict) and input_urls:
        parts.append("<h3>Input Sources</h3>")
        parts.append("<table><tr><th>Name</th><th>URL</th></tr>")
        for name, url in sorted(input_urls.items()):
            parts.append(f"<tr><td>{html.escape(str(name))}</td><td>{link_or_text(url)}</td></tr>")
        parts.append("</table>")

    return "\n".join(parts) if parts else "<p>No displayable provenance fields were found.</p>"


def status_label(entry: dict[str, Any]) -> str:
    public = "public" if entry.get("galaxy_history_public") else "private"
    importable = "importable" if entry.get("galaxy_history_importable") else "not importable"
    return f"{public}, {importable}"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def build_summary(entries: list[dict[str, Any]], warnings: list[str], generated_at: str | None = None) -> dict[str, Any]:
    tag_counts: dict[str, int] = {}
    profile_counts: dict[str, int] = {}
    validation_counts: dict[str, int] = {}

    for entry in entries:
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        profile = str(entry.get("validation_profile") or entry.get("workflow_class") or "unknown")
        profile_counts[profile] = profile_counts.get(profile, 0) + 1
        status = str(entry.get("validation_status") or "unknown")
        validation_counts[status] = validation_counts.get(status, 0) + 1

    return {
        "generated_at": generated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "entry_count": len(entries),
        "warning_count": len(warnings),
        "validation_statuses": validation_counts,
        "tags": tag_counts,
        "validation_profiles": profile_counts,
    }


def index_record(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "title": entry["title"],
        "slug": entry["slug"],
        "summary": entry["summary"],
        "workflow_class": entry["workflow_class"],
        "task_family": entry["task_family"],
        "validation_profile": entry["validation_profile"],
        "validation_status": entry["validation_status"],
        "review_status": entry["review_status"],
        "source_type": entry["source_type"],
        "source_ref": entry["source_ref"],
        "source_url": entry["source_url"],
        "galaxy_instance": entry["galaxy_instance"],
        "galaxy_history_url": entry["galaxy_history_url"],
        "galaxy_history_public": entry["galaxy_history_public"],
        "galaxy_history_importable": entry["galaxy_history_importable"],
        "execution_surface": entry["execution_surface"],
        "tags": entry["tags"],
        "created": entry["created"],
        "updated": entry["updated"],
        "page_url": f"workflows/{entry['slug']}/",
    }


def write_site_data(
    site_dir: Path,
    entries: list[dict[str, Any]],
    warnings: list[str],
    generated_at: str | None = None,
) -> None:
    records = [index_record(entry) for entry in entries]
    summary = build_summary(entries, warnings, generated_at)
    write_json(site_dir / "index.json", {"summary": summary, "entries": records})
    write_json(site_dir / "tags.json", summary["tags"])
    write_json(site_dir / "validation_profiles.json", summary["validation_profiles"])
    write_json(site_dir / "build_report.json", {"summary": summary, "warnings": warnings})


def page_shell(title: str, body: str, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
  {body}
</body>
</html>
"""


def write_styles(docs_dir: Path) -> None:
    styles = """
:root {
  color-scheme: light;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #172033;
  background: #f7f8fb;
}
body {
  margin: 0;
}
a {
  color: #165dba;
}
.wrap {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
}
.hero {
  padding: 40px 0 24px;
  border-bottom: 1px solid #d9deea;
  background: #ffffff;
}
.hero h1 {
  margin: 0 0 8px;
  font-size: 30px;
  line-height: 1.15;
}
.hero p {
  margin: 0;
  color: #4d5a70;
  max-width: 760px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 24px 0 40px;
}
.card, .panel {
  background: #ffffff;
  border: 1px solid #d9deea;
  border-radius: 8px;
}
.card {
  padding: 18px;
}
.card h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.meta {
  color: #5d687c;
  font-size: 13px;
}
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 12px 0;
}
.badge {
  display: inline-flex;
  border-radius: 999px;
  border: 1px solid #cfd6e5;
  padding: 3px 8px;
  font-size: 12px;
  color: #38455a;
  background: #f8fafc;
}
.badge.pass { border-color: #78b892; color: #1f6b3b; background: #effaf2; }
.badge.warning { border-color: #d2a647; color: #7a520f; background: #fff8e7; }
.badge.fail { border-color: #d37c7c; color: #8a2424; background: #fff0f0; }
.badge.draft, .badge.unknown { border-color: #a9b2c3; color: #505b70; background: #f2f4f8; }
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 6px;
  background: #174f9a;
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
}
.button.secondary {
  background: #eef2f8;
  color: #173250;
}
.content {
  padding: 24px 0 40px;
}
.panel {
  padding: 20px;
  margin-bottom: 16px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  text-align: left;
  border-bottom: 1px solid #e2e6ef;
  padding: 8px;
  vertical-align: top;
}
th {
  width: 220px;
  color: #4c5a70;
}
img.workflow-image {
  max-width: 100%;
  border: 1px solid #d9deea;
  border-radius: 6px;
  background: #ffffff;
}
""".lstrip()
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "styles.css").write_text(styles, encoding="utf-8")


def card_html(entry: dict[str, Any]) -> str:
    status = html.escape(str(entry["validation_status"]))
    source = entry.get("source_url") or entry.get("source_ref") or "source not recorded"
    history_link = entry.get("galaxy_history_url")
    history_button = ""
    if history_link:
        history_button = f'<a class="button" href="{html.escape(str(history_link))}">Galaxy history</a>'
    return f"""
<article class="card">
  <h2><a href="workflows/{html.escape(str(entry['slug']))}/">{html.escape(str(entry['title']))}</a></h2>
  <div class="meta">{html.escape(str(entry['workflow_class']))}</div>
  <div class="badges">
    <span class="badge {status}">{status}</span>
    <span class="badge">{html.escape(status_label(entry))}</span>
  </div>
  <p>{html.escape(str(entry.get('summary') or 'No summary recorded.'))}</p>
  <div class="meta">Source: {html.escape(str(source))}</div>
  <div class="actions">
    {history_button}
    <a class="button secondary" href="workflows/{html.escape(str(entry['slug']))}/">Details</a>
  </div>
</article>
"""


def metadata_table(entry: dict[str, Any]) -> str:
    rows = []
    keys = [
        "id",
        "workflow_class",
        "validation_profile",
        "validation_status",
        "review_status",
        "source_type",
        "source_ref",
        "source_url",
        "galaxy_instance",
        "galaxy_history_id",
        "execution_surface",
        "created",
        "updated",
        "tags",
    ]
    for key in keys:
        value = entry.get(key)
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        rows.append(f"<tr><th>{html.escape(key)}</th><td>{html.escape(str(value or ''))}</td></tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def write_index_page(docs_dir: Path, entries: list[dict[str, Any]]) -> None:
    if entries:
        cards = "\n".join(card_html(entry) for entry in entries)
    else:
        cards = '<section class="panel"><p>No reproduced workflow entries have been published yet.</p></section>'
    body = f"""
<header class="hero">
  <div class="wrap">
    <h1>Reproduced Galaxy Workflows</h1>
    <p>A lightweight registry of reproduced Galaxy histories and workflow artifacts.</p>
  </div>
</header>
<main class="wrap">
  <section class="grid">
    {cards}
  </section>
</main>
"""
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "index.html").write_text(page_shell("Reproduced Galaxy Workflows", body), encoding="utf-8")


def write_detail_page(workflows_dir: Path, docs_dir: Path, entry: dict[str, Any]) -> None:
    page_dir = docs_dir / "workflows" / str(entry["slug"])
    page_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_entry_artifacts(workflows_dir, docs_dir, entry)

    source_dir = workflows_dir / str(entry["entry_dir"])
    readme_path = source_dir / str(entry.get("readme_file") or "README.md")
    validation_report = load_json_artifact(source_dir, entry, "validation_file")
    provenance_report = load_json_artifact(source_dir, entry, "provenance_file")
    readme_html = ""
    if readme_path.is_file():
        readme_html = md_to_html(readme_path.read_text(encoding="utf-8"))
    else:
        readme_html = "<p>No README recorded for this entry.</p>"

    history = entry.get("galaxy_history_url")
    history_button = ""
    if history:
        history_button = f'<a class="button" href="{html.escape(str(history))}">Open Galaxy history</a>'

    artifact_links = []
    for field, label in ARTIFACT_FIELDS.items():
        if field in copied:
            artifact_links.append(f'<li><a href="{html.escape(copied[field])}">{html.escape(label)}</a></li>')
    if "metadata_file" in copied:
        artifact_links.append(f'<li><a href="{html.escape(copied["metadata_file"])}">metadata</a></li>')
    if "readme_file" in copied:
        artifact_links.append(f'<li><a href="{html.escape(copied["readme_file"])}">README</a></li>')
    artifacts_html = "<ul>" + "\n".join(artifact_links) + "</ul>" if artifact_links else "<p>No downloadable artifacts recorded.</p>"

    image_html = ""
    if "workflow_image" in copied:
        image_html = f'<img class="workflow-image" src="{html.escape(copied["workflow_image"])}" alt="Workflow image">'

    body = f"""
<header class="hero">
  <div class="wrap">
    <h1>{html.escape(str(entry['title']))}</h1>
    <p>{html.escape(str(entry.get('summary') or 'No summary recorded.'))}</p>
    <div class="actions">
      {history_button}
      <a class="button secondary" href="../../">All workflows</a>
    </div>
  </div>
</header>
<main class="wrap content">
  <section class="panel">
    <div class="badges">
      <span class="badge {html.escape(str(entry['validation_status']))}">{html.escape(str(entry['validation_status']))}</span>
      <span class="badge">{html.escape(status_label(entry))}</span>
    </div>
    {image_html}
    {metadata_table(entry)}
  </section>
  <section class="panel">
    <h2>Entry README</h2>
    {readme_html}
  </section>
  <section class="panel">
    <h2>Validation Summary</h2>
    {validation_summary_html(validation_report)}
  </section>
  <section class="panel">
    <h2>Provenance Summary</h2>
    {provenance_summary_html(provenance_report)}
  </section>
  <section class="panel">
    <h2>Downloads</h2>
    {artifacts_html}
  </section>
</main>
"""
    (page_dir / "index.html").write_text(page_shell(str(entry["title"]), body, depth=2), encoding="utf-8")


def write_docs(workflows_dir: Path, docs_dir: Path, entries: list[dict[str, Any]]) -> None:
    write_styles(docs_dir)
    write_index_page(docs_dir, entries)
    for entry in entries:
        write_detail_page(workflows_dir, docs_dir, entry)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    workflows_dir = root / args.workflows_dir
    site_dir = root / args.site_dir
    docs_dir = root / args.docs_dir

    entries, warnings = load_entries(workflows_dir)
    write_site_data(site_dir, entries, warnings, args.generated_at)
    write_docs(workflows_dir, docs_dir, entries)

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    print(f"Generated {len(entries)} workflow entries")
    print(f"Site data: {site_dir}")
    print(f"Static pages: {docs_dir}")

    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
