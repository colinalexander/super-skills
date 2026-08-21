# Synthesis methodology

## Objective

Produce one coherent, high-utility skill per category from a body of public skill evidence. The unit of work is a decision rule or operating principle, not a passage of source text.

## Baseline corpus

The initial baseline uses the top 100 GitSkills content groups ranked by repository count. One placeholder row was excluded, leaving 99 content hashes across eight initial categories. Identical hashes are exact byte matches; repeated names may still represent different versions.

The source ledger records both verified upstream locations and representative observed copies. “Observed copy” must not be read as an authorship claim.

## Evidence expansion

Popularity is useful for discovering common conventions but produces visibility, age, ecosystem, and copying biases. Expansion therefore uses the following sequence:

The top-1,000 ranking, metadata-only queue, provisional category triage, and
near-duplicate flags are complete. Metadata classification is only a routing
aid. Substantive review, no-new-information decisions, and any resulting
changes to skills or evals remain separate stages; queue membership and a
proposed category alone are not synthesis evidence.

Thirty-one expansion hashes have passed substantive review and been promoted to
the source ledger. Sixty-four additional sources were reviewed without adding a
material proposition. The review established `marketing-and-growth`,
`connected-service-automation`, and `data-science-and-ml` as distinct decision
systems, bringing the suite to 11 categories. Application engineering and
software delivery have each reached a recorded 20-source no-new-information
checkpoint under the targeted ordering. Those checkpoints describe review
history; they are not estimates of population saturation.

The resulting coverage accounting is:

| Measure | Count |
| --- | ---: |
| Ranked sampling frame | 1,000 |
| Eligible hashes | 999 |
| Substantively reviewed | 194 |
| Retained as synthesis evidence | 130 |
| Metadata/lineage triage only | 805 |

The expansion review was targeted using metadata, category gaps, and likely
distinctiveness. Its 31 retained hashes out of 900 expansion candidates are a
3.4% **frame yield**, while 31 retained out of 95 substantively reviewed hashes
are a 32.6% **review retention rate**. Neither estimates the residual information
rate of the 805 unreviewed hashes. Under targeted selection, a rising, flat, or
falling retention trajectory is confounded with changing targeting accuracy;
no trajectory from this design can establish saturation.

1. Pull the top 1,000 distinct content hashes by repository count.
2. Classify them into an existing category or an explicit taxonomy-review queue.
3. Collapse exact copies and flag near-duplicates before substantive review.
4. Within each category, prioritize distinct authors, ecosystems, task types, and minority approaches.
5. Review lower-ranked specialist sources when the high-ranked set leaves an identified coverage gap.
6. Treat 20 consecutive eligible, lineage-independent candidates with no new information as a review checkpoint, not a population-saturation claim.

Record exclusions and the reason for them. Population-level claims and future
ordered review are governed by the preregistered definitions, random probe, and
family-rerank requirements in `SAMPLING_PLAN.md`.

`scripts/export_expansion_candidates.py` creates the metadata-only review queue. Raw text used during review must remain in a separate, uncommitted research location.

`scripts/triage_expansion.py` uses representative names and descriptions to
propose categories, then uses content n-gram similarity to flag possible
lineages across both the eligible baseline and expansion records. It annotates
only expansion rows and commits only derived labels and similarity notes. Every
direct-similarity note names an actually observed edge; transitive component
membership is never reported as a fabricated pairwise score. Ambiguous records
remain in manual review. A repeated cluster may become a new category only
after substantive review establishes a distinct decision system and enough
evidence to synthesize and evaluate it.

## Synthesis procedure

For each category:

1. Extract candidate propositions in original research notes outside the public skill tree.
2. Normalize propositions into task, context, decision, action, evidence, and failure-mode fields.
3. Merge propositions that imply the same behavior.
4. Separate universal rules from context-dependent modes.
5. Resolve conflicts using this precedence:
   - safety and explicit user constraints;
   - authoritative project or platform requirements;
   - observable task context;
   - supported specialist guidance;
   - conservative defaults.
6. Add missing safeguards and boundary rules; frequency alone does not determine correctness.
7. Write new instructions without consulting source wording line by line.
8. Test routing, behavior, and non-goals with category and cross-category evals.

## Inclusion test

A rule belongs in a super-skill only if it changes a material decision, action, verification step, or failure response. Advice that is merely stylistic, redundant, unverifiable, or too product-version-specific is omitted or moved to a contextual reference.

## Independence and licensing controls

- Do not store raw third-party skill text in this repository.
- Do not reuse source scripts, examples, templates, names, or assets merely because they are popular.
- Keep source URLs, hashes, and license metadata in the ledger.
- Use the optional similarity checker against a separately held raw corpus before publication.
- Treat unknown or missing source-license metadata as a reason for stronger separation, not as permission.

Independently authored implementation materials are covered by the repository's Apache-2.0 license. Research materials in this directory are licensed under CC BY 4.0 and retain the GitSkills attribution and modification notice in `ATTRIBUTION.md`. Neither license applies to third-party source text, which is not distributed here.

## Releases

A release should state its corpus cutoff, ledger row count, synthesis-matrix revision, and eval results. Material changes to routing boundaries or safety rules must be called out explicitly; source-only additions that do not alter behavior still require an auditable ledger update.
