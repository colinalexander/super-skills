#!/usr/bin/env python3
"""Compare public skill prose with an external, uncommitted source corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
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
    """Return every regular file, including dot-prefixed distributable files."""
    return sorted(path for path in root.rglob("*") if path.is_file())


def require_external_source_root(path: Path) -> Path:
    """Return a resolved source directory that cannot overlap the repository."""
    source_root = path.expanduser().resolve()
    if not source_root.is_dir():
        raise RuntimeError(f"source directory does not exist: {source_root}")
    if ROOT == source_root or ROOT in source_root.parents or source_root in ROOT.parents:
        raise RuntimeError("raw sources must be outside the repository")
    return source_root


def git_blob_id(path: Path) -> str:
    """Return the Git blob identifier for a file's exact bytes."""
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def expected_gitskills_frame() -> set[str]:
    """Return the 999 eligible hashes recorded across the ledger and queue."""
    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        baseline = {
            row["file_sha"]
            for row in csv.DictReader(handle)
            if int(row["rank"]) <= 100
        }
    with (ROOT / "research" / "expansion-queue.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        expansion = {
            row["file_sha"]
            for row in csv.DictReader(handle)
            if row["review_status"] != "excluded-non-skill-placeholder"
        }
    expected = baseline | expansion
    if len(baseline) != 99 or len(expansion) != 900 or len(expected) != 999:
        raise RuntimeError("recorded GitSkills frame does not contain 999 unique hashes")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when an external source and a public skill share too many normalized word shingles."
    )
    parser.add_argument("--sources", type=Path, required=True, help="External raw-source directory")
    parser.add_argument("--threshold", type=float, default=0.20, help="Containment threshold (default: 0.20)")
    parser.add_argument("--ngram", type=int, default=8, help="Words per shingle (default: 8)")
    parser.add_argument(
        "--verify-gitskills-frame",
        action="store_true",
        help="Require external files to match the 999 recorded Git blob hashes",
    )
    args = parser.parse_args()

    try:
        source_root = require_external_source_root(args.sources)
    except RuntimeError as error:
        parser.error(str(error))
    if args.ngram < 5:
        parser.error("ngram must be at least 5 words")
    if not 0 < args.threshold <= 1:
        parser.error("threshold must be in (0, 1]")

    public_files = files_under(ROOT / "skills")
    source_files = files_under(source_root)
    if args.verify_gitskills_frame:
        try:
            expected_hashes = expected_gitskills_frame()
        except RuntimeError as error:
            parser.error(str(error))
        observed_hashes = {git_blob_id(path) for path in source_files}
        if len(source_files) != len(observed_hashes):
            print(
                "Source corpus contains duplicate Git blobs; expected one file per hash.",
                file=sys.stderr,
            )
            return 1
        missing = sorted(expected_hashes - observed_hashes)
        unexpected = sorted(observed_hashes - expected_hashes)
        if missing or unexpected:
            print(
                "Source corpus does not match the recorded GitSkills frame: "
                f"{len(missing)} missing and {len(unexpected)} unexpected blobs.",
                file=sys.stderr,
            )
            return 1
        print(
            f"Source corpus verified: {len(observed_hashes)} files match the "
            "recorded Git blob set."
        )
    public_sets = {path: shingles(path, args.ngram) for path in public_files}
    source_sets = {path: shingles(path, args.ngram) for path in source_files}
    public_digests = {
        path: hashlib.sha256(path.read_bytes()).digest() for path in public_files
    }
    source_digests = {
        path: hashlib.sha256(path.read_bytes()).digest() for path in source_files
    }

    matches: list[tuple[float, int, Path, Path, bool]] = []
    for public_path, public_shingles in public_sets.items():
        for source_path, source_shingles in source_sets.items():
            if public_digests[public_path] == source_digests[source_path]:
                matches.append((1.0, 0, public_path, source_path, True))
                continue
            containment, overlap = score(public_shingles, source_shingles)
            if overlap and containment >= args.threshold:
                matches.append((containment, overlap, public_path, source_path, False))

    if matches:
        print("Potentially close source overlap detected:", file=sys.stderr)
        for containment, overlap, public_path, source_path, exact in sorted(
            matches, reverse=True
        ):
            measure = (
                "exact byte match"
                if exact
                else f"{containment:.1%} containment, {overlap} shingles"
            )
            print(
                f"- {measure}: "
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
