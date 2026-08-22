#!/usr/bin/env python3
"""Compare public skill prose with an external, uncommitted source corpus."""

from __future__ import annotations

import argparse
import codecs
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
    "entry_repository_path",
    "selection_method",
    "candidate_order_sha256",
    "selected_candidate_index",
    "repository_path",
    "sha256",
    "executable",
    "staged_path",
}
OCCURRENCE_RECORD_FIELDS = {"source_file_sha", "selection_method", "candidates"}
CANDIDATE_FIELDS = {
    "repository", "entry_repository_path", "commit", "reachable", "entry_blob"
}
TEXT_SUFFIXES = {
    ".css", ".html", ".js", ".json", ".jsx", ".md", ".py", ".sh",
    ".svg", ".toml", ".ts", ".tsx", ".txt", ".yaml", ".yml",
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
    data = path.read_bytes()
    try:
        if data.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
            decoded = data.decode("utf-32")
        elif data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            decoded = data.decode("utf-16")
        elif data.startswith(codecs.BOM_UTF8):
            decoded = data.decode("utf-8-sig")
        else:
            decoded = data.decode("utf-8")
    except UnicodeDecodeError as error:
        if path.suffix.casefold() in TEXT_SUFFIXES:
            raise RuntimeError(f"text file has an unsupported encoding: {path}") from error
        return ()
    if "\0" in decoded and path.suffix.casefold() in TEXT_SUFFIXES:
        raise RuntimeError(f"text file has an unsupported NUL-bearing encoding: {path}")
    text = unicodedata.normalize("NFKC", decoded).casefold()
    words: list[str] = []
    for token in WORD.findall(text):
        if token.isascii():
            words.append(token)
            continue
        ascii_run: list[str] = []
        for character in token:
            if character.isascii() and character.isalnum():
                ascii_run.append(character)
                continue
            if ascii_run:
                words.append("".join(ascii_run))
                ascii_run.clear()
            if ord(character) > 127 and WORD.fullmatch(character):
                words.append(character)
        if ascii_run:
            words.append("".join(ascii_run))
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


def expected_active_source_hashes() -> set[str]:
    """Return the exact active retained source population."""
    with (ROOT / "research" / "review-decisions.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        expected = {
            row["file_sha"]
            for row in csv.DictReader(handle)
            if row["decision"] == "retained"
            and row["super_skill"] != "document-productivity"
        }
    if len(expected) != 119:
        raise RuntimeError("recorded active retained population is not 119 unique hashes")
    return expected


def ledger_exact_occurrences() -> dict[str, tuple[str, str, str]]:
    """Return ledger-backed exact occurrences for active retained sources."""
    expected = expected_active_source_hashes()
    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["file_sha"]: row for row in csv.DictReader(handle)}
    exact: dict[str, tuple[str, str, str]] = {}
    for source_hash in expected:
        row = rows[source_hash]
        if row["provenance_status"] == "upstream exact Git blob verified":
            exact[source_hash] = (
                row["reference_repository"],
                row["reference_commit"],
                row["reference_path"],
            )
    return exact


