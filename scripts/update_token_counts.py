#!/usr/bin/env python3
"""Generate or verify reproducible per-skill instruction token counts."""

from __future__ import annotations

import argparse
import ast
import csv
import io
import re
import sys
from importlib.metadata import version
from pathlib import Path

import tiktoken


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "token-counts.csv"
ENCODING = "cl100k_base"
TIKTOKEN_VERSION = "0.11.0"
FIELDS = (
    "skill",
    "tokenizer",
    "tokenizer_package_version",
    "description_tokens",
    "core_tokens",
    "full_tokens",
    "reference_files",
)


def frontmatter_description(text: str, source: Path) -> str:
    """Return the semantic description value from a skill's YAML front matter."""
    if not text.startswith("---\n"):
        raise RuntimeError(f"missing YAML front matter in {source}")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise RuntimeError(f"unterminated YAML front matter in {source}")
    match = re.search(r"(?m)^description:\s*(.+?)\s*$", parts[1])
    if not match:
        raise RuntimeError(f"missing front-matter description in {source}")
    value = match.group(1)
    if value[:1] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as error:
            raise RuntimeError(
                f"invalid quoted front-matter description in {source}"
            ) from error
        if not isinstance(parsed, str):
            raise RuntimeError(f"description is not text in {source}")
        return parsed
    return value


def render() -> str:
    installed = version("tiktoken")
    if installed != TIKTOKEN_VERSION:
        raise RuntimeError(
            f"tiktoken {TIKTOKEN_VERSION} is required; found {installed}"
        )

    encoding = tiktoken.get_encoding(ENCODING)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()

    for directory in sorted((ROOT / "skills").iterdir()):
        if not directory.is_dir():
            continue
        entry = directory / "SKILL.md"
        references = sorted((directory / "references").glob("*.md"))
        entry_text = entry.read_text(encoding="utf-8")
        description_tokens = len(
            encoding.encode(frontmatter_description(entry_text, entry))
        )
        core_tokens = len(encoding.encode(entry_text))
        reference_tokens = sum(
            len(encoding.encode(path.read_text(encoding="utf-8")))
            for path in references
        )
        writer.writerow(
            {
                "skill": directory.name,
                "tokenizer": ENCODING,
                "tokenizer_package_version": installed,
                "description_tokens": description_tokens,
                "core_tokens": core_tokens,
                "full_tokens": core_tokens + reference_tokens,
                "reference_files": len(references),
            }
        )
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        expected = render()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
        return 0

    actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
    if actual != expected:
        print(
            "research/token-counts.csv is stale; run "
            "python3 scripts/update_token_counts.py --write",
            file=sys.stderr,
        )
        return 1
    print("Token counts are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
