# Synthesis methodology

## Objective

Produce one coherent, high-utility skill per category from a body of public skill evidence. The unit of work is a decision rule or operating principle, not a passage of source text.

## Baseline corpus

Version 0 uses the top 100 GitSkills content groups ranked by repository count. One placeholder row was excluded, leaving 99 content hashes across eight categories. Identical hashes are exact byte matches; repeated names may still represent different versions.

The source ledger records both verified upstream locations and representative observed copies. “Observed copy” must not be read as an authorship claim.

## Evidence expansion

Popularity is useful for discovering common conventions but produces visibility, age, ecosystem, and copying biases. Expansion therefore uses the following sequence:

The top-1,000 ranking, metadata-only queue, provisional category triage, and
near-duplicate flags are complete. Metadata classification is only a routing
aid. Substantive review, evidence-saturation decisions, and any resulting
changes to skills or evals remain separate stages; queue membership and a
proposed category alone are not synthesis evidence.

Seven expansion hashes have passed substantive review and been promoted to the
source ledger. Forty additional sources were reviewed without adding a material
proposition. Application engineering and software delivery have each reached
the 20-source saturation checkpoint; the remaining categories retain
provisional or review-queue status.

1. Pull the top 1,000 distinct content hashes by repository count.
2. Classify them into the existing eight categories or an explicit review queue.
3. Collapse exact copies and flag near-duplicates before substantive review.
4. Within each category, prioritize distinct authors, ecosystems, task types, and minority approaches.
5. Review lower-ranked specialist sources when the high-ranked set leaves an identified coverage gap.
6. Stop a category after 20 consecutive eligible candidates contribute no new principle, mode, constraint, conflict, or eval case.

This is an evidence-saturation rule, not a fixed-source quota. Record exclusions and the reason for them.

`scripts/export_expansion_candidates.py` creates the metadata-only review queue. Raw text used during review must remain in a separate, uncommitted research location.

`scripts/triage_expansion.py` uses representative names and descriptions to
propose categories, then uses content n-gram similarity to flag possible
lineages. It commits only derived labels and similarity notes. Ambiguous
records remain in manual review, and apparent categories outside the current
suite remain explicit taxonomy-review candidates.

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

## Versioning

A release should state its corpus cutoff, ledger row count, synthesis-matrix version, and eval results. Material changes to routing boundaries or safety rules require a major or minor release note; source-only additions that do not alter behavior may be a patch.
