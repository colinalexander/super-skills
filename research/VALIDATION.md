# Baseline validation

Date: 2026-08-20

## Corpus checks

- Ledger rows: 130 distinct content hashes across 11 super-skills: 99 baseline hashes and 31 promoted expansion hashes.
- Source text reconstruction: 99/99 baseline hashes and all 900 eligible expansion hashes retrieved from GitSkills into temporary locations outside this repository.
- Public source-text inclusion: none; only metadata, hashes, links, aggregate decisions, and newly written instructions are retained.
- Similarity check: the original 52 public files passed against all 99 baseline sources; the expanded set of 73 public skill, reference, and routing-metadata files passed against all 900 expansion sources. No pair reached the 20% smaller-document containment threshold using normalized eight-word shingles.

This automated comparison detects suspicious phrase-level overlap; it does not make a legal determination or replace human review.

## Structural checks

- `scripts/validate_repository.py`: passed.
- Official skill-creator `quick_validate.py`: passed for all 11 skill directories.
- Python compilation: passed for all repository scripts.
- Git whitespace check: passed.

## Behavioral checks

The repository includes a shared rubric and category-specific positive, boundary, and non-trigger cases. These cases are authored evaluation specifications; they have not yet been run as a comparative model benchmark. A future release must distinguish rubric completeness from measured model performance.

## Expansion status

The metadata-only top-1,000 queue has been generated, triaged, and committed:

- 1,000 distinct ranked content hashes are covered by the 130-row evidence ledger (99 baseline plus 31 promoted expansion hashes) and 901 expansion records; promoted hashes intentionally appear in both provenance and queue views.
- All 99 baseline hashes reproduce their recorded ranks exactly.
- The expansion records contain 900 eligible candidates and the rank-24 non-skill placeholder excluded from the initial baseline.
- Triage yields 31 retained sources, 64 reviewed sources with no new contribution, 408 metadata-triaged records, and 397 manual-review records.
- Content similarity flags 205 records across 91 possible near-duplicate lineages; these flags are not authorship claims.
- Hashes are unique, ranks cover 1 through 1,000 exactly, and repository/occurrence counts satisfy the expected grain.
- The export query counts every artifact occurrence. `content_fetched` is an enrichment flag and is deliberately not used as a pre-aggregation filter.
- No third-party descriptions or source text are retained in the queue.

The 31 retained source reviews changed synthesis matrices, skills, or evals and
established three additional categories. Manual classification, remaining
lineage review, and evidence-saturation decisions continue for the rest of the
expansion.
