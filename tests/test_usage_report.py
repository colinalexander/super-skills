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

    def test_counts_exact_named_requests_once_per_turn(self) -> None:
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

        requests = usage_report.reconstruct_requests(self.database)

        self.assertEqual(len(requests["software-delivery"]), 1)
        self.assertFalse(Path(f"{self.database}-wal").exists())
        self.assertFalse(Path(f"{self.database}-journal").exists())
        self.assertFalse(Path(f"{self.database}-shm").exists())

    def test_ignores_announced_implicit_use_and_extended_names(self) -> None:
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

        requests = usage_report.reconstruct_requests(self.database)

        self.assertEqual(len(requests["interface-design"]), 0)

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

        requests = usage_report.reconstruct_requests(self.database)

        self.assertEqual(len(requests["reasoning-modes"]), 0)

    def test_rejects_database_with_a_data_bearing_sidecar(self) -> None:
        Path(f"{self.database}-wal").touch()

        with self.assertRaisesRegex(
            usage_report.UsageReportError, "stable, sidecar-free copy"
        ):
            usage_report.reconstruct_requests(self.database)

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
            usage_report.reconstruct_requests(unsupported)

    def test_json_report_is_machine_readable(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $reasoning-modes."}]},
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = usage_report.main(
                ["--database", str(self.database), "--json", "--active-only"]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(payload["scope"], "exact-named-requests-only")
        self.assertEqual(payload["host"], "codex-desktop")
        self.assertEqual(
            [row["skill"] for row in payload["skills"]], ["reasoning-modes"]
        )

    def test_empty_filtered_table_is_renderable(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            usage_report.print_table(self.database, [])

        self.assertIn("Requests", output.getvalue())
        self.assertIn("textual proxy", output.getvalue())


if __name__ == "__main__":
    unittest.main()
