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
DEFAULT_NGRAM = 8
DEFAULT_THRESHOLD = 0.20


def parameter_summary(closure_file_count: int) -> str:
    """Return the effective matching parameters for the audit record."""
    return (
        "ngram=8, containment_threshold=0.20, "
        "short_fallback=exact-byte+normalized-sequence-containment, "
        f"public_files=all-regular, closure_files={closure_file_count}"
    )


def normalized_words(path: Path) -> tuple[str, ...]:
    """Return case- and formatting-insensitive words for textual comparison."""
    return tuple(
        WORD.findall(path.read_text(encoding="utf-8", errors="ignore").lower())
    )


def shingles(words: tuple[str, ...], size: int) -> set[tuple[str, ...]]:
    return {
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    }


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
    parser.add_argument(
        "--closure-sources",
        type=Path,
        help="External pinned dependency-closure files to scan in addition to entries",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Containment threshold (default: 0.20)",
    )
    parser.add_argument(
        "--ngram",
        type=int,
        default=DEFAULT_NGRAM,
        help="Words per shingle (default: 8)",
    )
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
    closure_root = None
    if args.closure_sources is not None:
        try:
            closure_root = require_external_source_root(args.closure_sources)
        except RuntimeError as error:
            parser.error(str(error))
        if (
            source_root == closure_root
            or source_root in closure_root.parents
            or closure_root in source_root.parents
        ):
            parser.error("entry and closure source directories must not overlap")
    if args.ngram < 5:
        parser.error("ngram must be at least 5 words")
    if not 0 < args.threshold <= 1:
        parser.error("threshold must be in (0, 1]")
    if args.verify_gitskills_frame and (
        args.ngram != DEFAULT_NGRAM or args.threshold != DEFAULT_THRESHOLD
    ):
        parser.error(
            "--verify-gitskills-frame requires ngram=8 and threshold=0.20"
        )

    public_files = files_under(ROOT / "skills")
    entry_source_files = files_under(source_root)
    closure_source_files = files_under(closure_root) if closure_root else []
    if args.verify_gitskills_frame:
        try:
            expected_hashes = expected_gitskills_frame()
        except RuntimeError as error:
            parser.error(str(error))
        observed_hashes = {git_blob_id(path) for path in entry_source_files}
        if len(entry_source_files) != len(observed_hashes):
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
    if closure_root:
        closure_digest = hashlib.sha256()
        for path in closure_source_files:
            closure_digest.update(str(path.relative_to(closure_root)).encode("utf-8"))
            closure_digest.update(b"\0")
            closure_digest.update(hashlib.sha256(path.read_bytes()).digest())
            closure_digest.update(b"\n")
        print(
            f"Closure corpus: {len(closure_source_files)} files, "
            f"checksum={closure_digest.hexdigest()}."
        )
    print(f"Effective parameters: {parameter_summary(len(closure_source_files))}.")
    source_files = entry_source_files + closure_source_files
    public_words = {path: normalized_words(path) for path in public_files}
    source_words = {path: normalized_words(path) for path in source_files}
    public_sets = {
        path: shingles(words, args.ngram) for path, words in public_words.items()
    }
    source_sets = {
        path: shingles(words, args.ngram) for path, words in source_words.items()
    }
    public_digests = {
        path: hashlib.sha256(path.read_bytes()).digest() for path in public_files
    }
    source_digests = {
        path: hashlib.sha256(path.read_bytes()).digest() for path in source_files
    }

    matches: list[tuple[float, int, Path, Path, str]] = []
    for public_path, public_shingles in public_sets.items():
        for source_path, source_shingles in source_sets.items():
            if public_digests[public_path] == source_digests[source_path]:
                matches.append((1.0, 0, public_path, source_path, "exact byte match"))
                continue
            if (
                public_words[public_path]
                and public_words[public_path] == source_words[source_path]
            ):
                matches.append(
                    (1.0, 0, public_path, source_path, "normalized exact match")
                )
                continue
            short_measure = ""
            if not public_shingles or not source_shingles:
                effective_size = min(
                    args.ngram,
                    len(public_words[public_path]),
                    len(source_words[source_path]),
                )
                if effective_size:
                    public_shingles = shingles(
                        public_words[public_path], effective_size
                    )
                    source_shingles = shingles(
                        source_words[source_path], effective_size
                    )
                    short_measure = f"normalized {effective_size}-word"
            containment, overlap = score(public_shingles, source_shingles)
            if overlap and containment >= args.threshold:
                measure = (
                    f"{containment:.1%} {short_measure} containment, "
                    f"{overlap} shingles"
                    if short_measure
                    else ""
                )
                matches.append(
                    (containment, overlap, public_path, source_path, measure)
                )

    if matches:
        print("Potentially close source overlap detected:", file=sys.stderr)
        for containment, overlap, public_path, source_path, exact_measure in sorted(
            matches, reverse=True
        ):
            measure = (
                exact_measure
                if exact_measure
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
