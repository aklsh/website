#!/usr/bin/env python3
"""Prepare the shared Markdown source for one publishing target.

The source of truth is content/**/*.md.  This script creates a disposable
target-specific content tree before Hugo or md2gemini reads it.

Conditional blocks are deliberately HTML comments, so they remain valid
Markdown and do not show up in the rendered HTML:

    <!-- IF HTML -->
    HTML-only Markdown, raw HTML, or Hugo shortcodes
    <!-- ENDIF -->

    <!-- IF GEMTEXT -->
    Gemini-only Markdown
    <!-- ENDIF -->

The GEMTEXT spelling is used instead of GEMINI because it describes the
output format rather than the hosting protocol.  GEMINI is accepted as an
alias for convenience.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


MARKER = re.compile(
    r"^\s*<!--\s*(?:(?P<action>IF|END)\s+(?P<target>HTML|GEMTEXT|GEMINI)|(?P<endif>ENDIF))\s*-->\s*$",
    re.IGNORECASE,
)


def target_name(value: str) -> str:
    value = value.upper()
    return "GEMTEXT" if value == "GEMINI" else value


def render_markdown(source: str, target: str, path: Path) -> str:
    """Include only blocks applicable to *target* and remove their markers."""

    active = [True]
    targets: list[str] = []
    output: list[str] = []

    for line_number, line in enumerate(source.splitlines(keepends=True), 1):
        match = MARKER.match(line)
        if match:
            action = (match.group("action") or "ENDIF").upper()
            marker_target = target_name(match.group("target") or "")

            if action == "IF":
                active.append(active[-1] and marker_target == target)
                targets.append(marker_target)
            elif len(active) == 1:
                raise ValueError(f"{path}:{line_number}: unmatched conditional end")
            else:
                if action == "END" and marker_target != targets[-1]:
                    raise ValueError(f"{path}:{line_number}: mismatched conditional end")
                active.pop()
                targets.pop()
            continue

        if active[-1]:
            output.append(line)

    if len(active) != 1:
        raise ValueError(f"{path}: unterminated conditional block")

    return "".join(output)


def prepare(source_root: Path, output_root: Path, target: str) -> None:
    target = target_name(target)
    if target not in {"HTML", "GEMTEXT"}:
        raise ValueError(f"unsupported target: {target}")

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    for source in source_root.rglob("*"):
        relative = source.relative_to(source_root)
        destination = output_root / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif source.suffix.lower() == ".md":
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                render_markdown(source.read_text(), target, source),
                encoding="utf-8",
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("html", "gemtext", "gemini"), required=True)
    parser.add_argument("--source", type=Path, default=Path("content"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output, args.target)


if __name__ == "__main__":
    main()
