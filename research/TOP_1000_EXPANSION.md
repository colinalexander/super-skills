# Top-1,000 expansion

Generated: 2026-08-20 (US/Pacific)

## Scope

The expansion ranks distinct GitSkills content hashes by:

1. repository count, descending;
2. occurrence count, descending; and
3. content hash, ascending, as a deterministic final tie-break.

The committed evidence set consists of:

| Record class | Count | Status |
| --- | ---: | --- |
| Synthesized initial baseline | 99 | Recorded in `source-ledger.csv` |
| New eligible candidates | 900 | Metadata triage complete; source review in progress |
| Non-skill template placeholder | 1 | Excluded at rank 24 |
| **Total ranked hashes** | **1,000** | Complete rank coverage |

The underlying GitSkills mining runs span 9–20 July 2026. This repository retains only metadata and review decisions; third-party skill descriptions and source text are not committed.

## Profile

- Repository count ranges from 951 at rank 1 to 81 at rank 1,000.
- The 1,000 groups contain 181,576 artifact occurrences and 127,068 summed repository memberships.
- Representative metadata contains 834 distinct normalized names; three groups have no representative name.
- The cutoff intersects a tie: 37 groups have 81 repositories and occupy ranks 992–1,028. Occurrence count and then content hash determine which tied groups enter the top 1,000.

These statistics describe content-group reuse, not independent authorship, quality, or causal influence.

## Metadata triage and lineage flags

The 900 eligible additions have completed a reproducible first-pass triage:

| Triage result | Count | Meaning |
| --- | ---: | --- |
| Retained after source review | 31 | Added a material decision rule, category boundary, or evaluation case |
| Reviewed without a new contribution | 64 | Existing synthesis already covered the material behavior |
| Existing-category proposal | 408 | One category had a clear metadata-rule lead |
| Manual category review | 397 | No rule matched strongly or multiple boundaries tied |

Substantive review of the former taxonomy queue established three additional
decision systems: `marketing-and-growth`, `connected-service-automation`, and
`data-science-and-ml`. Twenty-four representative hashes were retained for
those categories; 23 variants added no distinct proposition. One
`codebase-onboarding` record was corrected to application engineering rather
than being treated as marketing. The public suite therefore contains 11
categories.

Content-similarity triage also flagged 225 expansion records across 121 possible
near-duplicate lineages after comparison with the eligible baseline content.
Forty-one lineages are anchored by a baseline hash; the remaining 80 have an
expansion record as their earliest ranked member. This is deliberately a review
aid rather than a claim of common authorship: similar skill structures,
templates, or independently convergent instructions can produce high
similarity.

Run the triage against a transient reconstructed corpus with:

```bash
python3 scripts/triage_expansion.py \
  --corpus /absolute/path/to/review-corpus.parquet \
  --write
```

Descriptions and source text are read only from the external corpus and are
never written to the repository. The transient corpus contains the 99 eligible
baseline hashes plus the 900 eligible expansion hashes; rank 24 remains excluded
as a non-skill placeholder. Only expansion rows receive committed annotations.

The promoted evidence consists of three application-engineering, one
software-delivery, three agent-tooling, 14 marketing-and-growth, five
connected-service-automation, and five data-science-and-ML hashes. The source
ledger records provenance before retained propositions appear in public skills.

Application engineering and software delivery each reached the current
saturation threshold: after the last retained source in each ranked stream, 20
eligible, non-lineage-duplicate candidates added no material principle, mode,
constraint, conflict, safeguard, or evaluation case. This is a checkpoint for
this corpus ordering, not proof that specialist or lower-ranked evidence can
never change those skills.

## Quality controls

The export must satisfy all of the following before the queue is accepted:

- every baseline hash appears at its recorded rank;
- promoted expansion hashes remain in the regenerated queue rather than being mistaken for baseline exclusions;
- the baseline and queue contain 1,000 unique hashes;
- combined ranks cover 1 through 1,000 exactly;
- repository and occurrence counts are positive, with occurrences greater than or equal to repository count;
- the known rank-24 placeholder remains explicitly excluded; and
- no source-text or description column is present.

The triage command additionally rejects missing, unexpected, duplicated, or
rank-mismatched corpus hashes before applying any lineage annotation.

An initial implementation incorrectly filtered to `content_fetched = 1` before aggregation. GitSkills uses that field to identify enriched rows, so the filter discarded most copies and produced a false hash-ordered ranking. The exporter now aggregates all non-null content hashes and fails if any of the 99 baseline ranks changes.

## Interpretation boundary

This expansion completes corpus selection and metadata triage, not synthesis.
The 900 eligible additions are not synthesis evidence until they are:

1. classified into an existing super-skill or an explicit out-of-scope/new-category queue;
2. checked for near-duplicate lineages and source diversity;
3. reviewed for a material new principle, mode, constraint, conflict, safeguard, or evaluation case; and
4. incorporated only when they pass the inclusion and evidence-saturation rules in `METHODOLOGY.md`.

Only promoted ledger entries are evidence for public skill instructions. Queue
membership and metadata classification remain routing aids, not votes.
