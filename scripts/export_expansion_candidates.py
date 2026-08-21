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
EXCLUDED_HASHES = {
    "50a4f9b104357d96361e257adb70454604cd15c0": "excluded-non-skill-placeholder",
}


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
    connection.execute("SET http_retries = 10")
    connection.execute("SET http_retry_wait_ms = 1000")
    connection.execute("SET http_retry_backoff = 2")
    connection.execute("SET http_timeout = 60")
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
            WHERE file_sha IS NOT NULL
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

    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        baseline_rows = list(csv.DictReader(handle))
    baseline_ranks = {row["file_sha"]: int(row["rank"]) for row in baseline_rows}
    ranked_hashes = {file_sha: rank for rank, file_sha, *_ in rows}

    missing_baseline = sorted(set(baseline_ranks) - set(ranked_hashes))
    if missing_baseline:
        raise RuntimeError(
            f"{len(missing_baseline)} baseline hashes are absent from the top {args.limit}; "
            "ranking semantics may have changed"
        )

    rank_mismatches = sorted(
        (file_sha, expected, ranked_hashes[file_sha])
        for file_sha, expected in baseline_ranks.items()
        if ranked_hashes[file_sha] != expected
    )
    if rank_mismatches:
        preview = ", ".join(
            f"{file_sha}: expected {expected}, got {actual}"
            for file_sha, expected, actual in rank_mismatches[:5]
        )
        raise RuntimeError(
            f"{len(rank_mismatches)} baseline ranks differ from the source ledger "
            f"({preview})"
        )

    baseline = set() if args.include_baseline else set(baseline_ranks)

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
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for rank, file_sha, repositories, occurrences, name, location in rows:
            if file_sha in baseline:
                continue
            review_status = EXCLUDED_HASHES.get(file_sha, "unreviewed")
            writer.writerow(
                {
                    "overall_rank": rank,
                    "file_sha": file_sha,
                    "repositories": repositories,
                    "occurrences": occurrences,
                    "representative_name": name or "",
                    "sample_location": location or "",
                    "proposed_super_skill": "",
                    "review_status": review_status,
                    "novel_contribution": "",
                    "source_diversity_note": (
                        "excluded in the v0 baseline as a non-skill template placeholder"
                        if file_sha in EXCLUDED_HASHES
                        else ""
                    ),
                }
            )
            written += 1

    print(
        f"Verified {len(baseline_ranks)} baseline ranks and wrote {written} "
        f"metadata-only candidates to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
