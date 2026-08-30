from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
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

    def test_preserves_activation_for_a_colon_introduced_skill_list(self) -> None:
        message = "I’m using these skills: software-delivery and interface-design."

        self.assertTrue(usage_report.announced_use(message, "software-delivery"))
        self.assertTrue(usage_report.announced_use(message, "interface-design"))
        self.assertFalse(
            usage_report.announced_use(
                "I’m using software-delivery: interface-design is unnecessary.",
                "interface-design",
            )
        )

    def test_excludes_negated_and_extended_skill_announcements(self) -> None:
        messages = (
            "I won't use interface-design.",
            "Do not use interface-design.",
            "I am not currently using interface-design.",
            "I’m using interface-design-extra.",
            "I’m using software-delivery and not interface-design.",
            "I’m using software-delivery rather than interface-design.",
            "I’m using software-delivery as opposed to interface-design.",
            "I’m proceeding without using interface-design.",
            "I’m proceeding except when applying interface-design.",
            "I never use interface-design.",
            "I am never using interface-design.",
            "I’ll avoid using interface-design.",
            "I stopped using interface-design.",
            "I’m using neither interface-design nor software-delivery.",
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

    def test_accepts_affirmative_not_only_announcement(self) -> None:
        self.assertTrue(
            usage_report.announced_use(
                "I’m not only using interface-design but also testing it.",
                "interface-design",
            )
        )
        self.assertTrue(
            usage_report.announced_use(
                "I’m using interface-design not only for layout but also accessibility.",
                "interface-design",
            )
        )

    def test_accepts_a_multiline_announced_skill_list(self) -> None:
        message = (
            "I’m using these skills:\n"
            "- software-delivery\n"
            "- interface-design"
        )

        self.assertTrue(usage_report.announced_use(message, "software-delivery"))
        self.assertTrue(usage_report.announced_use(message, "interface-design"))
        self.assertFalse(
            usage_report.announced_use(
                "I’m using these skills:\n- software-delivery\n- not interface-design",
                "interface-design",
            )
        )
        self.assertFalse(
            usage_report.announced_use(
                "I’m not using these skills:\n- software-delivery",
                "software-delivery",
            )
        )
        self.assertTrue(
            usage_report.announced_use(
                "I’m not only using these skills:\n- software-delivery",
                "software-delivery",
            )
        )

    def test_accepts_linked_skill_first_announcement(self) -> None:
        self.assertTrue(
            usage_report.announced_use(
                "software-delivery is the skill I am using for this change.",
                "software-delivery",
            )
        )

    def test_rejects_post_skill_exclusions(self) -> None:
        messages = (
            "I’m using software-delivery and interface-design is not needed.",
            "I’m using software-delivery because interface-design does not apply.",
        )

        for message in messages:
            self.assertFalse(usage_report.announced_use(message, "interface-design"))
        self.assertFalse(
            usage_report.announced_use(
                "software-delivery is the skill I am not using for this change.",
                "software-delivery",
            )
        )

    def test_database_recency_tolerates_a_disappearing_wal(self) -> None:
        database = Path(self.temporary.name) / "thread_history.sqlite"
        database.touch()
        wal = Path(f"{database}-wal")

        real_stat = Path.stat

        def disappearing_wal(path: Path, *args: object, **kwargs: object) -> os.stat_result:
            if path == wal:
                raise FileNotFoundError(path)
            return real_stat(path, *args, **kwargs)

        with mock.patch.object(Path, "stat", autospec=True, side_effect=disappearing_wal):
            activity = usage_report.database_activity_mtime(database)

        self.assertEqual(activity, database.stat().st_mtime)

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

    def test_database_discovery_ignores_a_candidate_rotated_before_sorting(self) -> None:
        home = Path(self.temporary.name) / "codex-home"
        home.mkdir()
        vanished = home / "thread_history_1.sqlite"
        survivor = home / "thread_history_2.sqlite"
        vanished.touch()
        survivor.touch()

        def activity(path: Path) -> float:
            if path == vanished:
                raise FileNotFoundError(path)
            return 100.0

        with (
            mock.patch.object(usage_report, "codex_home", return_value=home),
            mock.patch.object(
                usage_report, "database_activity_mtime", side_effect=activity
            ),
            mock.patch.object(usage_report, "has_supported_schema", return_value=True),
        ):
            selected = usage_report.discover_database()

        self.assertEqual(selected, survivor.resolve())

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

    def test_read_only_connection_rechecks_a_vanished_wal(self) -> None:
        database = Path(self.temporary.name) / "checkpointing.sqlite"
        with contextlib.closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("CREATE TABLE example (value TEXT)")
        wal = Path(f"{database}-wal")
        wal.touch()
        real_copy = shutil.copy2

        def checkpoint_during_copy(source: Path, destination: Path) -> Path:
            if Path(source).name == wal.name:
                wal.unlink()
                raise FileNotFoundError(wal)
            return real_copy(source, destination)

        with (
            mock.patch.object(
                usage_report.shutil, "copy2", side_effect=checkpoint_during_copy
            ),
            mock.patch.object(usage_report.time, "sleep") as sleep,
        ):
            with usage_report.connect_read_only(database) as reader:
                self.assertEqual(
                    reader.execute("SELECT count(*) FROM example").fetchone()[0], 0
                )

        self.assertFalse(wal.exists())
        self.assertFalse(Path(f"{database}-shm").exists())
        sleep.assert_called_once()

    def test_read_only_connection_rejects_a_changed_wal_generation(self) -> None:
        database = Path(self.temporary.name) / "restarted-wal.sqlite"
        with contextlib.closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("CREATE TABLE example (value TEXT)")
        wal = Path(f"{database}-wal")
        wal.touch()
        real_copy = shutil.copy2
        wal_copies = 0

        def restart_during_copy(source: Path, destination: Path) -> Path:
            nonlocal wal_copies
            result = real_copy(source, destination)
            if Path(source).name == wal.name:
                wal_copies += 1
                if wal_copies == 1:
                    current = database.stat()
                    os.utime(
                        database,
                        ns=(current.st_atime_ns, current.st_mtime_ns + 1_000_000),
                    )
                    wal.touch()
                else:
                    wal.unlink()
            return result

        with (
            mock.patch.object(
                usage_report.shutil, "copy2", side_effect=restart_during_copy
            ),
            mock.patch.object(usage_report.time, "sleep") as sleep,
        ):
            with usage_report.connect_read_only(database) as reader:
                self.assertEqual(
                    reader.execute("SELECT count(*) FROM example").fetchone()[0], 0
                )

        self.assertEqual(wal_copies, 2)
        self.assertFalse(wal.exists())
        self.assertEqual(sleep.call_count, 2)

    def test_snapshot_retries_isolate_obsolete_sidecars(self) -> None:
        database = Path(self.temporary.name) / "changing-mode.sqlite"
        wal = Path(f"{database}-wal")
        journal = Path(f"{database}-journal")
        database.write_bytes(b"database")
        wal.write_bytes(b"old-wal")
        journal.write_bytes(b"current-journal")
        destination = Path(self.temporary.name) / "snapshots"
        destination.mkdir()
        generations = [
            (database, wal),
            (database, journal),
            (database, journal),
            (database, journal),
        ]

        with (
            mock.patch.object(
                usage_report, "snapshot_sources", side_effect=generations
            ),
            mock.patch.object(usage_report.time, "sleep") as sleep,
        ):
            snapshot, sidecars = usage_report.stage_consistent_snapshot(
                database, destination
            )

        self.assertEqual(sidecars, {"-journal"})
        self.assertTrue(Path(f"{snapshot}-journal").is_file())
        self.assertFalse(Path(f"{snapshot}-wal").exists())
        self.assertTrue(Path(f"{destination / 'attempt-0' / database.name}-wal").is_file())
        sleep.assert_called_once()

    def test_hot_rollback_journal_is_recovered_only_in_private_snapshot(self) -> None:
        database = Path(self.temporary.name) / "hot-journal.sqlite"
        with contextlib.closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("CREATE TABLE example (value BLOB)")
            connection.execute("INSERT INTO example VALUES ('committed')")

        subprocess.run(
            [
                sys.executable,
                "-c",
                """
import os
import sqlite3
import sys

connection = sqlite3.connect(sys.argv[1])
connection.execute("PRAGMA journal_mode=DELETE")
connection.execute("PRAGMA cache_size=5")
connection.execute("BEGIN IMMEDIATE")
for _ in range(100):
    connection.execute("INSERT INTO example VALUES (?)", (b"x" * 8192,))
os._exit(0)
""",
                str(database),
            ],
            check=True,
        )
        journal = Path(f"{database}-journal")
        self.assertTrue(journal.is_file())
        database.chmod(0o444)
        journal.chmod(0o444)

        with usage_report.connect_read_only(database) as reader:
            values = [
                row[0] for row in reader.execute("SELECT value FROM example").fetchall()
            ]

        self.assertEqual(values, ["committed"])
        self.assertTrue(journal.is_file())
        self.assertEqual(database.stat().st_mode & 0o222, 0)
        self.assertEqual(journal.stat().st_mode & 0o222, 0)

    def test_print_table_supports_an_empty_filtered_report(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            usage_report.print_table(self.database, [])

        self.assertIn("Experimental local Codex desktop usage", output.getvalue())
        self.assertIn("Detected", output.getvalue())

    def test_print_table_sizes_columns_from_rendered_values(self) -> None:
        rows = [
            {
                "skill": "interface-design",
                "detected_turns": 1,
                "explicit_requests": 0,
                "inferred_implicit_turns": 1,
                "first_detected": "2026-08-30",
                "last_detected": "2026-08-30",
            }
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            usage_report.print_table(self.database, rows)

        lines = output.getvalue().splitlines()
        header = next(line for line in lines if line.startswith("Skill"))
        value = next(line for line in lines if line.startswith("interface-design"))
        self.assertEqual(header.index("First"), value.index("2026-08-30"))
        self.assertEqual(header.index("Last"), value.rindex("2026-08-30"))

    def test_default_discovery_explains_desktop_only_scope(self) -> None:
        home = Path(self.temporary.name) / "cli-only-home"
        home.mkdir()
        (home / "state_5.sqlite").touch()
        (home / "sessions").mkdir()

        with mock.patch.object(usage_report, "codex_home", return_value=home):
            with self.assertRaisesRegex(
                usage_report.UsageReportError,
                "Codex desktop.*Codex CLI session history is not currently supported",
            ):
                usage_report.discover_database()

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

    def test_skips_history_items_with_malformed_timestamps(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $reasoning-modes."}]},
        )
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "UPDATE thread_items SET created_at_ms = 'not-a-timestamp'"
            )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertTrue(all(not record.detected_turns for record in usage.values()))

    def test_skips_history_items_with_out_of_range_timestamps(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $reasoning-modes."}]},
        )
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "UPDATE thread_items SET created_at_ms = 9223372036854775807"
            )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertTrue(all(not record.detected_turns for record in usage.values()))

    def test_skips_history_items_without_usable_turn_identifiers(self) -> None:
        nullable = Path(self.temporary.name) / "nullable-identifiers.sqlite"
        with contextlib.closing(sqlite3.connect(nullable)) as connection, connection:
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
            payload = json.dumps(
                {"content": [{"type": "text", "text": "Use $reasoning-modes."}]}
            )
            connection.executemany(
                "INSERT INTO thread_items VALUES (?, ?, ?, ?, ?, ?)",
                (
                    (None, "turn-1", 1_700_000_000_000, 0, payload, "userMessage"),
                    ("thread-1", None, 1_700_000_000_001, 0, payload, "userMessage"),
                    ("", "turn-2", 1_700_000_000_002, 0, payload, "userMessage"),
                    ("thread-2", " ", 1_700_000_000_003, 0, payload, "userMessage"),
                ),
            )

        usage = usage_report.reconstruct_usage(nullable)

        self.assertTrue(all(not record.detected_turns for record in usage.values()))

    def test_skips_item_json_with_invalid_text_encoding(self) -> None:
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            {"content": [{"type": "text", "text": "Use $reasoning-modes."}]},
        )
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "UPDATE thread_items SET item_json = ?",
                (sqlite3.Binary(b"\xff"),),
            )

        usage = usage_report.reconstruct_usage(self.database)

        self.assertTrue(all(not record.detected_turns for record in usage.values()))

    def test_skips_item_json_that_exceeds_the_decoder_recursion_limit(self) -> None:
        nested_json = "[" * 10_000 + "0" + "]" * 10_000
        self.insert(
            "userMessage",
            "thread-1",
            "turn-1",
            1_700_000_000_000,
            nested_json,
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
