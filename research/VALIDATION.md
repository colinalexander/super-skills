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

The top-100 baseline establishes structure and initial behavior. The metadata-only top-1,000 queue and evidence-saturation review described in `METHODOLOGY.md` remain the next research phase.
