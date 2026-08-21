#!/usr/bin/env python3
"""Validate the public structure and source-separation invariants."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "interface-design",
    "software-delivery",
    "agent-tooling-and-orchestration",
    "application-engineering",
    "document-productivity",
    "game-development",
    "reasoning-modes",
    "systems-and-security",
)
DISALLOWED_MARKERS = ("[TODO", "TODO:", "Add the task-specific guidance")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(errors, f"{path}: missing YAML frontmatter")
        return {}
    try:
        block = text.split("---\n", 2)[1]
    except IndexError:
        fail(errors, f"{path}: unterminated YAML frontmatter")
        return {}
    result: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(errors, f"{path}: malformed frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def validate_skill(skill: str, errors: list[str]) -> None:
    directory = ROOT / "skills" / skill
    entry = directory / "SKILL.md"
    metadata = directory / "agents" / "openai.yaml"
    references = directory / "references"
    for required in (entry, metadata, references):
        if not required.exists():
            fail(errors, f"missing {required.relative_to(ROOT)}")
            return

    fields = parse_frontmatter(entry, errors)
    if fields.get("name") != skill:
        fail(errors, f"{entry}: name must be {skill!r}")
    if not fields.get("description") or "Use " not in fields["description"]:
        fail(errors, f"{entry}: description must say when to use the skill")
    if set(fields) != {"name", "description"}:
        fail(errors, f"{entry}: only name and description are allowed in frontmatter")

    entry_text = entry.read_text(encoding="utf-8")
    for marker in DISALLOWED_MARKERS:
        if marker in entry_text:
            fail(errors, f"{entry}: contains scaffold marker {marker!r}")
    for link in re.findall(r"\]\((references/[^)]+)\)", entry_text):
        if not (directory / link).is_file():
            fail(errors, f"{entry}: broken reference link {link}")

    yaml_text = metadata.read_text(encoding="utf-8")
    if f"$${skill}" in yaml_text:
        fail(errors, f"{metadata}: default prompt has an escaped skill name")
    if f"${skill}" not in yaml_text:
        fail(errors, f"{metadata}: default_prompt must mention ${skill}")
    if "allow_implicit_invocation: true" not in yaml_text:
        fail(errors, f"{metadata}: implicit invocation policy is missing")
    short_match = re.search(r'^\s*short_description:\s*"([^"]+)"', yaml_text, re.M)
    if not short_match or not 25 <= len(short_match.group(1)) <= 64:
        fail(errors, f"{metadata}: short_description must be 25-64 characters")

    reference_files = sorted(references.glob("*.md"))
    if not reference_files:
        fail(errors, f"{references}: must contain focused reference files")
    for path in reference_files:
        text = path.read_text(encoding="utf-8")
        for marker in DISALLOWED_MARKERS:
            if marker in text:
                fail(errors, f"{path}: contains scaffold marker {marker!r}")


def validate_ledger(errors: list[str]) -> None:
    ledger = ROOT / "research" / "source-ledger.csv"
    with ledger.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 99:
        fail(errors, f"source ledger contains {len(rows)} rows, expected 99")
    observed = {row["super_skill"] for row in rows}
    if observed != set(SKILLS):
        fail(errors, f"source ledger skill set differs: {sorted(observed)}")
    hashes = [row["file_sha"] for row in rows]
    if len(hashes) != len(set(hashes)):
        fail(errors, "source ledger contains duplicate content hashes")
    for number, row in enumerate(rows, start=2):
        if not row["reference_url"].startswith("https://"):
            fail(errors, f"source ledger row {number}: missing HTTPS reference URL")
        if row["reuse_policy"] != "ideas-only synthesis; no source prose, code, or assets copied":
            fail(errors, f"source ledger row {number}: unexpected reuse policy")


def validate_expansion_queue(errors: list[str]) -> None:
    ledger = ROOT / "research" / "source-ledger.csv"
    queue = ROOT / "research" / "expansion-queue.csv"
    if not queue.is_file():
        fail(errors, "missing research/expansion-queue.csv")
        return

    with ledger.open(newline="", encoding="utf-8") as handle:
        baseline_rows = list(csv.DictReader(handle))
    with queue.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        queue_fields = reader.fieldnames or []
        queue_rows = list(reader)

    expected_fields = [
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
    if queue_fields != expected_fields:
        fail(errors, f"expansion queue fields differ: {queue_fields}")
    if len(queue_rows) != 901:
        fail(errors, f"expansion queue contains {len(queue_rows)} rows, expected 901")

    combined = baseline_rows + queue_rows
    hashes = [row["file_sha"] for row in combined]
    if len(hashes) != 1000 or len(set(hashes)) != 1000:
        fail(errors, "baseline and expansion queue must contain 1,000 unique hashes")

    ranks = [int(row.get("rank") or row.get("overall_rank") or 0) for row in combined]
    if set(ranks) != set(range(1, 1001)):
        fail(errors, "baseline and expansion queue must cover ranks 1 through 1,000")

    status_counts: dict[str, int] = {}
    for number, row in enumerate(queue_rows, start=2):
        status = row["review_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if not re.fullmatch(r"[0-9a-f]{40}", row["file_sha"]):
            fail(errors, f"expansion queue row {number}: invalid file_sha")
        repositories = int(row["repositories"])
        occurrences = int(row["occurrences"])
        if repositories < 1 or occurrences < repositories:
            fail(errors, f"expansion queue row {number}: invalid occurrence counts")
        if not row["sample_location"]:
            fail(errors, f"expansion queue row {number}: missing sample location")

    expected_statuses = {
        "unreviewed": 900,
        "excluded-non-skill-placeholder": 1,
    }
    if status_counts != expected_statuses:
        fail(errors, f"expansion queue status counts differ: {status_counts}")

    excluded = [
        row
        for row in queue_rows
        if row["review_status"] == "excluded-non-skill-placeholder"
    ]
    if not excluded or excluded[0]["overall_rank"] != "24":
        fail(errors, "rank 24 must remain the excluded non-skill placeholder")


def validate_licensing(errors: list[str]) -> None:
    root_license = ROOT / "LICENSE"
    research_license = ROOT / "research" / "LICENSE"
    attribution = ROOT / "research" / "ATTRIBUTION.md"
    for required in (root_license, research_license, attribution):
        if not required.is_file():
            fail(errors, f"missing {required.relative_to(ROOT)}")
            return

    if "Apache License" not in root_license.read_text(encoding="utf-8"):
        fail(errors, "root LICENSE must contain Apache-2.0 terms")
    if "CC-BY-4.0" not in research_license.read_text(encoding="utf-8"):
        fail(errors, "research/LICENSE must identify CC-BY-4.0")

    attribution_text = attribution.read_text(encoding="utf-8")
    required_attribution = (
        "GitSkills: A Dataset of Agent Skills on GitHub",
        "Giuseppe Destefanis",
        "Daniel Graziotin",
        "Matteo Vaccargiu",
        "Marco Ortu",
        "https://huggingface.co/datasets/mvaccargiu/gitskills",
        "https://doi.org/10.5281/zenodo.21875637",
        "## Modifications",
        "selects the ranked top-100 baseline and excludes one non-skill placeholder",
        (
            "groups the remaining 99 content hashes into eight synthesized "
            "capability categories"
        ),
        (
            "adds super-skill mappings, representative source URLs, "
            "upstream-verification status, repository-license metadata, and "
            "reuse-policy fields"
        ),
        (
            "derives category counts, synthesis matrices, conflict decisions, "
            "and evaluation specifications"
        ),
        (
            "reformats selected metadata into repository-specific CSV and "
            "Markdown artifacts"
        ),
    )
    for marker in required_attribution:
        if marker not in attribution_text:
            fail(errors, f"research/ATTRIBUTION.md is missing {marker!r}")


def validate_suite(errors: list[str]) -> None:
    skill_dirs = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    if skill_dirs != set(SKILLS):
        fail(errors, f"skills directory differs: {sorted(skill_dirs)}")
    for skill in SKILLS:
        validate_skill(skill, errors)
        matrix = ROOT / "research" / "synthesis-matrices" / f"{skill}.md"
        evaluation = ROOT / "evals" / "category-specific" / f"{skill}.yaml"
        if not matrix.is_file():
            fail(errors, f"missing {matrix.relative_to(ROOT)}")
        if not evaluation.is_file():
            fail(errors, f"missing {evaluation.relative_to(ROOT)}")

    all_skill_files = list(ROOT.rglob("SKILL.md"))
    allowed = {(ROOT / "skills" / skill / "SKILL.md").resolve() for skill in SKILLS}
    unexpected = [path for path in all_skill_files if path.resolve() not in allowed]
    if unexpected:
        fail(errors, "unexpected SKILL.md files: " + ", ".join(str(p) for p in unexpected))

def main() -> int:
    errors: list[str] = []
    validate_suite(errors)
    validate_ledger(errors)
    validate_expansion_queue(errors)
    validate_licensing(errors)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Repository validation passed: 8 skills, 99 baseline rows, "
        "901 expansion records, complete matrices and evals."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
