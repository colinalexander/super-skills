#!/usr/bin/env python3
"""Export a metadata-only review queue from the GitSkills Parquet dataset."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
PARQUET_INDEX = "https://huggingface.co/api/datasets/mvaccargiu/gitskills/parquet"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank distinct GitSkills hashes and export unreviewed metadata without source text."
    )
    parser.add_argument("--limit", type=int, default=1000, help="Overall rank cutoff (default: 1000)")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "research" / "expansion-queue.csv",
        help="Queue path (default: research/expansion-queue.csv)",
    )
    parser.add_argument(
        "--include-baseline",
        action="store_true",
        help="Include hashes already present in research/source-ledger.csv",
    )
    args = parser.parse_args()
    if args.limit < 100:
        parser.error("limit must be at least 100")

    with urllib.request.urlopen(PARQUET_INDEX) as response:
        artifact_urls = json.load(response)["artifacts"]["train"]

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")
    rows = connection.execute(
        """
        WITH grouped AS (
            SELECT
                file_sha,
                COUNT(DISTINCT repo_full_name) AS repositories,
                COUNT(*) AS occurrences,
                MAX(name) AS representative_name,
                MIN(repo_full_name || '/' || path) AS sample_location
            FROM read_parquet(?)
            WHERE content_fetched = 1 AND file_sha IS NOT NULL
            GROUP BY file_sha
        ), ranked AS (
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY repositories DESC, occurrences DESC, file_sha
                ) AS overall_rank,
                *
            FROM grouped
        )
        SELECT * FROM ranked WHERE overall_rank <= ? ORDER BY overall_rank
        """,
        [artifact_urls, args.limit],
    ).fetchall()

    baseline: set[str] = set()
    if not args.include_baseline:
        with (ROOT / "research" / "source-ledger.csv").open(newline="", encoding="utf-8") as handle:
            baseline = {row["file_sha"] for row in csv.DictReader(handle)}

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "overall_rank",
        "file_sha",
        "repositories",
        "occurrences",
        "representative_name",
        "sample_location",
        "proposed_super_skill",
        "review_status",
        "novel_contribution",
        "source_diversity_note",
    ]
    written = 0
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, file_sha, repositories, occurrences, name, location in rows:
            if file_sha in baseline:
                continue
            writer.writerow(
                {
                    "overall_rank": rank,
                    "file_sha": file_sha,
                    "repositories": repositories,
                    "occurrences": occurrences,
                    "representative_name": name or "",
                    "sample_location": location or "",
                    "proposed_super_skill": "",
                    "review_status": "unreviewed",
                    "novel_contribution": "",
                    "source_diversity_note": "",
                }
            )
            written += 1

    print(f"Wrote {written} metadata-only candidates to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