def load_occurrence_manifest(
    manifest_path: Path,
) -> dict[str, tuple[str, str, str, str, str, int]]:
    """Validate source-level occurrence selection and return pinned tuples."""
    expected_sources = expected_active_source_hashes()
    exact_occurrences = ledger_exact_occurrences()
    selections: dict[str, tuple[str, str, str, str, str, int]] = {}
    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"invalid occurrence manifest JSON on line {line_number}"
            ) from error
        if not isinstance(record, dict) or set(record) != OCCURRENCE_RECORD_FIELDS:
            raise RuntimeError(
                f"occurrence manifest line {line_number} has incorrect fields"
            )
        source_hash = record["source_file_sha"]
        method = record["selection_method"]
        candidates = record["candidates"]
        if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-f]{40}", source_hash):
            raise RuntimeError(
                f"occurrence manifest line {line_number} has invalid source_file_sha"
            )
        if source_hash in selections:
            raise RuntimeError(f"duplicate occurrence record for source: {source_hash}")
        if not isinstance(method, str) or method not in {
            "ledger-exact", "sorted-first-reachable-exact"
        }:
            raise RuntimeError(
                f"occurrence manifest line {line_number} has invalid selection_method"
            )
        if not isinstance(candidates, list) or not candidates:
            raise RuntimeError(
                f"occurrence manifest line {line_number} has no candidates"
            )
        candidate_keys: list[tuple[str, str]] = []
        for candidate in candidates:
            if not isinstance(candidate, dict) or set(candidate) != CANDIDATE_FIELDS:
                raise RuntimeError(
                    f"occurrence manifest line {line_number} has invalid candidate fields"
                )
            if not all(
                isinstance(candidate[field], str) and candidate[field]
                for field in ("repository", "entry_repository_path", "commit")
            ):
                raise RuntimeError(
                    f"occurrence manifest line {line_number} has invalid candidate identity"
                )
            if not re.fullmatch(r"[0-9a-f]{40}", candidate["commit"]):
                raise RuntimeError(
                    f"occurrence manifest line {line_number} has invalid candidate commit"
                )
            if not isinstance(candidate["reachable"], bool):
                raise RuntimeError(
                    f"occurrence manifest line {line_number} has invalid reachable flag"
                )
            entry_blob = candidate["entry_blob"]
            if entry_blob is not None and (
                not isinstance(entry_blob, str)
                or not re.fullmatch(r"[0-9a-f]{40}", entry_blob)
            ):
                raise RuntimeError(
                    f"occurrence manifest line {line_number} has invalid entry_blob"
                )
            candidate_keys.append(
                (candidate["repository"], candidate["entry_repository_path"])
            )
        if candidate_keys != sorted(candidate_keys) or len(candidate_keys) != len(set(candidate_keys)):
            raise RuntimeError(
                f"occurrence candidates are not unique and case-sensitively sorted: {source_hash}"
            )
        qualifying = [
            index for index, candidate in enumerate(candidates)
            if candidate["reachable"] and candidate["entry_blob"] == source_hash
        ]
        if not qualifying:
            raise RuntimeError(f"no reachable exact occurrence for source: {source_hash}")
        selected_index = qualifying[0]
        selected = candidates[selected_index]
        if source_hash in exact_occurrences:
            if method != "ledger-exact" or selected_index != 0 or len(candidates) != 1:
                raise RuntimeError(f"invalid ledger-exact selection record: {source_hash}")
            if (
                selected["repository"], selected["commit"], selected["entry_repository_path"]
            ) != exact_occurrences[source_hash]:
                raise RuntimeError(f"ledger-exact occurrence differs from ledger: {source_hash}")
        elif method != "sorted-first-reachable-exact":
            raise RuntimeError(
                f"unverified source must use deterministic fallback selection: {source_hash}"
            )
        candidate_serialized = json.dumps(
            candidates, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        candidate_checksum = hashlib.sha256(candidate_serialized).hexdigest()
        selections[source_hash] = (
            selected["repository"], selected["commit"],
            selected["entry_repository_path"], method, candidate_checksum,
            selected_index,
        )
    if set(selections) != expected_sources:
        raise RuntimeError("occurrence manifest does not cover exactly 119 active sources")
    return selections


def load_closure_manifest(
    manifest_path: Path,
    closure_root: Path,
    occurrence_selections: dict[str, tuple[str, str, str, str, str, int]],
) -> tuple[list[Path], str]:
    """Validate staged files and hash canonical pinned-closure records."""
    records: list[str] = []
    staged_files: list[Path] = []
    staged_names: set[str] = set()
    source_paths: set[tuple[str, str]] = set()
    manifest_source_hashes: set[str] = set()
    entry_source_hashes: set[str] = set()
    pinned_occurrences: dict[str, tuple[str, str, str, str, str, int]] = {}
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
            "entry_repository_path",
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
        if not isinstance(record["selection_method"], str) or record[
            "selection_method"
        ] not in {
            "ledger-exact", "sorted-first-reachable-exact"
        }:
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid selection_method"
            )
        if type(record["selected_candidate_index"]) is not int or record[
            "selected_candidate_index"
        ] < 0:
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid selected_candidate_index"
            )
        candidate_checksum = record["candidate_order_sha256"]
        if not isinstance(candidate_checksum, str) or not re.fullmatch(
            r"[0-9a-f]{64}", candidate_checksum
        ):
            raise RuntimeError(
                f"closure manifest line {line_number} has invalid candidate_order_sha256"
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
        manifest_source_hashes.add(record["source_file_sha"])
        occurrence = (
            record["repository"],
            record["commit"],
            record["entry_repository_path"],
            record["selection_method"],
            candidate_checksum,
            record["selected_candidate_index"],
        )
        previous_occurrence = pinned_occurrences.setdefault(
            record["source_file_sha"], occurrence
        )
        if occurrence != previous_occurrence:
            raise RuntimeError(
                "closure manifest uses multiple pinned occurrences for source: "
                f"{record['source_file_sha']}"
            )
        if occurrence_selections.get(record["source_file_sha"]) != occurrence:
            raise RuntimeError(
                "closure occurrence differs from the validated selection record: "
                f"{record['source_file_sha']}"
            )
        staged_file = (closure_root / staged_relative).resolve()
        if closure_root not in staged_file.parents or not staged_file.is_file():
            raise RuntimeError(
                f"closure manifest line {line_number} maps to a missing file"
            )
        if hashlib.sha256(staged_file.read_bytes()).hexdigest() != record["sha256"]:
            raise RuntimeError(
                f"closure manifest line {line_number} has a digest mismatch"
            )
        actual_executable = bool(staged_file.stat().st_mode & 0o111)
        if actual_executable != record["executable"]:
            raise RuntimeError(
                f"closure manifest line {line_number} has an executable-bit mismatch"
            )
        if (
            record["repository_path"] == record["entry_repository_path"]
            and git_blob_id(staged_file) == record["source_file_sha"]
        ):
            entry_source_hashes.add(record["source_file_sha"])
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
    expected_sources = expected_active_source_hashes()
    if manifest_source_hashes != expected_sources:
        missing = expected_sources - manifest_source_hashes
        extra = manifest_source_hashes - expected_sources
        raise RuntimeError(
            "closure manifest source coverage differs from the 119 active retained "
            f"hashes (missing={len(missing)}, extra={len(extra)})"
        )
    if entry_source_hashes != expected_sources:
        missing_entries = expected_sources - entry_source_hashes
        raise RuntimeError(
            "closure manifest lacks a validated entry blob for "
            f"{len(missing_entries)} active retained source hashes"
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
        "--closure-occurrences",
        type=Path,
        help="External JSONL manifest proving deterministic source-occurrence selection",
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
    closure_arguments = (
        args.closure_sources, args.closure_manifest, args.closure_occurrences
    )
    if any(value is not None for value in closure_arguments) and not all(
        value is not None for value in closure_arguments
    ):
        parser.error(
            "--closure-sources, --closure-manifest, and --closure-occurrences "
            "must be used together"
        )
    closure_root = None
    closure_manifest = None
    closure_occurrences = None
    if args.closure_sources is not None:
        try:
            closure_root = require_external_source_root(args.closure_sources)
            closure_manifest = require_external_source_file(args.closure_manifest)
            closure_occurrences = require_external_source_file(args.closure_occurrences)
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
        if closure_occurrences == source_root or source_root in closure_occurrences.parents:
            parser.error("entry sources and occurrence manifest must not overlap")
        if closure_occurrences == closure_root or closure_root in closure_occurrences.parents:
            parser.error("closure files and occurrence manifest must not overlap")
        if closure_occurrences == closure_manifest:
            parser.error("closure and occurrence manifests must be separate files")
    verification_required = args.verify_gitskills_frame or closure_root is not None
    if args.ngram < 5:
        parser.error("ngram must be at least 5 words")
    if not 0 < args.threshold <= 1:
        parser.error("threshold must be in (0, 1]")
    if verification_required and (
        args.ngram != DEFAULT_NGRAM or args.threshold != DEFAULT_THRESHOLD
    ):
        parser.error(
            "frame verification and closure scans require ngram=8 and threshold=0.20"
        )

    public_files = files_under(ROOT / "skills")
    entry_source_files = files_under(source_root)
    closure_source_files: list[Path] = []
    closure_checksum = ""
    if closure_root and closure_manifest and closure_occurrences:
        try:
            occurrence_selections = load_occurrence_manifest(closure_occurrences)
            closure_source_files, closure_checksum = load_closure_manifest(
                closure_manifest, closure_root, occurrence_selections
            )
        except RuntimeError as error:
            parser.error(str(error))
    if verification_required:
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
    try:
        public_words = {path: normalized_words(path) for path in public_files}
        source_words = {path: normalized_words(path) for path in source_files}
    except RuntimeError as error:
        parser.error(str(error))
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
