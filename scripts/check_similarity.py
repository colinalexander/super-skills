#!/usr/bin/env python3
"""Compare public skill prose with an external, uncommitted source corpus."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


def shingles(path: Path, size: int) -> set[tuple[str, ...]]:
    words = WORD.findall(path.read_text(encoding="utf-8", errors="ignore").lower())
    return {tuple(words[index : index + size]) for index in range(len(words) - size + 1)}


def score(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> tuple[float, int]:
    if not left or not right:
        return 0.0, 0
    overlap = len(left & right)
    containment = overlap / min(len(left), len(right))
    return containment, overlap


def files_under(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and not path.name.startswith("."))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when an external source and a public skill share too many normalized word shingles."
    )
    parser.add_argument("--sources", type=Path, required=True, help="External raw-source directory")
    parser.add_argument("--threshold", type=float, default=0.20, help="Containment threshold (default: 0.20)")
    parser.add_argument("--ngram", type=int, default=8, help="Words per shingle (default: 8)")
    args = parser.parse_args()

    source_root = args.sources.expanduser().resolve()
    if not source_root.is_dir():
        parser.error(f"source directory does not exist: {source_root}")
    if ROOT == source_root or ROOT in source_root.parents or source_root in ROOT.parents:
        parser.error("raw sources must be outside the repository")
    if args.ngram < 5:
        parser.error("ngram must be at least 5 words")
    if not 0 < args.threshold <= 1:
        parser.error("threshold must be in (0, 1]")

    public_files = files_under(ROOT / "skills")
    source_files = files_under(source_root)
    public_sets = {path: shingles(path, args.ngram) for path in public_files}
    source_sets = {path: shingles(path, args.ngram) for path in source_files}

    matches: list[tuple[float, int, Path, Path]] = []
    for public_path, public_shingles in public_sets.items():
        for source_path, source_shingles in source_sets.items():
            containment, overlap = score(public_shingles, source_shingles)
            if overlap and containment >= args.threshold:
                matches.append((containment, overlap, public_path, source_path))

    if matches:
        print("Potentially close source overlap detected:", file=sys.stderr)
        for containment, overlap, public_path, source_path in sorted(matches, reverse=True):
            print(
                f"- {containment:.1%} containment, {overlap} shingles: "
                f"{public_path.relative_to(ROOT)} <> {source_path}",
                file=sys.stderr,
            )
        return 1

    print(
        f"Similarity check passed: {len(public_files)} public files compared with "
        f"{len(source_files)} external files at {args.threshold:.0%} containment."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
