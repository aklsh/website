#!/usr/bin/env python3
"""Build the Gemini capsule from prepared Markdown content."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote


FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FIGURE = re.compile(r"\{\{<\s*figure\s+(.*?)\s*>\}\}", re.DOTALL)
ART_LINKS = re.compile(r"\{\{<\s*art-links\s+\"([^\"]+)\"\s*>\}\}")
PARAM = re.compile(r"(\w+)\s*=\s*(?:\"([^\"]*)\"|([^\s]+))")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text

    values: dict[str, str] = {}
    for line in match.group(0).splitlines()[1:-1]:
        key, _, value = line.partition(":")
        if key and value:
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = value[1:-1]
            values[key.strip()] = value
    return values, text[match.end() :]


def slug(path: Path, metadata: dict[str, str]) -> str:
    if metadata.get("slug"):
        return metadata["slug"]
    name = path.stem
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()


def output_path(source: Path, content_root: Path, output_root: Path) -> Path:
    relative = source.relative_to(content_root)
    metadata, _ = frontmatter(source.read_text())
    if relative.name == "_index.md":
        destination = relative.parent / "index.gmi"
    elif relative.name == "index.md":
        destination = relative.parent.with_suffix(".gmi")
    else:
        destination = relative.with_name(slug(source, metadata) + ".gmi")
    return output_root / destination


def shortcode_to_gemtext(text: str) -> str:
    def figure(match: re.Match[str]) -> str:
        params = dict((key, quoted or plain) for key, quoted, plain in PARAM.findall(match.group(1)))
        label = params.get('caption', params.get('alt', 'image'))
        target = quote(params.get('link') or params["src"], safe=":/?#[]@!$&'()*+,;=%")
        return f"[{label}]({target})"

    text = FIGURE.sub(figure, text)
    text = ART_LINKS.sub(
        lambda match: (
            f"[pdf](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.pdf)\n\n"
            f"[jpg](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.jpg)\n\n"
            f"[png](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.png)"
        ),
        text,
    )
    return text


FOOTNOTE_DEF = re.compile(r"^\[\^([^\]]+)\]:[ \t]*(.*)$", re.MULTILINE)
INLINE_FOOTNOTE_DEF = re.compile(r"[ \t]*\[\^([^\]]+)\]:[ \t]*(https?://\S+)[ \t]*")
FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")
BARE_URL = re.compile(r"^<?(https?://\S+?)>?$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FENCE = re.compile(r"^\s*(?:```|~~~)")


def footnotes(text: str) -> str:
    """Turn footnote references into inline links or parenthetical notes."""

    notes: dict[str, str] = {}

    def store(match: re.Match[str]) -> str:
        notes[match.group(1)] = match.group(2).strip()
        return ""

    text = FOOTNOTE_DEF.sub(store, text)
    text = INLINE_FOOTNOTE_DEF.sub(store, text)

    def reference(match: re.Match[str]) -> str:
        note = notes.get(match.group(1))
        if note is None:
            return match.group(0)
        url = BARE_URL.match(note)
        if url:
            return f"[[{match.group(1)}]]({url.group(1)})"
        prefix = "" if match.start() and match.string[match.start() - 1].isspace() else " "
        return f"{prefix}({note})"

    return FOOTNOTE_REF.sub(reference, text)


def tighten_lists(text: str) -> str:
    """Remove blank lines between list items; md2gemini mangles loose lists."""

    if not text.strip():
        return ""
    output: list[str] = []
    in_list = False
    in_fence = False
    blank = False
    for line in text.splitlines():
        if FENCE.match(line):
            if blank:
                output.append("")
            in_fence = not in_fence
            in_list, blank = False, False
            output.append(line)
        elif in_fence:
            output.append(line)
        elif not line.strip():
            blank = True
        elif LIST_ITEM.match(line):
            if not in_list and blank:
                output.append("")
            in_list, blank = True, False
            output.append(line)
        elif in_list and line[:1] in (" ", "\t"):
            if blank:
                output.append("")
            output.append(line)
            blank = False
        else:
            if blank:
                output.append("")
            in_list, blank = False, False
            output.append(line)
    return "\n".join(output) + "\n"


def prepare_markdown(text: str) -> str:
    text = footnotes(text)
    text = tighten_lists(text)
    return re.sub(r"~~(.+?)~~", r"\1", text)


def convert(text: str, command: str) -> str:
    _, text = frontmatter(text)
    result = subprocess.run(
        [command, "--plain", "--strip-html", "--links", "copy", "--md-links"],
        input=shortcode_to_gemtext(prepare_markdown(text)),
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip() + "\n"


def date_value(metadata: dict[str, str]) -> str:
    return metadata.get("date", "").strip('"')


def clean_title(title: str) -> str:
    return title.replace("`", "").replace("**", "").strip()


def page(metadata: dict[str, str], body: str, back: str) -> str:
    lines: list[str] = []
    title = clean_title(metadata.get("title", ""))
    if title:
        lines.extend([f"# {title}", ""])
    description = metadata.get("description", "").strip()
    if description:
        lines.extend([f"> {description}", ""])
    if body.strip():
        lines.extend([body.strip(), ""])
    lines.extend([back, ""])
    return "\n".join(lines)


def blog_index(content_root: Path, output_root: Path, command: str) -> None:
    source_index = content_root / "blog/_index.md"
    index_metadata, _ = frontmatter(source_index.read_text())
    posts = []
    for source in sorted((content_root / "blog").glob("*.md")):
        if source.name == "_index.md":
            continue
        metadata, _ = frontmatter(source.read_text())
        posts.append(
            (
                date_value(metadata),
                clean_title(metadata.get("title", source.stem)),
                output_path(source, content_root, output_root),
            )
        )
    posts.sort(key=lambda post: post[0], reverse=True)

    lines = [f"# {clean_title(index_metadata.get('title') or 'Blog')}", ""]
    description = index_metadata.get("description", "").strip()
    if description:
        lines.extend([f"> {description}", ""])
    converted_body = convert(source_index.read_text(), command).strip()
    if converted_body:
        lines.extend([converted_body, ""])
    lines.extend(["## Recent posts", ""])
    for published, title, destination in posts:
        lines.append(f"=> /{destination.relative_to(output_root)} {title} ({published})")
    lines.extend(["", "=> /index.gmi ← Back to Home", ""])
    (output_root / "blog/index.gmi").write_text("\n".join(lines))


LINK = re.compile(r"^=>\s+(\S+)", re.MULTILINE)


def validate(output_root: Path) -> None:
    problems: list[str] = []
    for path in output_root.rglob("*.gmi"):
        text = path.read_text()
        first_line = text.lstrip().splitlines()[:1]
        if not first_line or not first_line[0].startswith("# "):
            problems.append(f"{path}: missing top-level heading")
        for target in LINK.findall(text):
            if not re.match(r"^(?:/|[a-zA-Z][a-zA-Z0-9+.-]*:)", target):
                problems.append(f"{path}: invalid link target {target}")
            elif target.startswith("/") and not (output_root / target[1:]).exists():
                problems.append(f"{path}: missing local link target {target}")
    if problems:
        raise SystemExit("gemtext validation failed:\n" + "\n".join(problems))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", type=Path, default=Path("content"))
    parser.add_argument("--output", type=Path, default=Path("public-gemini"))
    parser.add_argument("--command", default="md2gemini")
    args = parser.parse_args()

    if shutil.which(args.command) is None:
        raise SystemExit("md2gemini is required; install it with: pipx install md2gemini")

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)

    for source in args.content.rglob("*.md"):
        if source.name == "_index.md":
            continue
        metadata, _ = frontmatter(source.read_text())
        back = (
            "=> /blog/index.gmi ← Back to Blog"
            if source.parent.name == "blog"
            else "=> /index.gmi ← Back to Home"
        )
        destination = output_path(source, args.content, args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            page(metadata, convert(source.read_text(), args.command), back)
        )

    home = args.output / "index.gmi"
    home_source = args.content / "_index.md"
    metadata, _ = frontmatter(home_source.read_text())
    home_body = convert(home_source.read_text(), args.command).strip()
    home_lines = [f"# {clean_title(metadata.get('heading') or 'Home')}", ""]
    if metadata.get("handle"):
        home_lines.extend([f"> {metadata['handle']}", ""])
    if home_body:
        home_lines.extend([home_body, ""])
    home_lines.extend(
        [
            "=> /about.gmi About",
            "=> /blog/index.gmi Blog",
            "=> /art.gmi Art",
            "",
        ]
    )
    home.write_text("\n".join(home_lines))
    blog_index(args.content, args.output, args.command)
    validate(args.output)


if __name__ == "__main__":
    main()
