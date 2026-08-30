#!/usr/bin/env python3
"""Report exact Super Skills requests from a Codex desktop history copy."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from contextlib import closing
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


class UsageReportError(RuntimeError):
    """Raised when the supplied history copy cannot be analyzed safely."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Count exact $skill-name requests in a stable, sidecar-free copy "
            "of a Codex desktop thread-history database."
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
        help="Omit skills with no exact named requests.",
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


def iter_user_messages(connection: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return connection.execute(
        """
        SELECT thread_id, turn_id, created_at_ms, item_json
        FROM thread_items
        WHERE item_type = 'userMessage'
        ORDER BY created_at_ms, rollout_ordinal
        """
    )


def local_date(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000).astimezone().date().isoformat()


def reconstruct_requests(path: Path) -> dict[str, dict[tuple[str, str], int]]:
    requests: dict[str, dict[tuple[str, str], int]] = {
        skill: {} for skill in SKILLS
    }
    with closing(connect_database_copy(path)) as connection:
        for row in iter_user_messages(connection):
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

            text = content_text(payload)
            turn = (thread_id, turn_id)
            for skill in SKILLS:
                if explicit_request(text, skill):
                    requests[skill].setdefault(turn, timestamp)
    return requests


def report_rows(
    requests: dict[str, dict[tuple[str, str], int]], active_only: bool
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for skill in SKILLS:
        timestamps = list(requests[skill].values())
        row: dict[str, object] = {
            "skill": skill,
            "explicit_requests": len(timestamps),
            "first_requested": local_date(min(timestamps)) if timestamps else None,
            "last_requested": local_date(max(timestamps)) if timestamps else None,
        }
        if not active_only or row["explicit_requests"]:
            rows.append(row)
    return rows


def print_table(path: Path, rows: list[dict[str, object]]) -> None:
    print("Exact $skill-name mentions in Codex desktop user turns")
    print(f"Database copy: {path.expanduser().resolve()}")
    print()
    headings = ("Skill", "Requests", "First", "Last")
    rendered_rows = [
        (
            str(row["skill"]),
            str(row["explicit_requests"]),
            str(row["first_requested"] or "—"),
            str(row["last_requested"] or "—"),
        )
        for row in rows
    ]
    widths = [
        max([len(headings[index]), *(len(row[index]) for row in rendered_rows)])
        for index in range(len(headings))
    ]
    print(
        f"{headings[0]:<{widths[0]}}  {headings[1]:>{widths[1]}}  "
        f"{headings[2]:<{widths[2]}}  {headings[3]:<{widths[3]}}"
    )
    for row in rendered_rows:
        print(
            f"{row[0]:<{widths[0]}}  {row[1]:>{widths[1]}}  "
            f"{row[2]:<{widths[2]}}  {row[3]:<{widths[3]}}"
        )
    print()
    print("Counts are a textual proxy, not automatic-activation telemetry.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        requests = reconstruct_requests(args.database)
    except (UsageReportError, OSError, sqlite3.Error) as error:
        print(f"usage report failed: {error}", file=sys.stderr)
        return 2

    rows = report_rows(requests, args.active_only)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "scope": "exact-named-requests-only",
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
