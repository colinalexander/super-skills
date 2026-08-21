# Baseline validation

Date: 2026-08-20

## Corpus checks

- Ledger rows: 130 distinct content hashes across 11 observed categories: 99 baseline hashes and 31 promoted expansion hashes. Eleven document-productivity hashes are preserved as withheld research evidence; 119 hashes support the 10-skill active suite.
- Review-decision rows: 194 distinct substantively reviewed hashes: 130 retained and 64 not retained, with a nonempty hash-level reason and synthesis target for every row.
- Token counts: generated for every active skill with `cl100k_base` under pinned `tiktoken==0.11.0`; README description/core/full figures match the generated record. Description counts measure the always-loaded front-matter value and total 580 tokens across the 10-skill suite. Applying the same tokenizer to the 119 active evidence descriptions reconstructed transiently from GitSkills produced 5,613 tokens; no source description text was committed.
- Source text reconstruction: 99/99 baseline hashes and all 900 eligible expansion hashes retrieved from GitSkills into temporary locations outside this repository.
- Public source-text inclusion: none; only metadata, hashes, links, aggregate decisions, and newly written instructions are retained.
- Baseline similarity check: the current 66 active skill, reference, and routing-metadata files pass against all 99 baseline sources. No pair reached the 20% smaller-document containment threshold using normalized eight-word shingles.

### Full expansion similarity gate

- Status: **passed before benchmark execution**.
- Source population: all 900 eligible expansion source files, reconstructed by exact Git blob hash from GitSkills; the rank-24 non-skill placeholder is excluded.
- Source-population checksum: `83204e8fe3947f4d8a0d01d3cf8d299c1c43efda50c6cc21af13af87ae3d0b00`.
- Public surface: all 66 files under the 10 active skill directories.
- Public-surface checksum: `de1b0eef5ee49404dccb7d3640e2ea652a663faa02bc07613707a40719cbeeb6`.
- Command: `.venv/bin/python scripts/check_similarity.py --sources /absolute/path/to/reconstructed-900-source-corpus`.
- Parameters: normalized eight-word shingles; 20% smaller-document containment threshold.
- Result: `Similarity check passed: 66 public files compared with 900 external files at 20% containment.`

The source-population checksum is SHA-256 over the sorted, newline-terminated
list of 900 content hashes. Because Git blob identifiers address exact source
bytes, it fixes the external comparison population without storing its prose.
The public-surface checksum is SHA-256 over each sorted repository-relative path
and its file SHA-256 digest. Repository validation recomputes both checksums; any
active skill edit invalidates this gate until the 900-source comparison is rerun
and the recorded public checksum is deliberately updated.

This automated comparison detects suspicious phrase-level overlap; it does not make a legal determination or replace human review.

## Occurrence and lineage audit

- The baseline contains 31,405 distinct repository–hash pairs across 9,222 repositories; 42,684 is the path-level artifact count and is not used as the coverage denominator.
- Repeated multi-hash collection signatures account for 10,690 pairs (34.04%), while repositories containing at least 10 baseline hashes account for 13,153 pairs (41.88%).
- Owner deduplication retains 30,100 owner–hash pairs (95.84% of repository–hash coverage).
- Twenty-one of 99 baseline hashes exactly match historical Anthropic `main`-branch blobs; two further hashes pass the shingle near-match threshold. Together they account for 34.1% of repository–hash coverage.
- Eleven of the 21 exact matches were frozen older versions at the collection cutoff. Exact and thresholded near matching provide a floor on broader lineage because edits can evade both tests. Only three origin-repository artifacts were retrieved, so origin absence cannot classify a copy as stale.
- Ten of 11 document-productivity evidence hashes are exact historical Anthropic blobs; eight belong to the source-available document set. The category is preserved as research but withheld from the installable suite and benchmark cases.

## Structural checks

- `scripts/validate_repository.py`: passed.
- `scripts/update_token_counts.py --check`: passed under Python 3.12 with the pinned validation requirements.
- Official skill-creator `quick_validate.py`: passed for all 10 active skill directories.
- Python compilation: passed for all repository scripts.
- Git whitespace check: passed.

## Behavioral checks

The repository includes 56 active-category cases, 36 global true negatives, a shared
rubric, and a preregistered four-arm benchmark protocol: 92 evaluation cases in
total. The source-suite arm installs all 119 active-category retained sources as a ceiling on
narrow-skill overhead rather than a typical deployment, and the super-suite arm
installs all 10 active super-skills; arm membership is not selected after seeing a
task. Natural and matched-token-budget comparisons are both required. Primary
quality scores use two blinded independent human graders with adjudication, and
the protocol defines quality, false-activation, and critical-side-effect
falsification gates. These are authored evaluation specifications; they have
not yet been run as a comparative model benchmark.

The 36 global negatives were re-audited after withholding document productivity.
Two residual document-only cases (`pdf-acronym` and `spreadsheet-definition`)
were replaced with near misses for the active systems/security and data/ML
boundaries. Repository validation prevents those withheld-category case IDs
from returning.

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
