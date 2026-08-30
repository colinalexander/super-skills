#!/usr/bin/env python3
"""Report observed Super Skills loads and requests from Codex desktop history."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


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
SKILL_PATH_MARKERS = (".agents/skills", ".codex/skills")
TurnKey = tuple[str, str]


@dataclass
class SkillUsage:
    """Distinct turns with an observed load or explicit request for one skill."""

    observed_loads: dict[TurnKey, int] = field(default_factory=dict)
    explicit_requests: dict[TurnKey, int] = field(default_factory=dict)


class UsageReportError(RuntimeError):
    """Raised when the supplied history copy cannot be analyzed safely."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Count observed SKILL.md loads and exact $skill-name requests in "
            "a stable, sidecar-free copy of a Codex desktop thread-history "
            "database."
        )
    )
    parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help="Stable copy of a Codex desktop thread_history*.sqlite database.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable report.",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Omit skills with neither an observed load nor a named request.",
    )
    return parser.parse_args(argv)


def connect_database_copy(path: Path) -> sqlite3.Connection:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise UsageReportError(f"history database copy does not exist: {resolved}")

    sidecars = [
        sidecar
        for sidecar in (Path(f"{resolved}-wal"), Path(f"{resolved}-journal"))
        if sidecar.exists()
    ]
    if sidecars:
        names = ", ".join(sidecar.name for sidecar in sidecars)
        raise UsageReportError(
            "history database must be a stable, sidecar-free copy; found " + names
        )

    connection = sqlite3.connect(
        f"{resolved.as_uri()}?mode=ro&immutable=1",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(thread_items)")
        }
    except sqlite3.Error:
        connection.close()
        raise
    if not REQUIRED_COLUMNS <= columns:
        connection.close()
        raise UsageReportError(
            f"unsupported Codex desktop history schema in {resolved}; "
            "expected a compatible thread_items table"
        )
    return connection


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


def observed_load(command: str, skill: str) -> bool:
    """Return whether a command references an installed skill instruction file."""
    normalized = command.replace("\\", "/")
    return any(
        f"{marker}/{skill}/SKILL.md" in normalized
        for marker in SKILL_PATH_MARKERS
    )


def iter_usage_items(connection: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return connection.execute(
        """
        SELECT thread_id, turn_id, created_at_ms, item_json, item_type
        FROM thread_items
        WHERE item_type IN ('userMessage', 'commandExecution')
        ORDER BY created_at_ms, rollout_ordinal
        """
    )


def local_date(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000).astimezone().date().isoformat()


def reconstruct_usage(path: Path) -> dict[str, SkillUsage]:
    usage = {skill: SkillUsage() for skill in SKILLS}
    with closing(connect_database_copy(path)) as connection:
        for row in iter_usage_items(connection):
            try:
                payload = json.loads(row["item_json"])
            except (
                TypeError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                RecursionError,
            ):
                continue
            if not isinstance(payload, dict):
                continue

            thread_id = row["thread_id"]
            turn_id = row["turn_id"]
            if (
                not isinstance(thread_id, str)
                or not thread_id.strip()
                or not isinstance(turn_id, str)
                or not turn_id.strip()
            ):
                continue
            try:
                timestamp = int(row["created_at_ms"])
                local_date(timestamp)
            except (TypeError, ValueError, OverflowError, OSError):
                continue

            turn = (thread_id, turn_id)
            if row["item_type"] == "userMessage":
                text = content_text(payload)
                for skill in SKILLS:
                    if explicit_request(text, skill):
                        usage[skill].explicit_requests.setdefault(turn, timestamp)
            elif row["item_type"] == "commandExecution":
                command = payload.get("command")
                if not isinstance(command, str):
                    continue
                for skill in SKILLS:
                    if observed_load(command, skill):
                        usage[skill].observed_loads.setdefault(turn, timestamp)
    return usage


def report_rows(
    usage: dict[str, SkillUsage], active_only: bool
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for skill in SKILLS:
        load_timestamps = list(usage[skill].observed_loads.values())
        request_timestamps = list(usage[skill].explicit_requests.values())
        row: dict[str, object] = {
            "skill": skill,
            "observed_loads": len(load_timestamps),
            "explicit_requests": len(request_timestamps),
            "first_observed_load": (
                local_date(min(load_timestamps)) if load_timestamps else None
            ),
            "last_observed_load": (
                local_date(max(load_timestamps)) if load_timestamps else None
            ),
            "first_explicit_request": (
                local_date(min(request_timestamps)) if request_timestamps else None
            ),
            "last_explicit_request": (
                local_date(max(request_timestamps)) if request_timestamps else None
            ),
        }
        if not active_only or row["observed_loads"] or row["explicit_requests"]:
            rows.append(row)
    return rows


def print_table(path: Path, rows: list[dict[str, object]]) -> None:
    print("Observed Super Skill loads and exact named requests in Codex desktop")
    print(f"Database copy: {path.expanduser().resolve()}")
    print()
    headings = ("Skill", "Observed loads", "Explicit", "First load", "Last load")
    rendered_rows = [
        (
            str(row["skill"]),
            str(row["observed_loads"]),
            str(row["explicit_requests"]),
            str(row["first_observed_load"] or "—"),
            str(row["last_observed_load"] or "—"),
        )
        for row in rows
    ]
    widths = [
        max([len(headings[index]), *(len(row[index]) for row in rendered_rows)])
        for index in range(len(headings))
    ]
    print(
        f"{headings[0]:<{widths[0]}}  {headings[1]:>{widths[1]}}  "
        f"{headings[2]:>{widths[2]}}  {headings[3]:<{widths[3]}}  "
        f"{headings[4]:<{widths[4]}}"
    )
    for row in rendered_rows:
        print(
            f"{row[0]:<{widths[0]}}  {row[1]:>{widths[1]}}  "
            f"{row[2]:>{widths[2]}}  {row[3]:<{widths[3]}}  "
            f"{row[4]:<{widths[4]}}"
        )
    print()
    print("Observed loads and explicit requests are separate local proxies.")
    print("A skill-file read does not prove that its instructions affected output.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        usage = reconstruct_usage(args.database)
    except (UsageReportError, OSError, sqlite3.Error) as error:
        print(f"usage report failed: {error}", file=sys.stderr)
        return 2

    rows = report_rows(usage, args.active_only)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 2,
                    "scope": "observed-loads-and-explicit-requests",
                    "host": "codex-desktop",
                    "database_copy": str(args.database.expanduser().resolve()),
                    "skills": rows,
                },
                indent=2,
            )
        )
    else:
        print_table(args.database, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
