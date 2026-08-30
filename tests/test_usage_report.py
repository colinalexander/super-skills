from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import usage_report


class UsageReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "history-copy.sqlite"
        with (
            contextlib.closing(sqlite3.connect(self.database)) as connection,
            connection,
        ):
            connection.execute(
                """
                CREATE TABLE thread_items (
                    thread_id TEXT,
                    turn_id TEXT,
                    created_at_ms INTEGER,
                    rollout_ordinal INTEGER,
                    item_json TEXT,
                    item_type TEXT
                )
                """
            )

    def insert(
        self,
        item_type: str,
        thread: object,
        turn: object,
        timestamp: object,
        payload: object,
        ordinal: int = 0,
    ) -> None:
        value = payload if isinstance(payload, str) else json.dumps(payload)
        with (
            contextlib.closing(sqlite3.connect(self.database)) as connection,
            connection,
        ):
            connection.execute(
                "INSERT INTO thread_items VALUES (?, ?, ?, ?, ?, ?)",
                (thread, turn, timestamp, ordinal, value, item_type),
            )

    def test_counts_observed_loads_and_explicit_requests_once_per_turn(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {
                "content": [
                    {
                        "type": "text",
                        "text": "Use $software-delivery and $software-delivery.",
                    }
                ]
            },
        )
        self.insert(
            "commandExecution",
            "thread-1",
            "turn-1",
            1_700_000_000_001,
            {
                "command": (
                    "cat /Users/example/.agents/skills/"
                    "software-delivery/SKILL.md"
                )
            },
            ordinal=1,
        )
        self.insert(
            "commandExecution",
            "thread-1",
            "turn-1",
            1_700_000_000_002,
            {
                "command": (
                    "sed -n '1,80p' /Users/example/.agents/skills/"
                    "software-delivery/SKILL.md"
                )
            },
            ordinal=2,
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["software-delivery"].explicit_requests), 1)
        self.assertEqual(len(usage["software-delivery"].observed_loads), 1)
        self.assertFalse(Path(f"{self.database}-wal").exists())
        self.assertFalse(Path(f"{self.database}-journal").exists())
        self.assertFalse(Path(f"{self.database}-shm").exists())

    def test_ignores_announcements_extended_names_and_repository_source_reads(
        self,
    ) -> None:
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"phase": "commentary", "text": "I’m using interface-design."},
        )
        self.insert(
            "userMessage",
            "thread-1",
            "turn-2",
            1_700_000_000_001,
            {"content": [{"type": "text", "text": "$interface-design-extra"}]},
        )
        self.insert(
            "commandExecution",
            "thread-1",
            "turn-2",
            1_700_000_000_002,
            {"command": "cat skills/interface-design/SKILL.md"},
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["interface-design"].explicit_requests), 0)
        self.assertEqual(len(usage["interface-design"].observed_loads), 0)

    def test_skips_malformed_rows(self) -> None:
        self.insert(
            "userMessage",
            None,
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "$reasoning-modes"}]},
        )
        self.insert(
            "userMessage",
            "thread-1",
            "turn-2",
            "not-a-timestamp",
            {"content": [{"type": "text", "text": "$reasoning-modes"}]},
        )
        self.insert(
            "userMessage",
            "thread-1",
            "turn-3",
            1_700_000_000_002,
            "not-json",
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["reasoning-modes"].explicit_requests), 0)
        self.assertEqual(len(usage["reasoning-modes"].observed_loads), 0)

    def test_rejects_database_with_a_data_bearing_sidecar(self) -> None:
        Path(f"{self.database}-wal").touch()

        with self.assertRaisesRegex(
            usage_report.UsageReportError, "stable, sidecar-free copy"
        ):
            usage_report.reconstruct_usage(self.database)

    def test_rejects_an_unsupported_schema(self) -> None:
        unsupported = Path(self.temporary.name) / "unsupported.sqlite"
        with (
            contextlib.closing(sqlite3.connect(unsupported)) as connection,
            connection,
        ):
            connection.execute("CREATE TABLE something_else (value TEXT)")

        with self.assertRaisesRegex(
            usage_report.UsageReportError, "unsupported Codex desktop history schema"
        ):
            usage_report.reconstruct_usage(unsupported)

    def test_json_report_is_machine_readable(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $reasoning-modes."}]},
        )
        self.insert(
            "commandExecution",
            "thread-1",
            "turn-1",
            1_700_000_000_001,
            {
                "command": (
                    "cat /Users/example/.codex/skills/reasoning-modes/SKILL.md"
                )
            },
            ordinal=1,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = usage_report.main(
                ["--database", str(self.database), "--json", "--active-only"]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(
            payload["scope"], "observed-loads-and-explicit-requests"
        )
        self.assertEqual(payload["host"], "codex-desktop")
        self.assertEqual(
            [row["skill"] for row in payload["skills"]], ["reasoning-modes"]
        )
        self.assertEqual(payload["skills"][0]["observed_loads"], 1)
        self.assertEqual(payload["skills"][0]["explicit_requests"], 1)

    def test_empty_filtered_table_is_renderable(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            usage_report.print_table(self.database, [])

        self.assertIn("Observed loads", output.getvalue())
        self.assertIn("Explicit", output.getvalue())
        self.assertIn("proxies", output.getvalue())


if __name__ == "__main__":
    unittest.main()
