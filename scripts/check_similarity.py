#!/usr/bin/env python3
"""Compare public skill prose with an external, uncommitted source corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
DEFAULT_NGRAM = 8
DEFAULT_THRESHOLD = 0.20
MIN_SHORT_SEQUENCE = 4
CLOSURE_RECORD_FIELDS = {
    "source_file_sha",
    "repository",
    "commit",
    "repository_path",
    "sha256",
    "executable",
    "staged_path",
}


def parameter_summary(closure_file_count: int) -> str:
    """Return the effective matching parameters for the audit record."""
    return (
        "ngram=8, containment_threshold=0.20, "
        "short_fallback=exact-byte+unicode-sequence-containment, "
        "min_short_sequence=4, "
        "tokenization=unicode-word+nonascii-char, "
        f"public_files=all-regular, closure_files={closure_file_count}"
    )


def normalized_words(path: Path) -> tuple[str, ...]:
    """Return Unicode-aware tokens with a non-word character fallback."""
    text = unicodedata.normalize(
        "NFKC", path.read_text(encoding="utf-8", errors="ignore")
    ).casefold()
    words: list[str] = []
    for token in WORD.findall(text):
        if token and all(ord(character) > 127 for character in token):
            words.extend(character for character in token if WORD.fullmatch(character))
        else:
            words.append(token)
    if words:
        return tuple(words)
    return tuple(
        f"char:{character}"
        for character in text
        if not character.isspace() and ord(character) > 127
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


def require_external_source_file(path: Path) -> Path:
    """Return a resolved external file that cannot overlap the repository."""
    source_file = path.expanduser().resolve()
    if not source_file.is_file():
        raise RuntimeError(f"source file does not exist: {source_file}")
    if ROOT == source_file or ROOT in source_file.parents:
        raise RuntimeError("raw source manifests must be outside the repository")
    return source_file


def load_closure_manifest(manifest_path: Path, closure_root: Path) -> tuple[list[Path], str]:
    """Validate staged files and hash canonical pinned-closure records."""
    records: list[str] = []
    staged_files: list[Path] = []
    staged_names: set[str] = set()
    source_paths: set[tuple[str, str]] = set()
    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"invalid closure manifest JSON on line {line_number}"
            ) from error
        if not isinstance(record, dict) or set(record) != CLOSURE_RECORD_FIELDS:
            raise RuntimeError(
                f"closure manifest line {line_number} has incorrect fields"
            )
        for field in (
            "source_file_sha",
            "repository",
            "commit",
            "repository_path",
            "sha256",
            "staged_path",
        ):
            if not isinstance(record[field], str) or not record[field]:
                raise RuntimeError(
                    f"closure manifest line {line_number} has invalid {field}"
                )
        if not isinstance(record["executable"], bool):
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid executable"
            )
        if not re.fullmatch(r"[0-9a-f]{40}", record["source_file_sha"]):
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid source_file_sha"
            )
        if not re.fullmatch(r"[0-9a-f]{40}", record["commit"]):
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid commit"
            )
        if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid sha256"
            )
        staged_relative = Path(record["staged_path"])
        if staged_relative.is_absolute() or ".." in staged_relative.parts:
            raise RuntimeError(
                f"closure manifest line {line_number} has unsafe staged_path"
            )
        staged_name = staged_relative.as_posix()
        if staged_name in staged_names:
            raise RuntimeError(f"duplicate staged_path in closure manifest: {staged_name}")
        staged_names.add(staged_name)
        source_identity = (record["source_file_sha"], record["repository_path"])
        if source_identity in source_paths:
            raise RuntimeError(
                "duplicate source/path identity in closure manifest: "
                f"{source_identity[0]} {source_identity[1]}"
            )
        source_paths.add(source_identity)
        staged_file = (closure_root / staged_relative).resolve()
        if closure_root not in staged_file.parents or not staged_file.is_file():
            raise RuntimeError(
                f"closure manifest line {line_number} maps to a missing file"
            )
        if hashlib.sha256(staged_file.read_bytes()).hexdigest() != record["sha256"]:
            raise RuntimeError(
                f"closure manifest line {line_number} has a digest mismatch"
            )
        staged_files.append(staged_file)
        canonical = {key: record[key] for key in sorted(record) if key != "staged_path"}
        records.append(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        )
    observed_files = set(files_under(closure_root))
    if observed_files != set(staged_files):
        raise RuntimeError(
            "closure manifest does not map every staged file exactly once"
        )
    serialized = "\n".join(sorted(records)) + ("\n" if records else "")
    return sorted(staged_files), hashlib.sha256(serialized.encode("utf-8")).hexdigest()


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
        "--closure-manifest",
        type=Path,
        help="External JSONL manifest mapping staged closure files to canonical records",
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
    if (args.closure_sources is None) != (args.closure_manifest is None):
        parser.error("--closure-sources and --closure-manifest must be used together")
    closure_root = None
    closure_manifest = None
    if args.closure_sources is not None:
        try:
            closure_root = require_external_source_root(args.closure_sources)
            closure_manifest = require_external_source_file(args.closure_manifest)
        except RuntimeError as error:
            parser.error(str(error))
        if (
            source_root == closure_root
            or source_root in closure_root.parents
            or closure_root in source_root.parents
        ):
            parser.error("entry and closure source directories must not overlap")
        if closure_manifest == source_root or source_root in closure_manifest.parents:
            parser.error("entry sources and closure manifest must not overlap")
        if closure_manifest == closure_root or closure_root in closure_manifest.parents:
            parser.error("closure files and closure manifest must not overlap")
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
    closure_source_files: list[Path] = []
    closure_checksum = ""
    if closure_root and closure_manifest:
        try:
            closure_source_files, closure_checksum = load_closure_manifest(
                closure_manifest, closure_root
            )
        except RuntimeError as error:
            parser.error(str(error))
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
        print(
            f"Closure corpus: {len(closure_source_files)} files, "
            f"canonical_record_checksum={closure_checksum}."
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
                if effective_size >= MIN_SHORT_SEQUENCE:
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
