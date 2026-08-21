# Baseline validation

Date: 2026-08-20

## Corpus checks

- Ledger rows: 130 distinct content hashes across 11 super-skills: 99 baseline hashes and 31 promoted expansion hashes.
- Review-decision rows: 194 distinct substantively reviewed hashes: 130 retained and 64 not retained, with a nonempty hash-level reason and synthesis target for every row.
- Token counts: generated for every skill with `cl100k_base` under pinned `tiktoken==0.11.0`; README core/full figures match the generated record.
- Source text reconstruction: 99/99 baseline hashes and all 900 eligible expansion hashes retrieved from GitSkills into temporary locations outside this repository.
- Public source-text inclusion: none; only metadata, hashes, links, aggregate decisions, and newly written instructions are retained.
- Similarity check: the original 52 public files passed against all 99 baseline sources; the expanded set of 73 public skill, reference, and routing-metadata files passed against all 900 expansion sources. No pair reached the 20% smaller-document containment threshold using normalized eight-word shingles.

This automated comparison detects suspicious phrase-level overlap; it does not make a legal determination or replace human review.

## Structural checks

- `scripts/validate_repository.py`: passed.
- `scripts/update_token_counts.py --check`: passed under Python 3.12 with the pinned validation requirements.
- Official skill-creator `quick_validate.py`: passed for all 11 skill directories.
- Python compilation: passed for all repository scripts.
- Git whitespace check: passed.

## Behavioral checks

The repository includes 60 category cases, 12 global true negatives, a shared
rubric, and a preregistered four-arm benchmark protocol. The source-suite arm
installs all 130 retained sources and the super-suite arm installs all 11
super-skills; arm membership is not selected after seeing a task. Natural and
matched-token-budget comparisons are both required. These are authored
evaluation specifications; they have not yet been run as a comparative model
benchmark.

## Expansion status

The metadata-only top-1,000 queue has been generated, triaged, and committed:

- 1,000 distinct ranked content hashes are covered by the 130-row evidence ledger (99 baseline plus 31 promoted expansion hashes) and 901 expansion records; promoted hashes intentionally appear in both provenance and queue views.
- All 99 baseline hashes reproduce their recorded ranks exactly.
- The expansion records contain 900 eligible candidates and the rank-24 non-skill placeholder excluded from the initial baseline.
- Triage yields 31 retained sources, 64 reviewed sources with no new contribution, 408 metadata-triaged records, and 397 manual-review records.
- Content similarity flags 225 expansion records across 121 possible near-duplicate lineages after comparison with eligible baseline content; 41 lineages are anchored by a baseline hash. These flags are not authorship claims.
- Hashes are unique, ranks cover 1 through 1,000 exactly, and repository/occurrence counts satisfy the expected grain.
- The export query counts every artifact occurrence. `content_fetched` is an enrichment flag and is deliberately not used as a pre-aggregation filter.
- No third-party descriptions or source text are retained in the queue.

Review-fix reproduction checks also passed:

- a fresh default exporter run wrote 901 rows and matched every committed rank, hash, count, representative name, and sample location;
- all 999 eligible baseline-plus-expansion corpus records passed exact hash/rank reconciliation;
- an intentionally stale corpus rank was rejected before annotation; and
- all 145 reported pairwise lineage notes were confirmed as actual similarity edges at or above the configured threshold.

The 31 retained source reviews changed synthesis matrices, skills, or evals and
established three additional categories. Manual classification, remaining
lineage review, and preregistered no-new-information decisions continue for the rest of the
expansion.
