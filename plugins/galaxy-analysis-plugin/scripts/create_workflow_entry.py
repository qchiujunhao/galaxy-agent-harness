#!/usr/bin/env python3
"""Create a draft workflow-site entry from a reproduced Galaxy history."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_STATUSES = {"pass", "warning", "fail", "draft"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--id", help="Entry id. Defaults to wf_<date>_<slug>")
    parser.add_argument("--slug", help="Public page slug. Defaults to the entry id")
    parser.add_argument("--title", required=True, help="Workflow entry title")
    parser.add_argument("--summary", required=True, help="Short summary for site cards")
    parser.add_argument("--source-url", required=True, help="Original GitHub/source URL")
    parser.add_argument("--source-ref", default="", help="Commit, benchmark id, paper section, or source reference")
    parser.add_argument("--source-type", default="github_repository", help="Source type label")
    parser.add_argument("--galaxy-history-url", required=True, help="Reproduced Galaxy history URL")
    parser.add_argument("--galaxy-history-id", default="", help="Galaxy history id, if known")
    parser.add_argument("--galaxy-instance", default="", help="Galaxy instance URL. Inferred from history URL if omitted")
    parser.add_argument("--workflow-class", default="general_galaxy_workflow", help="Workflow class")
    parser.add_argument("--validation-profile", default="general_galaxy_workflow", help="Validation profile")
    parser.add_argument("--validation-status", default="draft", choices=sorted(VALIDATION_STATUSES))
    parser.add_argument("--review-status", default="draft", help="Review status")
    parser.add_argument("--execution-surface", default="galaxy-cli", help="Execution surface used")
    parser.add_argument("--submitted-by", default="", help="Submitter name or handle")
    parser.add_argument("--tag", action="append", default=[], help="Tag to include. Repeatable")
    parser.add_argument("--public", action="store_true", help="Mark the Galaxy history as public")
    parser.add_argument("--importable", action="store_true", help="Mark the Galaxy history as importable")
    parser.add_argument("--workflow-file", type=Path, help="Optional workflow.ga to copy")
    parser.add_argument("--workflow-image", type=Path, help="Optional workflow.svg to copy")
    parser.add_argument("--thumbnail", type=Path, help="Optional thumbnail image to copy")
    parser.add_argument("--validation-json", type=Path, help="Optional validation_report.json to copy")
    parser.add_argument("--provenance-json", type=Path, help="Optional provenance.json to copy")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing entry directory")
    parser.add_argument("--no-generate-site", action="store_true", help="Skip static site regeneration")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "workflow"


def yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(str(value))


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "\n".join(f"  - {yaml_scalar(value)}" for value in values)


def infer_galaxy_instance(history_url: str) -> str:
    parsed = urlparse(history_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return ""


def allocate_entry_id(root: Path, title: str, requested_id: str | None, force: bool) -> str:
    workflows_dir = root / "workflows"
    if requested_id:
        entry_id = requested_id
        if (workflows_dir / entry_id).exists() and not force:
            raise SystemExit(f"Entry already exists: workflows/{entry_id}. Use --force to overwrite.")
        return entry_id

    date = dt.date.today().strftime("%Y%m%d")
    base = f"wf_{date}_{slugify(title)}"
    candidate = base
    suffix = 2
    while (workflows_dir / candidate).exists():
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def copy_optional(src: Path | None, entry_dir: Path, target_name: str) -> str | None:
    if src is None:
        return None
    if not src.is_file():
        raise SystemExit(f"Optional artifact does not exist: {src}")
    dst = entry_dir / target_name
    shutil.copy2(src, dst)
    return target_name


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_metadata(path: Path, metadata: dict[str, object]) -> None:
    lines: list[str] = []
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.append(yaml_list([str(item) for item in value]))
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path, args: argparse.Namespace, entry_id: str) -> None:
    lines = [
        f"# {args.title}",
        "",
        "## Summary",
        "",
        args.summary,
        "",
        "## Source",
        "",
        f"- Type: {args.source_type}",
        f"- URL: {args.source_url}",
    ]
    if args.source_ref:
        lines.append(f"- Reference: {args.source_ref}")
    lines.extend(
        [
            "",
            "## Galaxy Reproduction",
            "",
            f"- History: {args.galaxy_history_url}",
            f"- Public: {'yes' if args.public else 'no'}",
            f"- Importable: {'yes' if args.importable else 'no'}",
            f"- Execution surface: {args.execution_surface}",
            "",
            "## Validation",
            "",
            f"- Status: {args.validation_status}",
            f"- Profile: {args.validation_profile}",
            "",
            "## Files",
            "",
            "- Metadata: `metadata.yaml`",
            "- Validation report: `validation_report.json`",
            "- Provenance: `provenance.json`",
            "",
            f"Entry id: `{entry_id}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def regenerate_site(root: Path) -> None:
    generator = Path(__file__).with_name("generate_workflow_site.py")
    subprocess.run([sys.executable, str(generator), "--root", str(root)], check=True)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    workflows_dir = root / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    entry_id = allocate_entry_id(root, args.title, args.id, args.force)
    entry_dir = workflows_dir / entry_id
    entry_dir.mkdir(parents=True, exist_ok=True)

    today = dt.date.today().isoformat()
    slug = slugify(args.slug or entry_id)
    galaxy_instance = args.galaxy_instance or infer_galaxy_instance(args.galaxy_history_url)

    workflow_file = copy_optional(args.workflow_file, entry_dir, "workflow.ga")
    workflow_image = copy_optional(args.workflow_image, entry_dir, "workflow.svg")
    thumbnail_image = copy_optional(args.thumbnail, entry_dir, "thumbnail.png")

    if args.validation_json:
        validation_file = copy_optional(args.validation_json, entry_dir, "validation_report.json")
    else:
        validation_file = "validation_report.json"
        write_json(
            entry_dir / validation_file,
            {
                "status": args.validation_status,
                "profile": args.validation_profile,
                "checks": [],
                "warnings": ["Draft entry created before full validation report was attached."],
            },
        )

    if args.provenance_json:
        provenance_file = copy_optional(args.provenance_json, entry_dir, "provenance.json")
    else:
        provenance_file = "provenance.json"
        write_json(
            entry_dir / provenance_file,
            {
                "source_url": args.source_url,
                "source_ref": args.source_ref,
                "galaxy_history_url": args.galaxy_history_url,
                "execution_surface": args.execution_surface,
                "created": today,
            },
        )

    write_readme(entry_dir / "README.md", args, entry_id)

    metadata: dict[str, object] = {
        "id": entry_id,
        "title": args.title,
        "slug": slug,
        "task_family": args.workflow_class,
        "workflow_class": args.workflow_class,
        "validation_profile": args.validation_profile,
        "source_type": args.source_type,
        "source_ref": args.source_ref,
        "source_url": args.source_url,
        "galaxy_instance": galaxy_instance,
        "galaxy_history_url": args.galaxy_history_url,
        "galaxy_history_id": args.galaxy_history_id,
        "galaxy_history_public": args.public,
        "galaxy_history_importable": args.importable,
        "submitted_by": args.submitted_by,
        "submission_date": today,
        "created": today,
        "updated": today,
        "status": args.validation_status,
        "review_status": args.review_status,
        "validation_status": args.validation_status,
        "execution_surface": args.execution_surface,
        "workflow_file": workflow_file,
        "workflow_image": workflow_image,
        "thumbnail_image": thumbnail_image,
        "readme_file": "README.md",
        "validation_file": validation_file,
        "provenance_file": provenance_file,
        "tags": args.tag,
        "summary": args.summary,
    }
    write_metadata(entry_dir / "metadata.yaml", metadata)

    if not args.no_generate_site:
        regenerate_site(root)

    print(f"Created workflow entry: {entry_dir}")
    print(f"Galaxy history link: {args.galaxy_history_url}")
    if not args.no_generate_site:
        print(f"Updated static site: {root / 'docs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
