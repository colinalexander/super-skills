# Synthesis methodology

## Objective

Produce one coherent, high-utility skill per category from a body of public skill evidence. The unit of work is a decision rule or operating principle, not a passage of source text.

## Baseline corpus

The initial baseline uses the top 100 GitSkills content groups ranked by repository count. One placeholder row was excluded, leaving 99 content hashes across eight initial categories. Identical hashes are exact byte matches; repeated names may still represent different versions.

The source ledger records retained evidence at verified upstream locations or
representative observed copies. The separate `review-decisions.csv` records
every substantive outcome, including decisions not to retain a source, the
specific synthesis rule that already covers it, and direct near-duplicate links
where available. “Observed copy” must not be read as an authorship claim.

The [occurrence, lineage, and concentration audit](CORPUS_AUDIT.md) found that
34.04% of baseline repository–hash coverage belongs to repeated multi-skill
collection signatures and 41.88% occurs in repositories containing at least 10
baseline hashes. Occurrence rank therefore measures bundle inclusion as well as
individual adoption. Historical-blob analysis also found 21 exact and two near
Anthropic matches; 11 exact matches were frozen older upstream versions at the
collection cutoff. These findings affect interpretation and reranking, not the
byte-level occurrence counts themselves.

## Evidence expansion

Popularity is useful for discovering common conventions but produces visibility, age, ecosystem, and copying biases. Expansion therefore uses the following sequence:

1. Pull the top 1,000 distinct content hashes by repository count.
2. Classify them into an existing category or an explicit taxonomy-review queue.
3. Collapse exact copies and flag near-duplicates before substantive review.
4. Within each category, prioritize distinct authors, ecosystems, task types, and minority approaches.
5. Review lower-ranked specialist sources when the high-ranked set leaves an identified coverage gap.
6. Treat 20 consecutive eligible, lineage-independent candidates with no new information as a review checkpoint, not a population-saturation claim.

The top-1,000 ranking, metadata-only queue, provisional category triage, and
near-duplicate flags are complete. Metadata classification is only a routing
aid. Substantive review, no-new-information decisions, and any resulting
changes to skills or evals remain separate stages; queue membership and a
proposed category alone are not synthesis evidence.

Thirty-one expansion hashes have passed substantive review and been promoted to
the source ledger. Sixty-four additional sources were reviewed without adding a
material proposition. The review established `marketing-and-growth`,
`connected-service-automation`, and `data-science-and-ml` as distinct decision
systems, bringing the observed taxonomy to 11 categories. The
`document-productivity` category was subsequently withheld because 10 of its 11
evidence hashes exactly match historical Anthropic blobs, including eight from
the source-available document set. The active suite therefore contains 10
skills supported by 119 retained hashes; all 130 research decisions remain in
the provenance records. Application engineering and
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

Record exclusions and the reason for them. Population-level claims and future
ordered review are governed by the preregistered definitions, random probe, and
family-rerank requirements in `SAMPLING_PLAN.md`.

The 194-row decision register distinguishes retained evidence, context- or
product-specific material, near-duplicate lineages, out-of-scope records, and
propositions already covered by a named synthesis rule. Its hash-level
`reason_detail`, `covered_by`, and `duplicate_of_file_sha` fields make later
no-new-information decisions auditable. These are substantive research
judgments, not labels regenerated mechanically from filenames.

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
6. Recheck recency and register before synthesis: verify prohibitions, worked examples, model-generation assumptions, and product-specific instructions against current primary sources; omit obsolete tactics or convert them into explicitly contextual modes.
7. Add missing safeguards and boundary rules; frequency alone does not determine correctness.
8. Write new instructions without consulting source wording line by line.
9. Test routing, behavior, and non-goals with category and cross-category evals.

A stale or vendor-specific copy may remain valid provenance, but it is not
current authority. The synthesis record must distinguish a durable principle
from an obsolete example, model-era prompting tactic, or superseded product
constraint.

Comparative evaluation follows `evals/BENCHMARK.md`. Arm composition is fixed
mechanically before execution: no skills, one rank-selected source, all 119
retained sources supporting active categories, and all 10 active super-skills.
The exhaustive source arm is an upper
bound on overhead and conflict exposure, not a typical deployment estimate.
Thirty-six global true negatives supply the negative denominator for activation
precision. Natural-host results and a fixed full-skill-budget sensitivity analysis
are both required so lower context cost cannot substitute for task quality.
Two blinded independent human graders produce the primary quality outcome, and
predeclared non-inferiority, false-activation, and critical-side-effect gates
define results that falsify the consolidation hypothesis.

## Inclusion test

A rule belongs in a super-skill only if it changes a material decision, action, verification step, or failure response. Advice that is merely stylistic, redundant, unverifiable, or too product-version-specific is omitted or moved to a contextual reference.

## Independence and licensing controls

- Do not store raw third-party skill text in this repository.
- Do not reuse source scripts, examples, templates, names, or assets merely because they are popular.
- Keep source URLs, hashes, and license metadata in the ledger.
- Resolve licensing at file lineage: repository-level license metadata on a
  redistributed file does not override verified upstream file-level terms and
  is not evidence of relicensing.
- Run exact and thresholded near-lineage checks before synthesis and release.
  The baseline control found 23 of 99 hashes with exact or qualifying near
  Anthropic lineage, including restrictively licensed document sources and
  stale historical versions.
- Treat the similarity checker as a mandatory release gate against every
  distributable skill file and the full separately held raw corpus. Rerun it
  whenever either population changes; the current gate covers 66 public files
  against all 999 eligible baseline-plus-expansion sources.
- Treat unknown or missing source-license metadata as a reason for stronger separation, not as permission.
- Withhold an implementation when its evidence is overwhelmingly derived from
  one restrictively licensed vendor lineage and independent corpus support is
  insufficient.

Independently authored implementation materials are covered by the repository's Apache-2.0 license. Research materials in this directory are licensed under CC BY 4.0 and retain the GitSkills attribution and modification notice in `ATTRIBUTION.md`. Neither license applies to third-party source text, which is not distributed here.

## Releases

A release should state its corpus cutoff, review-decision and retained-ledger row counts, synthesis-matrix revision, pinned tokenizer/count record, and eval results. Material changes to routing boundaries or safety rules must be called out explicitly; source-only additions that do not alter behavior still require an auditable review-decision update.
