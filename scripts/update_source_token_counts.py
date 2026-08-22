#!/usr/bin/env python3
"""Generate or verify token counts for retained source descriptions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
from importlib.metadata import version
from pathlib import Path

import tiktoken

from update_token_counts import (
    ENCODING,
    TIKTOKEN_VERSION,
    frontmatter_description,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "source-description-token-counts.csv"
FIELDS = (
    "rank",
    "file_sha",
    "super_skill",
    "tokenizer",
    "tokenizer_package_version",
    "description_tokens",
)


def git_blob_id(path: Path) -> str:
    """Return Git's content identifier for one file."""
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def require_external_source_root(path: Path) -> Path:
    """Reject source roots that could expose or absorb repository files."""
    source_root = path.expanduser().resolve()
    repository_root = ROOT.resolve()
    if not source_root.is_dir():
        raise RuntimeError(f"source root is not a directory: {source_root}")
    if (
        source_root == repository_root
        or source_root.is_relative_to(repository_root)
        or repository_root.is_relative_to(source_root)
    ):
        raise RuntimeError(
            "source root must be outside and must not contain the repository"
        )
    return source_root


def active_ledger_rows() -> list[dict[str, str]]:
    """Return retained evidence rows routed to an active skill."""
    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["super_skill"] != "document-productivity"
        ]
    if len(rows) != 119:
        raise RuntimeError(f"expected 119 active retained sources; found {len(rows)}")
    return rows


def expected_frame_hashes() -> set[str]:
    """Return the 999 eligible hashes recorded by the ranked frame."""
    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        ledger_hashes = {row["file_sha"] for row in csv.DictReader(handle)}
    with (ROOT / "research" / "expansion-queue.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        queue_hashes = {
            row["file_sha"]
            for row in csv.DictReader(handle)
            if row["review_status"] != "excluded-non-skill-placeholder"
        }
    expected = ledger_hashes | queue_hashes
    if len(expected) != 999:
        raise RuntimeError(f"expected a 999-hash eligible frame; found {len(expected)}")
    return expected


def verified_source_map(source_root: Path) -> dict[str, Path]:
    """Map exact Git blobs to files after verifying the complete frame."""
    observed: dict[str, Path] = {}
    for path in sorted(item for item in source_root.rglob("*") if item.is_file()):
        blob_id = git_blob_id(path)
        if blob_id in observed:
            raise RuntimeError(f"duplicate Git blob in source corpus: {blob_id}")
        observed[blob_id] = path

    expected = expected_frame_hashes()
    missing = expected - set(observed)
    unexpected = set(observed) - expected
    if missing or unexpected:
        raise RuntimeError(
            "source corpus does not match the recorded GitSkills frame: "
            f"{len(missing)} missing and {len(unexpected)} unexpected blobs"
        )
    return observed


def render(source_root: Path) -> str:
    """Render the active retained-source description-token record."""
    installed = version("tiktoken")
    if installed != TIKTOKEN_VERSION:
        raise RuntimeError(
            f"tiktoken {TIKTOKEN_VERSION} is required; found {installed}"
        )

    sources = verified_source_map(source_root)
    encoding = tiktoken.get_encoding(ENCODING)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in sorted(active_ledger_rows(), key=lambda item: int(item["rank"])):
        source = sources[row["file_sha"]]
        try:
            source_text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise RuntimeError(f"source is not UTF-8 text: {source}") from error
        description = frontmatter_description(source_text, source)
        writer.writerow(
            {
                "rank": int(row["rank"]),
                "file_sha": row["file_sha"],
                "super_skill": row["super_skill"],
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
        expected = render(require_external_source_root(args.sources))
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
