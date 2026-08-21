# Baseline validation

Date: 2026-08-20

## Corpus checks

- Ledger rows: 99 distinct content hashes across eight super-skills.
- Source text reconstruction: 99/99 hashes retrieved from the GitSkills `artifacts` Parquet table into a temporary directory outside this repository.
- Public source-text inclusion: none; only metadata, hashes, links, aggregate decisions, and newly written instructions are retained.
- Similarity check: 52 public skill, reference, and routing-metadata files compared with all 99 temporary source files using normalized eight-word shingles. No pair reached the 20% smaller-document containment threshold.

This automated comparison detects suspicious phrase-level overlap; it does not make a legal determination or replace human review.

## Structural checks

- `scripts/validate_repository.py`: passed.
- Official skill-creator `quick_validate.py`: passed for all eight skill directories.
- Python compilation: passed for all repository scripts.
- Git whitespace check: passed.

## Behavioral checks

The repository includes a shared rubric and category-specific positive, boundary, and non-trigger cases. These cases are authored evaluation specifications; they have not yet been run as a comparative model benchmark. A future release must distinguish rubric completeness from measured model performance.

## Expansion status

The metadata-only top-1,000 queue has been generated and committed:

- 1,000 distinct ranked content hashes are covered by the 99-row baseline ledger plus 901 expansion records.
- All 99 baseline hashes reproduce their recorded ranks exactly.
- The expansion records contain 900 eligible unreviewed candidates and the rank-24 non-skill placeholder excluded from the v0 baseline.
- Hashes are unique, ranks cover 1 through 1,000 exactly, and repository/occurrence counts satisfy the expected grain.
- The export query counts every artifact occurrence. `content_fetched` is an enrichment flag and is deliberately not used as a pre-aggregation filter.
- No third-party descriptions or source text are retained in the queue.

Classification, near-duplicate review, evidence-saturation decisions, and any changes to synthesis matrices, skills, or evals remain in progress. The top-100 baseline still defines current synthesized behavior.
