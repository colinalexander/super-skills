#!/usr/bin/env python3
"""Triage the top-1,000 expansion without retaining third-party source text.

The input is the transient Parquet review corpus reconstructed from GitSkills.
Only derived category, review-status, and lineage metadata are written to the
committed expansion queue.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import duckdb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "research" / "expansion-queue.csv"


@dataclass(frozen=True)
class Rule:
    pattern: re.Pattern[str]
    weight: int = 1


def rules(*patterns: str) -> tuple[Rule, ...]:
    return tuple(Rule(re.compile(pattern, re.I)) for pattern in patterns)


CATEGORY_RULES = {
    "marketing-and-growth": rules(
        r"\bseo\b|schema markup|search engine",
        r"\bcro\b|conversion|signup flow|onboarding|paywall|funnel",
        r"marketing|advertis|ad creative|copywriting|growth hack",
        r"investor|fundrais|market research|competitive analysis|startup analyst",
        r"pricing strategy|product strateg|sales|lead generation|monetization",
    ),
    "data-science-and-ml": rules(
        r"fine[- ]?tun|pytorch|tensorflow|machine learning|deep learning",
        r"data scien|statistical|feature engineering|model training|mlops",
        r"hugging ?face|transformers|computer vision|nlp\b",
    ),
    "connected-service-automation": rules(
        r"\bautomation\b.*\b(?:asana|shopify|whatsapp|docusign|slack|notion|telegram)\b",
        r"\b(?:sonos|imessage|spotify|apple notes|feishu)\b",
        r"send and receive|control .* speakers",
    ),
    "interface-design": rules(
        r"\bui\b|\bux\b|user interface|user experience",
        r"frontend[- ]design|web design|design system|design taste",
        r"brand|visual design|creative direction|art direction",
        r"banner|logo|icon|image[- ]to[- ]code|imagegen|algorithmic art",
        r"tailwind|shadcn|css\b|typography|color palette|liquid glass",
        r"animation|motion design|view transition|human interface guidelines|\bhig\b",
    ),
    "software-delivery": rules(
        r"\btdd\b|test[- ]driven|\btesting\b|test harness|test coverage",
        r"debug|diagnos|root cause|bug fix|incident",
        r"code review|pull request|\bpr review\b|review checklist",
        r"\bgit\b|worktree|pre-commit|commit message|version control",
        r"ci[ /-]?cd|deployment|release|rollback|production readiness",
        r"verification|quality gate|lint|refactor|technical debt",
        r"writing plans|executing plans|task breakdown|issue triage",
        r"spec[- ]driven|openspec|change management",
    ),
    "agent-tooling-and-orchestration": rules(
        r"skill creator|skill development|writing skills|find skills|skill installer",
        r"\bagent(?:ic|s)?\b|subagent|multi[- ]agent|parallel agents|orchestrat",
        r"\bmcp\b|model context protocol|tool interface|tool definition",
        r"prompt engineering|prompt library|context engineering|context manager",
        r"llm eval|evaluating llm|agent harness|agent development",
        r"plugin development|plugin creator|hook development|command development",
        r"conversation memory|knowledge ops|\brag\b",
    ),
    "application-engineering": rules(
        r"architecture|domain model|backend|frontend patterns|full[- ]stack",
        r"\bapi\b|database|postgres|mysql|sqlite|schema design|query optim",
        r"react|next\.?js|vue|svelte|angular|django|fastapi|spring ?boot|laravel",
        r"swift|kotlin|golang|\bgo\b|rust|python|node\.?js|typescript|javascript|c\+\+|\.net\b",
        r"firebase|supabase|cloudflare|vercel|azure|aws\b|gcp\b",
        r"docker|container|serverless|distributed|queue|cache|authentication",
        r"sdk\b|blockchain|web3|browser extension|telegram bot|discord bot",
    ),
    "document-productivity": rules(
        r"\bpdf\b|\bdocx\b|\bpptx\b|\bxlsx\b|spreadsheet|presentation|slides",
        r"office productivity|document|bilingual|translation",
        r"obsidian|notebook|notes|knowledge base|markdown",
        r"article|editorial|workplace writing|internal comm|research documentation",
        r"diagram|mermaid|json canvas|infographic",
    ),
    "game-development": rules(
        r"\bgame(?:s|play|play)?\b|game design|game art|game audio",
        r"unity|unreal|godot|multiplayer|level design",
        r"\b2d\b|\b3d\b|\bvr\b|\bxr\b|augmented reality|virtual reality",
    ),
    "reasoning-modes": rules(
        r"brainstorm|ideation|idea refin|explore mode",
        r"grill|adversarial review|zoom[- ]out|caveman|compressed communication",
        r"teach the user|thinking partner|reasoning mode|behavioral mode",
        r"decision framework|decision making|assumption",
    ),
    "systems-and-security": rules(
        r"security|secure coding|hardening|vulnerab|\bowasp\b",
        r"penetration|\bpentest\b|red team|attack surface|exploit",
        r"shell|bash|powershell|linux|windows admin|system operations",
        r"network scanning|forensic|malware|credential|secrets management",
        r"path traversal|injection|xss|csrf|authentication flaw",
    ),
}


# Human review decisions are kept as derived propositions, never source prose.
# They make a regenerated queue preserve the auditable review state.
REVIEW_DECISIONS: dict[int, tuple[str, str, str]] = {
    101: (
        "application-engineering",
        "reviewed-retained",
        "architecture decision record: constraints, alternatives, rationale, and revisit signal",
    ),
    107: (
        "software-delivery",
        "reviewed-retained",
        "durable narrow guardrails for destructive developer operations",
    ),
    142: (
        "application-engineering",
        "reviewed-retained",
        "deployment-unit boundaries for configuration, privilege, health, and shutdown",
    ),
    148: (
        "application-engineering",
        "reviewed-retained",
        "domain language validated against scenarios and aligned with code contracts",
    ),
    193: (
        "agent-tooling-and-orchestration",
        "reviewed-retained",
        "observation contracts and recovery-aware action-space design",
    ),
    233: (
        "agent-tooling-and-orchestration",
        "reviewed-retained",
        "lifecycle, observability, rollout, and emergency controls for persistent agents",
    ),
    344: (
        "agent-tooling-and-orchestration",
        "reviewed-retained",
        "task-scoped context selection with explicit authority and freshness",
    ),
}

for reviewed_rank in (
    152,
    163,
    164,
    169,
    172,
    173,
    175,
    180,
    185,
    189,
    195,
    196,
    199,
    203,
    206,
    215,
    217,
    219,
    245,
    249,
):
    REVIEW_DECISIONS[reviewed_rank] = (
        "application-engineering",
        "reviewed-no-new-contribution",
        "covered by existing architecture, contract, persistence, runtime, or verification rules",
    )

for reviewed_rank in (
    110,
    111,
    116,
    127,
    129,
    146,
    149,
    151,
    157,
    158,
    162,
    167,
    176,
    183,
    187,
    188,
    192,
    197,
    202,
    205,
):
    REVIEW_DECISIONS[reviewed_rank] = (
        "software-delivery",
        "reviewed-no-new-contribution",
        "covered by existing planning, testing, debugging, review, deployment, or completion rules",
    )


NEW_CATEGORY_CONTRIBUTIONS = {
    102: ("marketing-and-growth", "cross-asset factual consistency for fundraising materials"),
    125: ("marketing-and-growth", "search discovery, technical quality, content utility, and measurement"),
    131: ("marketing-and-growth", "decision-led market research with sourced ranges and explicit uncertainty"),
    209: ("connected-service-automation", "recipient, channel, platform permission, and send-state verification"),
    255: ("marketing-and-growth", "verified relevance and consistent claims in investor outreach"),
    294: ("connected-service-automation", "record identity, search completeness, edit semantics, and recoverable deletion"),
    299: ("data-science-and-ml", "reproducible device-aware training and data-pipeline validation"),
    310: ("connected-service-automation", "account and device resolution before media state changes"),
    378: ("marketing-and-growth", "behavioral principles bounded by evidence, trust, and user welfare"),
    420: ("connected-service-automation", "stable resource targeting for cloud-file mutations"),
    423: ("marketing-and-growth", "value metrics, packaging, economics, evidence, and migration"),
    434: ("connected-service-automation", "least-privilege collaborator changes with access verification"),
    455: ("marketing-and-growth", "scaled search pages gated by unique value and reliable data"),
    456: ("data-science-and-ml", "statistical framing, experimental validity, and stakeholder decision context"),
    466: ("marketing-and-growth", "dated shared commercial context separating facts from assumptions"),
    502: ("marketing-and-growth", "message construction from audience, proof, objection, and one intended action"),
    570: ("marketing-and-growth", "conversion diagnosis across traffic, offer, trust, experience, and measurement"),
    648: ("marketing-and-growth", "interruptive conversion patterns bounded by timing, relevance, and respect"),
    735: ("data-science-and-ml", "perception evaluation across capture conditions, geometry, and deployment constraints"),
    874: ("marketing-and-growth", "signup friction decisions tied to commitment, consent, and downstream quality"),
    905: ("data-science-and-ml", "distributed training selected from measured memory and communication constraints"),
    929: ("marketing-and-growth", "activation defined by delivered value and validated against retention"),
    931: ("marketing-and-growth", "ad variants organized as testable message hypotheses"),
    980: ("data-science-and-ml", "fine-tuning method chosen from data, quality, resource, and serving tradeoffs"),
}

for reviewed_rank, (category, contribution) in NEW_CATEGORY_CONTRIBUTIONS.items():
    REVIEW_DECISIONS[reviewed_rank] = (
        category,
        "reviewed-retained",
        contribution,
    )

for reviewed_rank in (
    433,
    540,
    542,
    552,
    578,
    609,
    641,
    746,
    747,
    754,
    809,
    831,
    832,
    886,
    889,
    907,
    908,
    930,
    933,
    988,
    992,
    996,
):
    REVIEW_DECISIONS[reviewed_rank] = (
        "marketing-and-growth",
        "reviewed-no-new-contribution",
        "covered by retained market, positioning, acquisition, conversion, pricing, or fundraising rules",
    )

REVIEW_DECISIONS[497] = (
    "connected-service-automation",
    "reviewed-no-new-contribution",
    "covered by the retained record-management and safe-mutation rules",
)
REVIEW_DECISIONS[330] = (
    "application-engineering",
    "reviewed-no-new-contribution",
    "codebase orientation is not a marketing capability and adds no new application rule",
)


REVIEW_DECISION_HASHES = {
    101: "3e4f6ad3411d31cd53c90f3d7e1d6e266cd211f8",
    107: "d943c68219d0f47512f10c5018a11fd8358e9bb5",
    110: "ddb07e807888d9c89dbf17be6d35b9225aaee707",
    111: "f4a4f60e303ea5b603d0b26b31b4e09c660fbd91",
    116: "1933545d57be0275ef5cac60fff332f279020e9e",
    127: "395a77b5f7e33911092f7bc86e7d87c4ca70d189",
    129: "448ca3193b0cd68dba36f73160be66a890fd66c4",
    142: "c438c4ad53664664fbe607084fc3c12276e3ed7c",
    146: "fea12112db430034a2560872711e3f5d99795e10",
    148: "d0f7e1a5ccb06a7184056ff9af02b67bc77f9dda",
    149: "450e46bf290ae31459ae09c5af341a1380a103c4",
    151: "2dd66850b52d775265699fdf1810273169d37a67",
    152: "922aec09b9f3db1972e9925869863fa62424a0c8",
    157: "9b1f851aaad8761d463392a9895b0276623d4659",
    158: "f400de7c1937377fec7ff9bae3b0c072670f1e81",
    162: "bcccaf9e12dc61bbdf8ba7448b78373b7f7f2b5d",
    163: "5e75d2710119f8e92d797f87cedce0b42cefc63d",
    164: "f80be15621dac2b817368817128f505ceb55162d",
    167: "c8f790aac0fd8ae01f057f692d233eebe97ebbd7",
    169: "73c4b0fed029de63431a7fc328c714ff04ad8ed8",
    172: "bebd018cdcae1771eacdee30cfb96af3ad3bd936",
    173: "ec59113de529bc58ae07dedb65defc1394afa5b0",
    175: "8e5287102e5518504b7d44aecea59ca0794db16f",
    176: "d27bc5312cac823cc4b30d7d28eed9cd17b7a168",
    180: "85cb198652e603fe9cf707355a582ad398ae017a",
    183: "c1b2533f489ab7f8fd01225a0edfd709271c0a39",
    185: "c1000fae66ba993d2796a4881ce5708d5e9cc416",
    187: "578b7299cc38db90f176c4c956c2458f4b2dd04d",
    188: "3b20b610f72169d91386e70e2da73f56fb7f1c63",
    189: "1b4963f5dc12fdec7a9c11f68f9445c4b3a40269",
    192: "118456fcb10225c030769a4fee7815b9c536b0ce",
    193: "29cd83411d3a5daddf26944a2a8e9bbd4b3febcf",
    195: "04f5c13c5d3cb4d156f69a4d40692c422e940e9e",
    196: "dcecd8e3f356c73f340676cfcefb33539435e987",
    197: "239b2848489511de30d9e63b0bd183adc4b01347",
    199: "10c9522f819d7d37baf415d82a6fef8460cdcc00",
    202: "39417d3f67cdf427aac2709fe97d40e9b0f4f855",
    203: "80cc2b2b6165ed0de7592189605bd2c5affb0ce7",
    205: "7029916a5687f9679256ae634e3388c9ad1721d4",
    206: "d4f8d66235603ebacc0ccef2f25758c7d623c8b2",
    215: "6627ec6d9a09aa0a88c957e1c8a02a16283838f1",
    217: "083ce216fb7ea9c1126fdb1a688ce9cf6fdb4b70",
    219: "7b603dfa6b74b46a58468d4dbecf2bc753ab0270",
    233: "7576b5416502e93f3c5cf9d1009850d1c597ea94",
    245: "13a8961d94881f9d92323f51f11be4731dd475d9",
    249: "210d666118023f47746414b2ee027584370f9df9",
    344: "be991103fe2b13f7e5f6f5da9d3c6029ad30ac64",
    102: "e392706af5d1b6b7c03738526c1251f122873f1e",
    125: "682fea80b08a35552266feea7be97c6f6659e2dc",
    131: "12ffa034b4f40ccd989ab3a2413bae8c424d1c26",
    209: "82df6a6ecf8a81e9ff265fe2d70cabb44b0ebc6c",
    255: "4fc69f4c288f26a1c0aedc166789795671d2204b",
    294: "61e8cf76d9a4a8f8e6cad3d7458170cecb719242",
    299: "8b56d81529300eac854fafe1c5a663e0dd9d142b",
    310: "040da793fd869f9bd56803715c81648a9f5f0347",
    330: "a008205c12fab4c8ccb52226c9e529b925c5557a",
    378: "5b23873fb55490b805abbf4ae94817a53ed7580f",
    420: "6b46eec7c8798ef0083348a083d1883d3ed9cf4a",
    423: "3651310a1a7f4dfe16bdf4dc03e1dc9dd76a1bc0",
    433: "ecf0a1e56bd137b9e19da0e1e68071cf1733461a",
    434: "1ce5db8b86c52d53a2687a630e102e8355cfd101",
    455: "b3e150eb8418bff9081edc296ec1b5611cf8ffc7",
    456: "c61c186893eb0afda5d391a9d1ad70f6edad11b9",
    466: "4ba17e616350c0bb3e9dc3d25671a911b6da795e",
    497: "020f0d641df4074d69d6c31cf816afcd42d583c7",
    502: "cbf9adff01b55fd12511faea71da44b548b80c10",
    540: "dd3ed3c85d5329be335f4b34a9640f9914e36c6c",
    542: "f34860e42913a67adc65d3fc5b74cf996f524e69",
    552: "42bf746b426600c416c0a5969a043592ff14ba7b",
    570: "2bdffe5269a8b1a08e95d1a84825c3bf56c3adcf",
    578: "6979118584a6e46bd32318321c84d546b6350c09",
    609: "f00f7678ac70063822085da8823fdcfe986b1fa8",
    641: "5883b6527d2ef5a5a68ffa24301c2ddc3ad33883",
    648: "5dd86483d389b69d51c5c20171b665225b37a13d",
    735: "6d69f63f6dbaa57c525a1a32d1f37eb4412c8aa8",
    746: "ef3e782c46de14767d7a86d299e4980827ba5ee9",
    747: "715c5a20aa858e71a5b77a24a2606311278bd40a",
    754: "503b05bf8cb3707dad7a62a918c8932d8f6ee7e5",
    809: "e6eb588cac767a67570b36930d9c28ac5697e0ef",
    831: "b80991c92514a1ec4371c26f7b7f62cdbe4356e6",
    832: "15f1fd56ce8590dcaf1d3daecb7cee32ac827a69",
    874: "26615e089246c5cd619c03a71bad11cccb278764",
    886: "eddedb4c9ce5357c358cbdedb8af9faa48cea179",
    889: "630f11a8bd04abf9bc274ab71565bca599caca14",
    905: "9e16f446ff7601ba63cc898eca4eb47b12b663d2",
    907: "5ae86ff7e1aad7ccbae671f2707429505421924c",
    908: "5cb2c1030a5d02bd47d029b79ce3fd2fe2f43b10",
    929: "af71b61cc7e430b42eb797cc37c7edad005ef2ce",
    930: "e8544a7235687a58639bf6873aa372fe60a67611",
    931: "acf77e503d9f9c0efb535365894be3339547adfd",
    933: "1abb41607062b6d620c795a4522a9885ecb379a4",
    980: "6f920713034307123bd172b2828e2149bb0823b3",
    988: "0b2f338b9ca93e96255935a710582eba73a019da",
    992: "baeaae74515ad6d5b255bba6d6bb1c9f5c6860de",
    996: "4933f61bd31fe691e393e1758ac952ef55147e74",
}


def normalized(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def rule_score(text: str, category_rules: tuple[Rule, ...]) -> int:
    return sum(rule.weight for rule in category_rules if rule.pattern.search(text))


def classify(name: str, description: str) -> tuple[str, str, str]:
    # The representative name is usually the strongest routing signal.
    name_text = normalized(name).replace("-", " ")
    description_text = normalized(description)
    combined = f"{name_text} {description_text}"

    scores = {
        category: 3 * rule_score(name_text, category_rules)
        + rule_score(description_text, category_rules)
        for category, category_rules in CATEGORY_RULES.items()
    }
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best_category, best_score = ranked[0]
    runner_up_score = ranked[1][1]

    if best_score < 3 or best_score == runner_up_score:
        candidates = ",".join(
            category for category, score in ranked if score == best_score and score > 0
        )
        return candidates, "manual-review", f"ambiguous metadata score {best_score}"
    return best_category, "metadata-triaged", (
        f"metadata score {best_score}; margin {best_score - runner_up_score}"
    )


class UnionFind:
    def __init__(self, values: list[int]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[max(left_root, right_root)] = min(left_root, right_root)


def lineage_notes(records: list[dict[str, object]], threshold: float) -> dict[int, str]:
    ranks = [int(record["overall_rank"]) for record in records]
    contents = [normalized(str(record["content"])) for record in records]
    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(3, 5),
        min_df=2,
        max_features=300_000,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(contents)
    similarities = cosine_similarity(matrix, dense_output=False).tocoo()
    union_find = UnionFind(ranks)
    strongest: dict[tuple[int, int], float] = {}
    for left, right, similarity in zip(
        similarities.row, similarities.col, similarities.data, strict=True
    ):
        if left >= right or similarity < threshold:
            continue
        left_rank, right_rank = ranks[left], ranks[right]
        union_find.union(left_rank, right_rank)
        strongest[(left_rank, right_rank)] = float(similarity)

    groups: dict[int, list[int]] = defaultdict(list)
    for rank in ranks:
        groups[union_find.find(rank)].append(rank)

    notes: dict[int, str] = {}
    for members in groups.values():
        if len(members) < 2:
            continue
        root = min(members)
        for rank in sorted(members):
            if rank == root:
                notes[rank] = f"near-duplicate lineage root; {len(members)} top-1000 variants"
                continue
            similarity = max(
                (
                    value
                    for pair, value in strongest.items()
                    if rank in pair and root in pair
                ),
                default=threshold,
            )
            notes[rank] = f"near-duplicate of rank {root}; cosine >= {similarity:.3f}"
    return notes


def load_corpus(path: Path) -> list[dict[str, object]]:
    connection = duckdb.connect()
    rows = connection.execute(
        """
        SELECT overall_rank, file_sha, name, description, content
        FROM read_parquet(?)
        ORDER BY overall_rank
        """,
        [str(path)],
    ).fetchall()
    fields = ("overall_rank", "file_sha", "name", "description", "content")
    return [dict(zip(fields, row, strict=True)) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--lineage-threshold", type=float, default=0.85)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    records = load_corpus(args.corpus)
    if len(records) != 900:
        raise SystemExit(f"expected 900 expansion records, found {len(records)}")

    by_hash = {str(record["file_sha"]): record for record in records}
    notes = lineage_notes(records, args.lineage_threshold)

    with args.queue.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        queue_rows = list(reader)

    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    lineage_count = 0
    for row in queue_rows:
        if row["review_status"] == "excluded-non-skill-placeholder":
            continue
        record = by_hash.get(row["file_sha"])
        if record is None:
            raise SystemExit(f"queue hash missing from corpus: {row['file_sha']}")
        category, status, classification_note = classify(
            str(record["name"] or ""), str(record["description"] or "")
        )
        rank = int(row["overall_rank"])
        decision = REVIEW_DECISIONS.get(rank)
        if decision is not None:
            expected_hash = REVIEW_DECISION_HASHES[rank]
            if row["file_sha"] != expected_hash:
                raise SystemExit(
                    f"review decision rank {rank} expected {expected_hash}, "
                    f"found {row['file_sha']}"
                )
            category, status, contribution = decision
        else:
            contribution = ""
        row["proposed_super_skill"] = category
        row["review_status"] = status
        row["novel_contribution"] = contribution
        lineage_note = notes.get(rank)
        row["source_diversity_note"] = "; ".join(
            value for value in (classification_note, lineage_note) if value
        )
        status_counts[status] += 1
        category_counts[category] += 1
        lineage_count += int(lineage_note is not None)

    print("Statuses:")
    for label, count in sorted(status_counts.items()):
        print(f"  {label}: {count}")
    print("Proposed categories:")
    for label, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {label}: {count}")
    print(f"Near-duplicate lineage members: {lineage_count}")

    if args.write:
        with args.queue.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(queue_rows)
        print(f"Updated {args.queue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
