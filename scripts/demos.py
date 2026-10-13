#!/usr/bin/env python3
"""Create, inspect, and catalog reusable demos using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = Path("demos")
TEMPLATE_ROOT = Path("templates") / "demo-template"
CATALOG_PATH = DEMO_ROOT / "README.md"
CATALOG_BEGIN = "<!-- DEMO-CATALOG:BEGIN -->"
CATALOG_END = "<!-- DEMO-CATALOG:END -->"

DEMO_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TOKEN = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
FORBIDDEN_TITLE = re.compile(r'["<>\\`\r\n]')
ALLOWED_STATUSES = {"draft", "ready", "deprecated"}
TEXT_EXTENSIONS = {
    "",
    ".bicep",
    ".css",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".tf",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
REQUIRED_FILES = {
    Path("README.md"),
    Path("demo.json"),
    Path("docs/EXTENDING.md"),
    Path("infra/README.md"),
    Path("walkthrough/README.md"),
    Path("walkthrough/index.html"),
}


def demo_directories(root: Path) -> list[Path]:
    directory = root / DEMO_ROOT
    if not directory.exists():
        return []
    return sorted(
        entry
        for entry in directory.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )


def read_manifest(directory: Path) -> dict[str, Any]:
    data = json.loads((directory / "demo.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("demo.json must contain a JSON object")
    return data


def _nonempty_strings(value: object, *, require_item: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not require_item or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _contained_file(directory: Path, value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        candidate = (directory / value).resolve()
        candidate.relative_to(directory.resolve())
    except ValueError:
        return False
    return candidate.is_file()


def manifest_errors(directory: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in ("id", "title", "summary", "status", "walkthrough"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"demo.json field '{field}' must be a non-empty string")

    if manifest.get("id") != directory.name:
        errors.append("demo.json field 'id' must match the demo folder name")
    if manifest.get("status") not in ALLOWED_STATUSES:
        errors.append("demo.json field 'status' must be draft, ready, or deprecated")
    if not _nonempty_strings(manifest.get("owners"), require_item=True):
        errors.append("demo.json field 'owners' must contain at least one string")
    if not _nonempty_strings(manifest.get("tags")):
        errors.append("demo.json field 'tags' must be a list of strings")
    if "prerequisites" in manifest and not _nonempty_strings(manifest["prerequisites"]):
        errors.append("demo.json field 'prerequisites' must be a list of strings")
    if not _contained_file(directory, manifest.get("walkthrough")):
        errors.append("demo.json field 'walkthrough' must reference a file inside the demo")

    deploy = manifest.get("deploy")
    if not isinstance(deploy, dict):
        errors.append("demo.json field 'deploy' must be an object")
    else:
        if not _nonempty_strings(deploy.get("targets"), require_item=True):
            errors.append("demo.json field 'deploy.targets' must contain at least one string")
        if not _contained_file(directory, deploy.get("guide")):
            errors.append("demo.json field 'deploy.guide' must reference a file inside the demo")

    return errors


def validate_demo(directory: Path) -> list[str]:
    errors: list[str] = []
    if not DEMO_ID.fullmatch(directory.name):
        errors.append("demo folder name must use lowercase kebab-case")

    for relative in sorted(REQUIRED_FILES):
        if not (directory / relative).is_file():
            errors.append(f"required file is missing: {relative.as_posix()}")

    source = directory / "src"
    if not source.is_dir() or not any(item.is_file() for item in source.rglob("*")):
        errors.append("src/ must exist and contain at least one file")

    manifest_file = directory / "demo.json"
    if manifest_file.is_file():
        try:
            errors.extend(manifest_errors(directory, read_manifest(directory)))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"demo.json could not be read: {error}")

    for file in sorted(item for item in directory.rglob("*") if item.is_file()):
        if file.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            content = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if TOKEN.search(content):
            errors.append(f"template token remains in {file.relative_to(directory).as_posix()}")

    return errors


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def catalog_table(root: Path) -> str:
    rows = [
        "| Demo | Summary | Status | Tags | Walkthrough | Deployment |",
        "|:-----|:--------|:------:|:-----|:------------|:-----------|",
    ]
    for directory in demo_directories(root):
        try:
            manifest = read_manifest(directory)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if manifest_errors(directory, manifest):
            continue
        deploy = manifest["deploy"]
        tags = ", ".join(f"`{tag}`" for tag in manifest["tags"])
        targets = ", ".join(deploy["targets"])
        rows.append(
            f"| [{_markdown_cell(manifest['title'])}]({directory.name}/) "
            f"| {_markdown_cell(manifest['summary'])} "
            f"| {_markdown_cell(manifest['status'])} "
            f"| {tags} "
            f"| [Open]({directory.name}/{manifest['walkthrough']}) "
            f"| [{_markdown_cell(targets)}]({directory.name}/{deploy['guide']}) |"
        )
    if len(rows) == 2:
        rows.append("| _No demos registered_ | | | | | |")
    return "\n".join(rows)


def synchronize_catalog(root: Path, *, check: bool) -> bool:
    catalog = root / CATALOG_PATH
    current = catalog.read_text(encoding="utf-8")
    begin = current.find(CATALOG_BEGIN)
    end = current.find(CATALOG_END)
    if begin < 0 or end < begin:
        raise ValueError("demos/README.md is missing the demo catalog markers")
    revised = (
        current[: begin + len(CATALOG_BEGIN)]
        + "\n"
        + catalog_table(root)
        + "\n"
        + current[end:]
    )
    if revised == current:
        return True
    if not check:
        catalog.write_text(revised, encoding="utf-8")
    return False


def create_demo(root: Path, demo_id: str, title: str) -> Path:
    if not DEMO_ID.fullmatch(demo_id):
        raise ValueError("demo id must use lowercase kebab-case")
    if not title.strip() or FORBIDDEN_TITLE.search(title):
        raise ValueError("title contains an unsupported character")

    destination = root / DEMO_ROOT / demo_id
    if destination.exists():
        raise ValueError(f"demo already exists: {demo_id}")

    shutil.copytree(root / TEMPLATE_ROOT, destination)
    substitutions = {"{{DEMO_ID}}": demo_id, "{{DEMO_TITLE}}": title}
    for file in (item for item in destination.rglob("*") if item.is_file()):
        if file.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        content = file.read_text(encoding="utf-8")
        for token, replacement in substitutions.items():
            content = content.replace(token, replacement)
        file.write_text(content, encoding="utf-8")
    synchronize_catalog(root, check=False)
    return destination


def command_new(args: argparse.Namespace) -> int:
    title = args.title or args.demo_id.replace("-", " ").title()
    try:
        destination = create_demo(args.root, args.demo_id, title)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Created {destination}")
    print("Complete the manifest, walkthrough, source, deployment, and extension guidance.")
    print("Then run: python scripts/demos.py validate")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    failed = False
    directories = demo_directories(args.root)
    for directory in directories:
        errors = validate_demo(directory)
        if not errors:
            print(f"PASS {directory.name}")
            continue
        failed = True
        print(f"FAIL {directory.name}")
        for error in errors:
            print(f"  {error}")

    try:
        current = synchronize_catalog(args.root, check=True)
    except (OSError, ValueError) as error:
        current = False
        print(f"FAIL catalog: {error}")
    if not current:
        failed = True
        print("FAIL catalog: run 'python scripts/demos.py catalog'")

    print(f"Checked {len(directories)} demo(s)")
    return int(failed)


def command_catalog(args: argparse.Namespace) -> int:
    try:
        current = synchronize_catalog(args.root, check=args.check)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.check:
        print("Catalog is current." if current else "Catalog needs regeneration.")
        return 0 if current else 1
    print("Catalog updated." if not current else "Catalog already current.")
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Manage the repository's reusable demos.")
    cli.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    commands = cli.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="create a demo from the repository template")
    new.add_argument("demo_id")
    new.add_argument("--title")
    new.set_defaults(handler=command_new)

    validate = commands.add_parser("validate", help="validate demos and the generated catalog")
    validate.set_defaults(handler=command_validate)

    catalog = commands.add_parser("catalog", help="regenerate the demo catalog")
    catalog.add_argument("--check", action="store_true")
    catalog.set_defaults(handler=command_catalog)
    return cli


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
