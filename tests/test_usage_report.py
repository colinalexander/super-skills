from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock
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

    def test_scopes_activation_verbs_to_the_same_clause(self) -> None:
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {
                "phase": "commentary",
                "text": (
                    "I’m using software-delivery; interface-design is unnecessary."
                ),
            },
        )
        self.insert(
            "agentMessage",
            "thread-1",
            "turn-2",
            1_700_100_000_000,
            {
                "phase": "commentary",
                "text": "I’m using software-delivery and interface-design together.",
            },
        )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["software-delivery"].announced), 2)
        self.assertEqual(len(usage["interface-design"].announced), 1)

    def test_excludes_negated_and_extended_skill_announcements(self) -> None:
        messages = (
            "I won't use interface-design.",
            "Do not use interface-design.",
            "I am not currently using interface-design.",
            "I’m using interface-design-extra.",
        )
        for index, text in enumerate(messages):
            self.insert(
                "agentMessage",
                "thread-1",
                f"turn-{index}",
                1_700_000_000_000 + index,
                {"phase": "commentary", "text": text},
            )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertEqual(len(usage["interface-design"].announced), 0)

    def test_database_recency_includes_wal_activity(self) -> None:
        home = Path(self.temporary.name) / "codex-home"
        home.mkdir()
        newer_main = home / "thread_history_1.sqlite"
        active_wal = home / "thread_history_2.sqlite"
        newer_main.touch()
        active_wal.touch()
        wal = Path(f"{active_wal}-wal")
        wal.touch()
        os_times = {
            newer_main: (300, 300),
            active_wal: (100, 100),
            wal: (400, 400),
        }
        for path, times in os_times.items():
            path.touch()
            path.chmod(0o600)
            os.utime(path, times)

        with (
            mock.patch.object(usage_report, "codex_home", return_value=home),
            mock.patch.object(usage_report, "has_supported_schema", return_value=True),
        ):
            selected = usage_report.discover_database()

        self.assertEqual(selected, active_wal.resolve())

    def test_quiescent_wal_database_is_opened_without_sidecar_writes(self) -> None:
        database = Path(self.temporary.name) / "quiescent.sqlite"
        with contextlib.closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("CREATE TABLE example (value TEXT)")
        wal = Path(f"{database}-wal")
        shm = Path(f"{database}-shm")
        self.assertFalse(wal.exists())
        self.assertFalse(shm.exists())

        with usage_report.connect_read_only(database) as connection:
            self.assertEqual(
                connection.execute("SELECT count(*) FROM example").fetchone()[0], 0
            )

        self.assertFalse(wal.exists())
        self.assertFalse(shm.exists())

    def test_live_wal_database_includes_uncheckpointed_history(self) -> None:
        database = Path(self.temporary.name) / "live.sqlite"
        with contextlib.closing(sqlite3.connect(database)) as writer:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("PRAGMA wal_autocheckpoint=0")
            writer.execute("CREATE TABLE example (value TEXT)")
            writer.commit()
            writer.execute("INSERT INTO example VALUES ('current')")
            writer.commit()
            self.assertTrue(Path(f"{database}-wal").exists())

            with usage_report.connect_read_only(database) as reader:
                self.assertEqual(
                    reader.execute("SELECT value FROM example").fetchone()[0],
                    "current",
                )

    def test_read_only_wal_snapshot_without_shm_is_staged_safely(self) -> None:
        source = Path(self.temporary.name) / "source.sqlite"
        snapshot_directory = Path(self.temporary.name) / "snapshot"
        snapshot_directory.mkdir()
        snapshot = snapshot_directory / "history.sqlite"
        with contextlib.closing(sqlite3.connect(source)) as writer:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("PRAGMA wal_autocheckpoint=0")
            writer.execute("CREATE TABLE example (value TEXT)")
            writer.commit()
            writer.execute("INSERT INTO example VALUES ('from-wal')")
            writer.commit()
            shutil.copy2(source, snapshot)
            shutil.copy2(Path(f"{source}-wal"), Path(f"{snapshot}-wal"))

        snapshot.chmod(0o400)
        Path(f"{snapshot}-wal").chmod(0o400)
        snapshot_directory.chmod(0o500)
        try:
            with usage_report.connect_read_only(snapshot) as reader:
                self.assertEqual(
                    reader.execute("SELECT value FROM example").fetchone()[0],
                    "from-wal",
                )
            self.assertFalse(Path(f"{snapshot}-shm").exists())
        finally:
            snapshot_directory.chmod(0o700)

    def test_print_table_supports_an_empty_filtered_report(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            usage_report.print_table(self.database, [])

        self.assertIn("Experimental local Codex usage", output.getvalue())
        self.assertIn("Detected", output.getvalue())

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
