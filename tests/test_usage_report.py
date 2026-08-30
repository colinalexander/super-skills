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
        self.database = Path(self.temporary.name) / "history.sqlite"
        with (
            contextlib.closing(sqlite3.connect(self.database)) as connection,
            connection,
        ):
            connection.execute(
                """
                CREATE TABLE thread_items (
                    thread_id TEXT NOT NULL,
                    turn_id TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL,
                    rollout_ordinal INTEGER NOT NULL,
                    item_json TEXT NOT NULL,
                    item_type TEXT NOT NULL
                )
                """
            )

    def insert(
        self,
        item_type: str,
        thread: str,
        turn: str,
        timestamp: int,
        payload: object,
        ordinal: int = 0,
    ) -> None:
        value = payload if isinstance(payload, str) else json.dumps(payload)
        with (
            contextlib.closing(sqlite3.connect(self.database)) as connection,
            connection,
        ):
            connection.execute(
                """
                INSERT INTO thread_items (
                    thread_id,
                    turn_id,
                    created_at_ms,
                    rollout_ordinal,
                    item_json,
                    item_type
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (thread, turn, timestamp, ordinal, value, item_type),
            )

    def test_reconstructs_explicit_and_announced_implicit_turns(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $software-delivery."}]},
        )
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-1",
            1_700_000_001_000,
            {
                "phase": "commentary",
                "text": "I’m using the software-delivery workflow for this change.",
            },
            ordinal=1,
        )
        self.insert(
            "userMessage",
            "thread-1",
            "turn-2",
            1_700_100_000_000,
            {"content": [{"type": "text", "text": "Make the layout responsive."}]},
        )
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-2",
            1_700_100_001_000,
            {
                "phase": "commentary",
                "text": "I’m using interface-design guidance for responsive behavior.",
            },
            ordinal=1,
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["software-delivery"].detected_turns), 1)
        self.assertEqual(len(usage["software-delivery"].explicit), 1)
        self.assertEqual(len(usage["software-delivery"].implicit_turns), 0)
        self.assertEqual(len(usage["interface-design"].detected_turns), 1)
        self.assertEqual(len(usage["interface-design"].explicit), 0)
        self.assertEqual(len(usage["interface-design"].implicit_turns), 1)

    def test_ignores_bare_mentions_near_names_and_non_commentary(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {
                "content": [
                    {"type": "text", "text": "$software-delivery-extra is unrelated."}
                ]
            },
        )
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-1",
            1_700_000_001_000,
            {
                "phase": "commentary",
                "text": "The software-delivery description is concise.",
            },
            ordinal=1,
        )
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-2",
            1_700_100_000_000,
            {
                "phase": "final_answer",
                "text": "I’m using software-delivery.",
            },
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["software-delivery"].detected_turns), 0)

    def test_skips_malformed_history_items(self) -> None:
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            "not-json",
        )
        usage = usage_report.reconstruct_usage(self.database)
        self.assertTrue(all(not record.detected_turns for record in usage.values()))

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
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(
            [row["skill"] for row in payload["skills"]], ["reasoning-modes"]
        )
        self.assertEqual(payload["skills"][0]["explicit_requests"], 1)

    def test_rejects_an_unsupported_schema(self) -> None:
        unsupported = Path(self.temporary.name) / "unsupported.sqlite"
        with (
            contextlib.closing(sqlite3.connect(unsupported)) as connection,
            connection,
        ):
            connection.execute("CREATE TABLE something_else (value TEXT)")
        with self.assertRaises(usage_report.UsageReportError):
            usage_report.discover_database(unsupported)


if __name__ == "__main__":
    unittest.main()
