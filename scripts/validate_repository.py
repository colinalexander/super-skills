#!/usr/bin/env python3
"""Validate the public structure and source-separation invariants."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "interface-design",
    "software-delivery",
    "agent-tooling-and-orchestration",
    "application-engineering",
    "game-development",
    "reasoning-modes",
    "systems-and-security",
    "marketing-and-growth",
    "connected-service-automation",
    "data-science-and-ml",
)
WITHHELD_CATEGORIES = ("document-productivity",)
EVIDENCE_CATEGORIES = SKILLS + WITHHELD_CATEGORIES
DISALLOWED_MARKERS = ("[TODO", "TODO:", "Add the task-specific guidance")
LEDGER_FIELDS = (
    "rank",
    "super_skill",
    "category",
    "skill_name",
    "file_sha",
    "repositories",
    "occurrences",
    "reference_repository",
    "reference_path",
    "reference_commit",
    "reference_url",
    "license_metadata",
    "provenance_status",
    "reuse_policy",
)
ANTHROPIC_DOCUMENT_EXACT_HASHES = {
    "f6a22ddf88fdc7e7b7603f4c9064cc51bd930ad9",
    "df5000e17ef60ecf400e65bfcd3c58ff88b604c3",
    "c5c881be9ebaa2bfcdd02f97de2ebd711ab78803",
    "d3e046a5ae107a6cb23cfb16c219837094ab35d3",
    "2951e559989765293b6fbf83942378a3c2d0cba6",
    "22db189c8b17d48f94f11fa0c45343441239ff40",
    "a5a69839ef4a161131d80b6daef10037a9686f4a",
    "b93b875fe11cf805bdfbbe5f0e7878a7562896ac",
    "56ea935b74f371bfeb4c7d3c19d5139df866e73b",
    "664663895bcd11b88a632301d830b313cbabb845",
}
RESTRICTED_DOCUMENT_HASHES = {
    "f6a22ddf88fdc7e7b7603f4c9064cc51bd930ad9",
    "df5000e17ef60ecf400e65bfcd3c58ff88b604c3",
    "c5c881be9ebaa2bfcdd02f97de2ebd711ab78803",
    "d3e046a5ae107a6cb23cfb16c219837094ab35d3",
    "2951e559989765293b6fbf83942378a3c2d0cba6",
    "22db189c8b17d48f94f11fa0c45343441239ff40",
    "b93b875fe11cf805bdfbbe5f0e7878a7562896ac",
    "664663895bcd11b88a632301d830b313cbabb845",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def benchmark_installed_name(rank: int, original_name: str) -> str:
    """Return the deterministic collision-free name used by benchmark Arm 3."""
    slug = re.sub(r"[^a-z0-9]+", "-", original_name.lower()).strip("-")
    slug = slug[:48].rstrip("-") or "skill"
    return f"gs-r{rank:04d}-{slug}"


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
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        rows = list(reader)
    if fields != LEDGER_FIELDS:
        fail(errors, f"source ledger fields differ: {fields}")
    if len(rows) != 130:
        fail(errors, f"source ledger contains {len(rows)} rows, expected 130")
    observed = {row["super_skill"] for row in rows}
    if observed != set(EVIDENCE_CATEGORIES):
        fail(errors, f"source ledger category set differs: {sorted(observed)}")
    active_rows = [row for row in rows if row["super_skill"] in SKILLS]
    withheld_rows = [row for row in rows if row["super_skill"] in WITHHELD_CATEGORIES]
    if len(active_rows) != 119 or len(withheld_rows) != 11:
        fail(
            errors,
            "source ledger must contain 119 active and 11 withheld evidence rows",
        )
    hashes = [row["file_sha"] for row in rows]
    if len(hashes) != len(set(hashes)):
        fail(errors, "source ledger contains duplicate content hashes")
    for number, row in enumerate(rows, start=2):
        if not row["reference_url"].startswith("https://"):
            fail(errors, f"source ledger row {number}: missing HTTPS reference URL")
        if row["reuse_policy"] != "ideas-only synthesis; no source prose, code, or assets copied":
            fail(errors, f"source ledger row {number}: unexpected reuse policy")
        if row["file_sha"] in ANTHROPIC_DOCUMENT_EXACT_HASHES:
            commit = row["reference_commit"]
            expected_prefix = f"https://github.com/anthropics/skills/blob/{commit}/"
            if (
                row["reference_repository"] != "anthropics/skills"
                or not commit
                or not row["reference_url"].startswith(expected_prefix)
                or not row["provenance_status"].startswith("upstream exact Git blob")
            ):
                fail(errors, f"source ledger row {number}: stale document lineage")
        if (
            row["file_sha"] in RESTRICTED_DOCUMENT_HASHES
            and row["license_metadata"]
            != "Anthropic file-level terms (source-available)"
        ):
            fail(errors, f"source ledger row {number}: stale document license terms")


def validate_review_decisions(errors: list[str]) -> None:
    decisions_path = ROOT / "research" / "review-decisions.csv"
    ledger_path = ROOT / "research" / "source-ledger.csv"
    queue_path = ROOT / "research" / "expansion-queue.csv"
    expected_fields = [
        "rank",
        "file_sha",
        "representative_name",
        "super_skill",
        "decision",
        "decision_code",
        "reason_detail",
        "covered_by",
        "duplicate_of_file_sha",
    ]
    if not decisions_path.is_file():
        fail(errors, "missing research/review-decisions.csv")
        return
    with decisions_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        decisions = list(reader)
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        ledger = list(csv.DictReader(handle))
    with queue_path.open(newline="", encoding="utf-8") as handle:
        queue = list(csv.DictReader(handle))

    if fields != expected_fields:
        fail(errors, f"review decision fields differ: {fields}")
    if len(decisions) != 194:
        fail(errors, f"review decisions contain {len(decisions)} rows, expected 194")
    hashes = [row["file_sha"] for row in decisions]
    if len(hashes) != len(set(hashes)):
        fail(errors, "review decisions contain duplicate hashes")

    retained = {row["file_sha"] for row in decisions if row["decision"] == "retained"}
    rejected = {
        row["file_sha"] for row in decisions if row["decision"] == "not-retained"
    }
    ledger_hashes = {row["file_sha"] for row in ledger}
    queue_rejected = {
        row["file_sha"]
        for row in queue
        if row["review_status"] == "reviewed-no-new-contribution"
    }
    if retained != ledger_hashes:
        fail(errors, "retained review decisions must match the evidence ledger")
    if rejected != queue_rejected:
        fail(errors, "not-retained review decisions must match the reviewed queue")

    all_frame_hashes = ledger_hashes | {row["file_sha"] for row in queue}
    allowed_codes = {
        "retained-synthesis-evidence",
        "not-retained-covered",
        "not-retained-context-specific",
        "not-retained-near-duplicate",
        "not-retained-product-specific",
        "not-retained-out-of-scope",
    }
    for number, row in enumerate(decisions, start=2):
        if row["decision_code"] not in allowed_codes:
            fail(errors, f"review decision row {number}: unknown decision code")
        if not row["reason_detail"].strip():
            fail(errors, f"review decision row {number}: missing reason_detail")
        if "::" not in row["covered_by"]:
            fail(errors, f"review decision row {number}: invalid covered_by")
            continue
        path_text, area = row["covered_by"].split("::", 1)
        target = ROOT / path_text
        if not target.is_file() or f"| {area} |" not in target.read_text(encoding="utf-8"):
            fail(errors, f"review decision row {number}: unresolved covered_by")
        duplicate = row["duplicate_of_file_sha"]
        if duplicate and (duplicate not in all_frame_hashes or duplicate == row["file_sha"]):
            fail(errors, f"review decision row {number}: invalid duplicate target")
        if row["decision_code"] == "not-retained-near-duplicate" and not duplicate:
            fail(errors, f"review decision row {number}: missing duplicate target")


def validate_token_counts(errors: list[str]) -> None:
    path = ROOT / "research" / "token-counts.csv"
    expected_fields = [
        "skill",
        "tokenizer",
        "tokenizer_package_version",
        "description_tokens",
        "core_tokens",
        "full_tokens",
        "reference_files",
    ]
    if not path.is_file():
        fail(errors, "missing research/token-counts.csv")
        return
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    if fields != expected_fields:
        fail(errors, f"token count fields differ: {fields}")
    if {row["skill"] for row in rows} != set(SKILLS):
        fail(errors, "token counts must cover every skill exactly once")
    if len(rows) != len(SKILLS):
        fail(errors, f"token counts contain {len(rows)} rows, expected {len(SKILLS)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    description_total = 0
    for number, row in enumerate(rows, start=2):
        description = int(row["description_tokens"])
        description_total += description
        core = int(row["core_tokens"])
        full = int(row["full_tokens"])
        references = int(row["reference_files"])
        if row["tokenizer"] != "cl100k_base" or row["tokenizer_package_version"] != "0.11.0":
            fail(errors, f"token count row {number}: tokenizer pin differs")
        if description < 1 or core < description or full < core or references < 1:
            fail(errors, f"token count row {number}: invalid counts")
        marker = f"| [`{row['skill']}`](skills/{row['skill']}/) |"
        if (
            marker not in readme
            or f"| {description:,} | {core:,} | {full:,} |" not in readme
        ):
            fail(errors, f"README token counts are stale for {row['skill']}")
    if f"total **{description_total:,} tokens**" not in readme:
        fail(errors, "README aggregate description-token count is stale")
    source_counts_path = ROOT / "research" / "source-description-token-counts.csv"
    source_fields = (
        "rank",
        "file_sha",
        "super_skill",
        "original_name",
        "installed_name",
        "tokenizer",
        "tokenizer_package_version",
        "description_tokens",
    )
    with source_counts_path.open(newline="", encoding="utf-8") as handle:
        source_reader = csv.DictReader(handle)
        observed_source_fields = tuple(source_reader.fieldnames or ())
        source_rows = list(source_reader)
    if observed_source_fields != source_fields:
        fail(errors, f"source token count fields differ: {observed_source_fields}")

    with (ROOT / "research" / "source-ledger.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        active_ledger_rows = {
            row["file_sha"]: row
            for row in csv.DictReader(handle)
            if row["super_skill"] in SKILLS
        }
    observed_source_hashes = {row["file_sha"] for row in source_rows}
    if len(source_rows) != 119 or observed_source_hashes != set(active_ledger_rows):
        fail(errors, "source token counts do not match the 119 active ledger hashes")
    installed_names = {row["installed_name"] for row in source_rows}
    if len(installed_names) != 119:
        fail(errors, "source token counts contain colliding benchmark names")

    source_total = 0
    for number, row in enumerate(source_rows, start=2):
        ledger_row = active_ledger_rows.get(row["file_sha"])
        if ledger_row is None:
            continue
        if (
            row["rank"] != ledger_row["rank"]
            or row["super_skill"] != ledger_row["super_skill"]
            or row["original_name"] != ledger_row["skill_name"]
            or row["installed_name"]
            != benchmark_installed_name(int(row["rank"]), row["original_name"])
            or row["tokenizer"] != "cl100k_base"
            or row["tokenizer_package_version"] != "0.11.0"
        ):
            fail(errors, f"source token count row {number}: ledger or tokenizer differs")
        count = int(row["description_tokens"])
        if count < 1:
            fail(errors, f"source token count row {number}: invalid count")
        source_total += count

    expected_ratio = source_total / description_total
    benchmark = (ROOT / "evals" / "BENCHMARK.md").read_text(encoding="utf-8")
    if (
        f"**{source_total:,} tokens**" not in readme
        or f"{expected_ratio:.1f}×" not in readme
    ):
        fail(errors, "README retained-source description-token comparison is missing")
    if f"{source_total:,} tokens for the externally reconstructed Arm 3" not in benchmark:
        fail(errors, "benchmark retained-source description-token count is stale")


def validate_evaluations(errors: list[str]) -> None:
    category_dir = ROOT / "evals" / "category-specific"
    evaluation_files = {path.stem for path in category_dir.glob("*.yaml")}
    if evaluation_files != set(SKILLS):
        fail(errors, f"category evaluation set differs: {sorted(evaluation_files)}")
    category_cases = sum(
        path.read_text(encoding="utf-8").count('  - id: "')
        for path in category_dir.glob("*.yaml")
    )
    if category_cases != 56:
        fail(errors, f"category evaluations contain {category_cases} cases, expected 56")

    negatives_path = ROOT / "evals" / "shared" / "true-negatives.yaml"
    if not negatives_path.is_file():
        fail(errors, "missing global true-negative evaluations")
    else:
        negatives = negatives_path.read_text(encoding="utf-8")
        if negatives.count('  - id: "') != 36:
            fail(errors, "global true-negative set must contain 36 cases")
        if negatives.count("    should_activate: false") != 36:
            fail(errors, "every global true negative must disable activation")
        if negatives.count('    forbidden_activations: "all"') != 36:
            fail(errors, "every global true negative must forbid all skills")
        for withheld_id in ('id: "pdf-acronym"', 'id: "spreadsheet-definition"'):
            if withheld_id in negatives:
                fail(errors, f"global true negatives retain withheld-category case {withheld_id!r}")
        for active_near_miss in (
            'id: "financial-security-definition"',
            'id: "athletic-training-definition"',
        ):
            if active_near_miss not in negatives:
                fail(errors, f"global true negatives are missing {active_near_miss!r}")

    benchmark_path = ROOT / "evals" / "BENCHMARK.md"
    if not benchmark_path.is_file():
        fail(errors, "missing evals/BENCHMARK.md")
    else:
        benchmark = benchmark_path.read_text(encoding="utf-8")
        for marker in (
            "**Unskilled:**",
            "**Highest-occurrence source:**",
            "**Source-suite ceiling:**",
            "**Super suite:**",
            "all 119 active-category retained exact-hash sources",
            "upper bound on narrow-skill overhead",
            "global true-negative",
            "fixed-budget sensitivity analysis",
            "two independent human",
            "three times per case",
            "10,000 stratified nonparametric bootstrap samples",
            "Generator(PCG64)",
            "Bonferroni-adjusted 99.8333%",
            "Wilson score intervals",
            "continuity correction",
            "correct activated-skill events",
            "arm-neutral evidence packet",
            "machine-checkable linkage",
            "gs-rRRRR-<slug>",
            "protocol-imposed compatibility transform",
            "complete, pinned file-dependency closure",
            "checksum over the sorted closure records",
            "same file classes as the generated Arm 4",
            "success conditions, not merely",
            "absolute false-activation threshold is **10%**",
            "absolute blocker regardless of comparator behavior",
            "Falsification criteria",
            "0.5 points",
            "all 999 eligible",
            "baseline-plus-expansion sources",
            "Before any benchmark execution",
        ):
            if marker not in benchmark:
                fail(errors, f"benchmark protocol is missing {marker!r}")

    conflict_path = (
        ROOT / "research" / "conflict-decisions" / "interface-aesthetic-profiles.md"
    )
    if not conflict_path.is_file():
        fail(errors, "missing worked interface conflict decision")
    else:
        conflict = conflict_path.read_text(encoding="utf-8")
        for marker in (
            "44ead27ef04ffe79ade0c6df7fd696dbcf7b246b",
            "f5375b908340e1376ed391232a31c5d82d5babfb",
            "Existing product authority",
            "Audience and task",
            "Why majority vote fails",
            "front-matter name",
        ):
            if marker not in conflict:
                fail(errors, f"worked interface conflict is missing {marker!r}")

    audit_path = ROOT / "research" / "CORPUS_AUDIT.md"
    if not audit_path.is_file():
        fail(errors, "missing research/CORPUS_AUDIT.md")
    else:
        audit = audit_path.read_text(encoding="utf-8")
        for marker in (
            "34.04%",
            "41.88%",
            "31,405",
            "11 were frozen",
            "Lineage family is the ranking unit",
            "withholds the installable skill",
        ):
            if marker not in audit:
                fail(errors, f"corpus audit is missing {marker!r}")


def validate_similarity_gate(errors: list[str]) -> None:
    ledger_path = ROOT / "research" / "source-ledger.csv"
    queue_path = ROOT / "research" / "expansion-queue.csv"
    validation_path = ROOT / "research" / "VALIDATION.md"
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        baseline_hashes = [
            row["file_sha"]
            for row in csv.DictReader(handle)
            if int(row["rank"]) <= 100
        ]
    with queue_path.open(newline="", encoding="utf-8") as handle:
        expansion_hashes = [
            row["file_sha"]
            for row in csv.DictReader(handle)
            if row["review_status"] != "excluded-non-skill-placeholder"
        ]
    source_hashes = sorted(baseline_hashes + expansion_hashes)
    if len(source_hashes) != 999 or len(source_hashes) != len(set(source_hashes)):
        fail(errors, "similarity-gate source population must contain 999 unique hashes")
        return
    source_checksum = hashlib.sha256(
        ("\n".join(source_hashes) + "\n").encode("utf-8")
    ).hexdigest()

    public_files = sorted(
        path
        for path in (ROOT / "skills").rglob("*")
        if path.is_file()
    )
    public_digest = hashlib.sha256()
    for path in public_files:
        public_digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        public_digest.update(b"\0")
        public_digest.update(hashlib.sha256(path.read_bytes()).digest())
        public_digest.update(b"\n")
    public_checksum = public_digest.hexdigest()

    validation = validation_path.read_text(encoding="utf-8")
    for marker in (
        "Status: **passed before benchmark execution**",
        f"Source-population checksum: `{source_checksum}`",
        f"Public surface: all {len(public_files)} files",
        f"Public-surface checksum: `{public_checksum}`",
        "--verify-gitskills-frame",
        "Source corpus verified: 999 files match the recorded Git blob set.",
        (
            "Similarity check passed: "
            f"{len(public_files)} public files compared with 999 external files "
            "at 20% containment."
        ),
    ):
        if marker not in validation:
            fail(errors, f"full-corpus similarity gate is stale or missing {marker!r}")


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
    hashes = {row["file_sha"] for row in combined}
    if len(hashes) != 1000:
        fail(errors, "source ledger and expansion queue must cover 1,000 unique hashes")

    ranks = {
        int(row.get("rank") or row.get("overall_rank") or 0) for row in combined
    }
    if ranks != set(range(1, 1001)):
        fail(errors, "source ledger and expansion queue must cover ranks 1 through 1,000")

    queue_hashes = {row["file_sha"] for row in queue_rows}
    queue_by_hash = {row["file_sha"]: row for row in queue_rows}
    expansion_evidence = [row for row in baseline_rows if int(row["rank"]) > 100]
    if len(expansion_evidence) != 31 or any(
        row["file_sha"] not in queue_hashes for row in expansion_evidence
    ):
        fail(errors, "source ledger must contain 31 promoted expansion hashes")
    for row in expansion_evidence:
        queue_row = queue_by_hash[row["file_sha"]]
        if queue_row["review_status"] != "reviewed-retained":
            fail(errors, f"promoted hash {row['file_sha']} is not reviewed-retained")
        if queue_row["proposed_super_skill"] != row["super_skill"]:
            fail(errors, f"promoted hash {row['file_sha']} has inconsistent skill routing")

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
        "metadata-triaged": 408,
        "manual-review": 397,
        "reviewed-retained": 31,
        "reviewed-no-new-contribution": 64,
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

    lineage_members = 0
    lineage_roots = 0
    for row in queue_rows:
        note = row["source_diversity_note"]
        if "near-duplicate" in note:
            lineage_members += 1
        if "lineage root" in note:
            lineage_roots += 1

    if (lineage_members, lineage_roots) != (225, 80):
        fail(
            errors,
            "expansion lineage counts differ: "
            f"{lineage_members} members across {lineage_roots} roots",
        )


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
            "groups the remaining 99 content hashes into eight initial "
            "synthesized capability categories"
        ),
        (
            "adds super-skill mappings, representative source URLs, "
            "upstream-verification status, repository-license metadata, and "
            "reuse-policy fields"
        ),
        "renames `repository_license_metadata` to `license_metadata`",
        "researched upstream file-level terms where lineage is verified",
        (
            "derives category counts, synthesis matrices, conflict decisions, "
            "evaluation specifications, and instruction token counts"
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
    validate_review_decisions(errors)
    validate_token_counts(errors)
    validate_evaluations(errors)
    validate_similarity_gate(errors)
    validate_licensing(errors)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Repository validation passed: 10 active skills, 119 active and 11 "
        "withheld evidence rows, 194 review decisions, 901 expansion records, "
        "and 92 eval cases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
