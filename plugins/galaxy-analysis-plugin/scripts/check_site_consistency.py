#!/usr/bin/env python3
"""Check that committed static site outputs match workflow metadata."""

from __future__ import annotations

import argparse
import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--workflows-dir", default="workflows", help="Workflow entry directory under root")
    parser.add_argument("--site-dir", default="site", help="Committed site data directory under root")
    parser.add_argument("--docs-dir", default="docs", help="Committed static docs directory under root")
    return parser.parse_args()


def current_generated_at(site_dir: Path) -> str:
    index_path = site_dir / "index.json"
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        value = data.get("summary", {}).get("generated_at")
        if isinstance(value, str) and value:
            return value
    except Exception:
        pass
    return "1970-01-01T00:00:00+00:00"


def generated_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(path.relative_to(base) for path in base.rglob("*") if path.is_file())


def compare_tree(expected_dir: Path, actual_dir: Path, label: str, allowed_extra: set[Path] | None = None) -> list[str]:
    errors: list[str] = []
    expected_files = set(generated_files(expected_dir))
    actual_files = set(generated_files(actual_dir))
    allowed_extra = allowed_extra or set()

    for rel in sorted(expected_files):
        expected = expected_dir / rel
        actual = actual_dir / rel
        if not actual.is_file():
            errors.append(f"{label}: missing committed file {actual}")
            continue
        if not filecmp.cmp(expected, actual, shallow=False):
            errors.append(f"{label}: committed file is stale: {actual}")

    for rel in sorted(actual_files - expected_files - allowed_extra):
        errors.append(f"{label}: committed generated output is stale or no longer generated: {actual_dir / rel}")

    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    site_dir = root / args.site_dir
    docs_dir = root / args.docs_dir
    generated_at = current_generated_at(site_dir)
    generator = Path(__file__).with_name("generate_workflow_site.py")

    with tempfile.TemporaryDirectory(prefix="galaxy-site-check-") as tmp:
        tmp_root = Path(tmp)
        tmp_site = tmp_root / "site"
        tmp_docs = tmp_root / "docs"
        command = [
            sys.executable,
            str(generator),
            "--root",
            str(root),
            "--workflows-dir",
            args.workflows_dir,
            "--site-dir",
            str(tmp_site),
            "--docs-dir",
            str(tmp_docs),
            "--generated-at",
            generated_at,
            "--strict",
        ]
        completed = subprocess.run(command, text=True, capture_output=True)
        if completed.returncode:
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode

        errors = []
        errors.extend(compare_tree(tmp_site, site_dir, "site"))
        errors.extend(compare_tree(tmp_docs, docs_dir, "docs", allowed_extra={Path(".nojekyll")}))

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1

    print("Static workflow site is consistent with workflow metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
