#!/usr/bin/env python3
"""
Render custom citation markers in Markdown.

Converts occurrences of:
  - [cite_start]  -> removed
  - [cite: N]     -> [N] (optionally as superscript when --sup is used)

If a references YAML/JSON is provided, a References section will be appended
containing only the numbers actually cited in the document (in ascending order).

Usage:
  python utils/render_citations.py -i README.md -o README.rendered.md \
         --refs references.yaml --sup

References file format (YAML or JSON):
  1: "Author, Title, Venue (Year). URL"
  2: "..."
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False


CITE_START_PATTERN = re.compile(r"\[cite_start\]")
CITE_NUM_PATTERN = re.compile(r"\[cite:\s*(\d+)\]")


def load_references(path: Path | None) -> dict[int, str]:
    if path is None:
        return {}
    if not path.exists():
        print(f"Warning: references file not found: {path}", file=sys.stderr)
        return {}
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            if not YAML_AVAILABLE:
                print("Warning: PyYAML not installed; can't read YAML. Falling back to empty references.", file=sys.stderr)
                return {}
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        refs: dict[int, str] = {}
        for k, v in data.items():
            try:
                refs[int(k)] = str(v)
            except Exception:
                continue
        return refs
    except Exception as e:
        print(f"Warning: failed to parse references: {e}", file=sys.stderr)
        return {}


def render_markdown(md: str, superscript: bool = False) -> tuple[str, list[int]]:
    # Remove cite_start markers
    md = CITE_START_PATTERN.sub("", md)
    cited: list[int] = []

    def repl(m: re.Match[str]) -> str:
        n = int(m.group(1))
        cited.append(n)
        if superscript:
            return f"<sup>[{n}]</sup>"
        return f"[{n}]"

    md = CITE_NUM_PATTERN.sub(repl, md)
    # preserve order of first occurrence while deduplicating
    seen = set()
    ordered = []
    for n in cited:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return md, ordered


def append_references(md: str, order: list[int], refs: dict[int, str]) -> str:
    if not order:
        return md
    lines = [md.rstrip(), "", "## References", ""]
    for n in sorted(order):
        entry = refs.get(n)
        if entry is None:
            entry = "(add reference details)"
        lines.append(f"[{n}] {entry}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Render custom [cite_*] markers in Markdown.")
    p.add_argument("-i", "--input", required=True, help="Input Markdown file")
    p.add_argument("-o", "--output", required=True, help="Output Markdown file")
    p.add_argument("--refs", help="Path to references YAML or JSON", default=None)
    p.add_argument("--sup", action="store_true", help="Render citations as superscripts")
    args = p.parse_args(argv)

    in_path = Path(args.input)
    out_path = Path(args.output)
    refs_path = Path(args.refs) if args.refs else None

    md = in_path.read_text(encoding="utf-8")
    rendered, order = render_markdown(md, superscript=args.sup)
    refs = load_references(refs_path)
    rendered = append_references(rendered, order, refs)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote: {out_path} (citations: {len(order)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
