#!/usr/bin/env python3
"""Build the Gemini capsule from prepared Markdown content."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FIGURE_LINK = re.compile(
    r"\[[^\]]*\{\{<\s*figure\s+.*?src=\s*[\"]([^\"]+)[\"]\s*>\}\}[^\]]*\]\(([^)]+)\)"
)
FIGURE = re.compile(
    r"\{\{<\s*(?:figure|avatar)\s+(.*?)\s*>\}\}", re.DOTALL
)
ART_LINKS = re.compile(r"\{\{<\s*art-links\s+\"([^\"]+)\"\s*>\}\}")
TABLE_OPEN = re.compile(r"\{\{<\s*table(?:\s+[^>]*)?>\}\}")
TABLE_CLOSE = re.compile(r"\{\{<\s*/table\s*>\}\}")
PARAM = re.compile(r"(\w+)\s*=\s*(?:\"([^\"]*)\"|([^\s]+))")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text

    values: dict[str, str] = {}
    for line in match.group(0).splitlines()[1:-1]:
        key, _, value = line.partition(":")
        if key and value:
            values[key.strip()] = value.strip().strip('"')
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
    def linked_figure(match: re.Match[str]) -> str:
        return f"[{match.group(1)}]({match.group(2)})"

    text = FIGURE_LINK.sub(linked_figure, text)

    def figure(match: re.Match[str]) -> str:
        params = dict((key, quoted or plain) for key, quoted, plain in PARAM.findall(match.group(1)))
        label = params.get('caption', params.get('alt', 'image'))
        return f"[{label}]({params['src']})"

    text = FIGURE.sub(figure, text)
    text = ART_LINKS.sub(
        lambda match: (
            f"[pdf](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.pdf)\n\n"
            f"[jpg](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.jpg)\n\n"
            f"[png](https://cdn.aklsh.me/art/{match.group(1)}/{match.group(1)}.png)"
        ),
        text,
    )
    text = TABLE_OPEN.sub("", text)
    return TABLE_CLOSE.sub("", text)


def convert(text: str, command: str) -> str:
    _, text = frontmatter(text)
    result = subprocess.run(
        [command, "--plain", "--strip-html", "--links", "copy", "--md-links"],
        input=shortcode_to_gemtext(text),
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip() + "\n"


def date_value(metadata: dict[str, str]) -> str:
    return metadata.get("date", "").strip('"')


def blog_index(content_root: Path, output_root: Path, command: str) -> None:
    source_index = content_root / "blog/_index.md"
    index_metadata, _ = frontmatter(source_index.read_text())
    posts = []
    for source in sorted((content_root / "blog").glob("*.md")):
        if source.name == "_index.md":
            continue
        metadata, _ = frontmatter(source.read_text())
        posts.append((date_value(metadata), metadata.get("title", source.stem), output_path(source, content_root, output_root)))
    posts.sort(reverse=True)

    lines = [f"# {index_metadata.get('title', 'Blog')}", ""]
    converted_body = convert(source_index.read_text(), command).strip()
    if converted_body:
        lines.extend([converted_body, ""])
    lines.extend(["Recent posts", ""])
    for published, title, destination in posts:
        lines.append(f"=> /{destination.relative_to(output_root)} {title} ({published})")
    lines.extend(["", "=> /index.gmi Back to home", ""])
    (output_root / "blog/index.gmi").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", type=Path, default=Path("content"))
    parser.add_argument("--assets", type=Path, default=Path("gemini"))
    parser.add_argument("--output", type=Path, default=Path("public-gemini"))
    parser.add_argument("--command", default="md2gemini")
    args = parser.parse_args()

    if shutil.which(args.command) is None:
        raise SystemExit("md2gemini is required; install it with: pipx install md2gemini")

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)

    for asset in args.assets.rglob("*"):
        if asset.is_file() and asset.suffix != ".gmi":
            destination = args.output / asset.relative_to(args.assets)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, destination)

    for source in args.content.rglob("*.md"):
        destination = output_path(source, args.content, args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(convert(source.read_text(), args.command))

    home = args.output / "index.gmi"
    home_source = args.content / "_index.md"
    metadata, _ = frontmatter(home_source.read_text())
    home_body = convert(home_source.read_text(), args.command).strip()
    body = f"{home_body}\n\n" if home_body else ""
    home.write_text(
        f"# {metadata.get('heading', 'Home')}\n\n> {metadata.get('handle', '')}\n\n"
        + body
        + "=> /about.gmi About\n=> /blog/index.gmi Blog\n=> /art.gmi Art\n"
    )
    blog_index(args.content, args.output, args.command)


if __name__ == "__main__":
    main()
