#!/usr/bin/env python3
"""Reconstruct Super Skills usage from retained Codex desktop task history."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]
SKILLS = tuple(sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")))
REQUIRED_COLUMNS = {
    "thread_id",
    "turn_id",
    "created_at_ms",
    "item_json",
    "item_type",
    "rollout_ordinal",
}
ACTIVATION_WORDS = re.compile(
    r"\b(?:using|use|applying|apply|invoking|invoke|loading|load|following|follow)\b",
    re.IGNORECASE,
)
LIST_INTRODUCTION = re.compile(
    r"\b(using|applying|invoking|loading|following)\s+(?:these\s+)?skills?\s*:",
    re.IGNORECASE,
)
EXCLUSION_MARKER = (
    r"(?:\bnot\b(?!\s+only\b)|\bnever\b|\bcannot\b|"
    r"\b(?:ca|did|do|does|must|should|wo|would)n['’]t\b|"
    r"\b(?:except|excluding|without)\b|\brather\s+than\b|"
    r"\bas\s+opposed\s+to\b|\bavoid(?:ed|ing)?\b|"
    r"\bstop(?:ped|ping)?\b)"
)
EXCLUSION_BEFORE_ACTIVATION = re.compile(
    EXCLUSION_MARKER + r"(?:\s+\w+){0,2}\s*$", re.IGNORECASE
)
EXCLUSION_AFTER_ACTIVATION = re.compile(EXCLUSION_MARKER, re.IGNORECASE)
SKILL_FIRST_ACTIVATION = re.compile(
    r"^\s+(?:is|was|will\s+be)\s+(?:the|a)\s+skill\b.{0,60}?"
    r"\b(?:using|applying|invoking|loading|following)\b",
    re.IGNORECASE,
)
CLAUSE_BOUNDARY = re.compile(
    r"(?:[.;:!?](?:\s+|$)|\n+|\b(?:although|but|however|instead|whereas|while)\b)",
    re.IGNORECASE,
)


class UsageReportError(RuntimeError):
    """Raised when local history cannot be read safely."""


@dataclass
class SkillUsage:
    explicit: dict[tuple[str, str], int] = field(default_factory=dict)
    announced: dict[tuple[str, str], int] = field(default_factory=dict)

    @property
    def detected_turns(self) -> set[tuple[str, str]]:
        return set(self.explicit) | set(self.announced)

    @property
    def implicit_turns(self) -> set[tuple[str, str]]:
        return set(self.announced) - set(self.explicit)

    def timestamps(self) -> list[int]:
        values: list[int] = []
        for turn in self.detected_turns:
            candidates = [
                source[turn]
                for source in (self.explicit, self.announced)
                if turn in source
            ]
            values.append(min(candidates))
        return values


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct explicit requests and announced implicit Super Skills "
            "usage from retained local Codex desktop task history."
        )
    )
    parser.add_argument(
        "--database",
        type=Path,
        help=(
            "Codex desktop thread-history SQLite database. By default, use the "
            "newest supported thread_history*.sqlite under the Codex home directory."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable report.",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Omit skills with no detected usage.",
    )
    return parser.parse_args(argv)


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def has_supported_schema(path: Path) -> bool:
    try:
        with connect_read_only(path) as connection:
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(thread_items)")
            }
    except (OSError, sqlite3.Error):
        return False
    return REQUIRED_COLUMNS <= columns


def discover_database(explicit: Path | None = None) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise UsageReportError(f"history database does not exist: {path}")
        if not has_supported_schema(path):
            raise UsageReportError(
                f"unsupported Codex history schema in {path}; "
                "expected a compatible thread_items table"
            )
        return path

    home = codex_home()
    candidates = sorted(
        (path for path in home.glob("thread_history*.sqlite") if path.is_file()),
        key=database_activity_mtime,
        reverse=True,
    )
    for path in candidates:
        if has_supported_schema(path):
            return path.resolve()
    raise UsageReportError(
        "no supported Codex desktop thread_history*.sqlite database found under "
        f"{home}; Codex CLI session history is not currently supported"
    )


def database_activity_mtime(path: Path) -> float:
    mtimes = [path.stat().st_mtime]
    wal = Path(f"{path}-wal")
    try:
        mtimes.append(wal.stat().st_mtime)
    except (FileNotFoundError, NotADirectoryError):
        # Codex desktop can checkpoint and remove a WAL between discovery and
        # this lookup. The main database remains a valid recency signal.
        pass
    return max(mtimes)


def sqlite_connection(path: Path, parameters: str) -> sqlite3.Connection:
    connection = sqlite3.connect(f"{path.as_uri()}?{parameters}", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def file_fingerprint(path: Path) -> tuple[int, int, int, int, int]:
    """Return metadata that changes when a SQLite file generation changes."""

    metadata = path.stat()
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


@contextmanager
def connect_read_only(path: Path) -> Iterator[sqlite3.Connection]:
    resolved = path.resolve()
    wal = Path(f"{resolved}-wal")
    for _attempt in range(5):
        wal_exists = wal.is_file()
        if wal_exists:
            with tempfile.TemporaryDirectory(
                prefix="super-skills-history-"
            ) as directory:
                snapshot = Path(directory) / resolved.name
                try:
                    before = (file_fingerprint(resolved), file_fingerprint(wal))
                    shutil.copy2(resolved, snapshot)
                    shutil.copy2(wal, Path(f"{snapshot}-wal"))
                    after = (file_fingerprint(resolved), file_fingerprint(wal))
                except FileNotFoundError:
                    # A checkpoint can remove the WAL between observation and
                    # copying. Re-evaluate the source sidecar state.
                    continue
                if before != after:
                    # Never open a staged main/WAL pair when either source file
                    # changed during the sequential copies.
                    continue
                with closing(sqlite_connection(snapshot, "mode=ro")) as connection:
                    yield connection
            return

        with closing(
            sqlite_connection(resolved, "mode=ro&immutable=1")
        ) as connection:
            yield connection
        return

    raise UsageReportError(
        f"Codex desktop history sidecars changed repeatedly while reading {resolved}"
    )


def content_text(payload: dict[str, object]) -> str:
    content = payload.get("content")
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def explicit_request(text: str, skill: str) -> bool:
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_-])\${re.escape(skill)}(?![A-Za-z0-9_-])",
        re.IGNORECASE,
    )
    return bool(pattern.search(text))


def announced_use(text: str, skill: str) -> bool:
    """Return whether nearby activation language announces use of a skill.

    This intentionally requires an activation verb shortly before the exact
    skill name. A bare mention in commentary is not treated as usage.
    """

    skill_pattern = re.compile(
        rf"(?<![A-Za-z0-9_-]){re.escape(skill)}(?![A-Za-z0-9_-])",
        re.IGNORECASE,
    )
    normalized = LIST_INTRODUCTION.sub(r"\1 skills ", text)
    for clause in CLAUSE_BOUNDARY.split(normalized):
        for skill_match in skill_pattern.finditer(clause):
            prefix = clause[: skill_match.start()]
            for activation in ACTIVATION_WORDS.finditer(prefix):
                before = prefix[: activation.start()]
                between = prefix[activation.end() :]
                if (
                    not EXCLUSION_BEFORE_ACTIVATION.search(before)
                    and not EXCLUSION_AFTER_ACTIVATION.search(between)
                ):
                    return True
            suffix = clause[skill_match.end() :]
            skill_first = SKILL_FIRST_ACTIVATION.match(suffix)
            if skill_first and not EXCLUSION_AFTER_ACTIVATION.search(
                skill_first.group(0)
            ):
                return True
    return False


def iter_history_rows(connection: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return connection.execute(
        """
        SELECT thread_id, turn_id, created_at_ms, item_type, item_json
        FROM thread_items
        WHERE item_type IN ('userMessage', 'agentMessage')
        ORDER BY created_at_ms, rollout_ordinal
        """
    )


def reconstruct_usage(path: Path) -> dict[str, SkillUsage]:
    usage = {skill: SkillUsage() for skill in SKILLS}
    with connect_read_only(path) as connection:
        for row in iter_history_rows(connection):
            try:
                payload = json.loads(row["item_json"])
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue

            item_type = row["item_type"]
            if item_type == "userMessage":
                text = content_text(payload)
            elif item_type == "agentMessage" and payload.get("phase") == "commentary":
                value = payload.get("text")
                text = value if isinstance(value, str) else ""
            else:
                continue

            turn = (str(row["thread_id"]), str(row["turn_id"]))
            timestamp = int(row["created_at_ms"])
            for skill, record in usage.items():
                if item_type == "userMessage" and explicit_request(text, skill):
                    record.explicit.setdefault(turn, timestamp)
                elif item_type == "agentMessage" and announced_use(text, skill):
                    record.announced.setdefault(turn, timestamp)
    return usage


def local_date(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000).astimezone().date().isoformat()


def report_rows(usage: dict[str, SkillUsage], active_only: bool) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for skill in SKILLS:
        record = usage[skill]
        timestamps = record.timestamps()
        row: dict[str, object] = {
            "skill": skill,
            "detected_turns": len(record.detected_turns),
            "explicit_requests": len(record.explicit),
            "inferred_implicit_turns": len(record.implicit_turns),
            "announced_turns": len(record.announced),
            "first_detected": local_date(min(timestamps)) if timestamps else None,
            "last_detected": local_date(max(timestamps)) if timestamps else None,
        }
        if not active_only or row["detected_turns"]:
            rows.append(row)
    return rows


def print_table(path: Path, rows: list[dict[str, object]]) -> None:
    print("Experimental local Codex desktop usage (reconstructed)")
    print(f"Database: {path}")
    print()
    headings = ("Skill", "Detected", "Explicit", "Implicit*", "First", "Last")
    rendered_rows = [
        (
            str(row["skill"]),
            str(row["detected_turns"]),
            str(row["explicit_requests"]),
            str(row["inferred_implicit_turns"]),
            str(row["first_detected"] or "—"),
            str(row["last_detected"] or "—"),
        )
        for row in rows
    ]
    widths = [
        max([len(headings[index]), *(len(row[index]) for row in rendered_rows)])
        for index in range(len(headings))
    ]
    print(
        f"{headings[0]:<{widths[0]}}  {headings[1]:>{widths[1]}}  "
        f"{headings[2]:>{widths[2]}}  {headings[3]:>{widths[3]}}  "
        f"{headings[4]:<{widths[4]}}  {headings[5]:<{widths[5]}}"
    )
    for row in rendered_rows:
        print(
            f"{row[0]:<{widths[0]}}  {row[1]:>{widths[1]}}  "
            f"{row[2]:>{widths[2]}}  {row[3]:>{widths[3]}}  "
            f"{row[4]:<{widths[4]}}  {row[5]:<{widths[5]}}"
        )
    print()
    print("* Announced use without a matching explicit $skill-name request.")
    print("Detected counts are heuristic, not native activation telemetry.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        path = discover_database(args.database)
        usage = reconstruct_usage(path)
    except (UsageReportError, OSError, sqlite3.Error) as error:
        print(f"usage report failed: {error}", file=sys.stderr)
        return 2

    rows = report_rows(usage, args.active_only)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "experimental",
                    "source": "retained-local-codex-desktop-history",
                    "database": str(path),
                    "skills": rows,
                },
                indent=2,
            )
        )
    else:
        print_table(path, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
