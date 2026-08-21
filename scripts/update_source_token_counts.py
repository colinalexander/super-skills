#!/usr/bin/env python3
"""Generate or verify token counts for retained external source descriptions."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from importlib.metadata import version
from pathlib import Path

import tiktoken

from check_similarity import (
    expected_gitskills_frame,
    files_under,
    git_blob_id,
    require_external_source_root,
)
from update_token_counts import (
    ENCODING,
    TIKTOKEN_VERSION,
    frontmatter_description,
    frontmatter_fields,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "source-description-token-counts.csv"
FIELDS = (
    "rank",
    "file_sha",
    "super_skill",
    "original_name",
    "installed_name",
    "tokenizer",
    "tokenizer_package_version",
    "description_tokens",
)


def active_ledger_rows() -> list[dict[str, str]]:
    """Return retained evidence rows routed to an active skill."""
    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        return [
            row
            for row in csv.DictReader(handle)
            if row["super_skill"] != "document-productivity"
        ]


def verified_source_map(source_root: Path) -> dict[str, Path]:
    """Map exact Git blob IDs to source paths after verifying the full frame."""
    source_files = files_under(source_root)
    observed: dict[str, Path] = {}
    for path in source_files:
        blob_id = git_blob_id(path)
        if blob_id in observed:
            raise RuntimeError(f"duplicate Git blob in source corpus: {blob_id}")
        observed[blob_id] = path

    expected = expected_gitskills_frame()
    missing = expected - set(observed)
    unexpected = set(observed) - expected
    if missing or unexpected:
        raise RuntimeError(
            "source corpus does not match the recorded GitSkills frame: "
            f"{len(missing)} missing and {len(unexpected)} unexpected blobs"
        )
    return observed


def benchmark_installed_name(rank: int, original_name: str) -> str:
    """Return the collision-free Arm 3 name fixed by the benchmark protocol."""
    slug = re.sub(r"[^a-z0-9]+", "-", original_name.lower()).strip("-")
    slug = slug[:48].rstrip("-") or "skill"
    return f"gs-r{rank:04d}-{slug}"


def render(source_root: Path) -> str:
    """Render the retained-source description-token record."""
    installed = version("tiktoken")
    if installed != TIKTOKEN_VERSION:
        raise RuntimeError(
            f"tiktoken {TIKTOKEN_VERSION} is required; found {installed}"
        )

    sources = verified_source_map(source_root)
    rows = active_ledger_rows()
    if len(rows) != 119:
        raise RuntimeError(f"expected 119 active retained sources; found {len(rows)}")

    encoding = tiktoken.get_encoding(ENCODING)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: int(item["rank"])):
        source = sources[row["file_sha"]]
        source_text = source.read_text(encoding="utf-8")
        fields = frontmatter_fields(source_text, source)
        original_name = fields.get("name")
        if not isinstance(original_name, str) or not original_name.strip():
            raise RuntimeError(f"missing front-matter name in {source}")
        description = frontmatter_description(source_text, source)
        rank = int(row["rank"])
        writer.writerow(
            {
                "rank": rank,
                "file_sha": row["file_sha"],
                "super_skill": row["super_skill"],
                "original_name": original_name,
                "installed_name": benchmark_installed_name(rank, original_name),
                "tokenizer": ENCODING,
                "tokenizer_package_version": installed,
                "description_tokens": len(encoding.encode(description)),
            }
        )
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        source_root = require_external_source_root(args.sources)
        expected = render(source_root)
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1

    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
        return 0

    actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
    if actual != expected:
        print(
            "research/source-description-token-counts.csv is stale; run "
            "scripts/update_source_token_counts.py with --write",
            file=sys.stderr,
        )
        return 1
    print("Retained-source description-token counts are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
