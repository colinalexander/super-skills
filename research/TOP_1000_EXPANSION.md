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
| Synthesized v0 baseline | 99 | Recorded in `source-ledger.csv` |
| New eligible candidates | 900 | Unreviewed metadata queue |
| Non-skill template placeholder | 1 | Excluded at rank 24 |
| **Total ranked hashes** | **1,000** | Complete rank coverage |

The underlying GitSkills mining runs span 9–20 July 2026. This repository retains only metadata and review decisions; third-party skill descriptions and source text are not committed.

## Profile

- Repository count ranges from 951 at rank 1 to 81 at rank 1,000.
- The 1,000 groups contain 181,576 artifact occurrences and 127,068 summed repository memberships.
- Representative metadata contains 834 distinct normalized names; three groups have no representative name.
- The cutoff intersects a tie: 37 groups have 81 repositories and occupy ranks 992–1,028. Occurrence count and then content hash determine which tied groups enter the top 1,000.

These statistics describe content-group reuse, not independent authorship, quality, or causal influence.

## Quality controls

The export must satisfy all of the following before the queue is accepted:

- every baseline hash appears at its recorded rank;
- the baseline and queue contain 1,000 unique hashes;
- combined ranks cover 1 through 1,000 exactly;
- repository and occurrence counts are positive, with occurrences greater than or equal to repository count;
- the known rank-24 placeholder remains explicitly excluded; and
- no source-text or description column is present.

An initial implementation incorrectly filtered to `content_fetched = 1` before aggregation. GitSkills uses that field to identify enriched rows, so the filter discarded most copies and produced a false hash-ordered ranking. The exporter now aggregates all non-null content hashes and fails if any of the 99 baseline ranks changes.

## Interpretation boundary

This expansion completes corpus selection, not synthesis. The 900 eligible additions remain `unreviewed` until they are:

1. classified into an existing super-skill or an explicit out-of-scope/new-category queue;
2. checked for near-duplicate lineages and source diversity;
3. reviewed for a material new principle, mode, constraint, conflict, safeguard, or evaluation case; and
4. incorporated only when they pass the inclusion and evidence-saturation rules in `METHODOLOGY.md`.

Until those stages are complete, the top-100 baseline remains the evidence base for the public skill instructions.
