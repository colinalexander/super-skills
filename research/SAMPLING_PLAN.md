# Preregistered sampling and stopping plan

Effective date: this plan takes effect when its pull request is merged. No probe
sample may be drawn before that merge.

Protocol amendment before sampling: no probe had been drawn when the product-
validation foundation was specified. The draw is deferred until the four-arm
benchmark protocol, global true negatives, review-decision register, worked
conflict example, and validation-enforced token counts are merged. This changes
execution order only; the population, seed rule, sample size, masking, and
analysis plan below remain unchanged.

The public seed commit is
`080777b878c37912a63627b344dc51b0e2df1e0c`, the squash merge that activated
this plan. Later documentation changes do not replace that seed.

## Purpose

Estimate the residual information content of the unreviewed portion of the
ranked top-1,000 GitSkills frame without using the metadata signals that drove
targeted review. The probe measures in-frame residual evidence; it cannot by
itself establish completeness beyond rank 1,000.

## Population and sample

- Population: the 805 rows in `expansion-queue.csv` whose status is
  `metadata-triaged` or `manual-review` at the effective commit.
- Sample size: 50 hashes drawn uniformly without replacement.
- Randomization: after this plan is squash-merged, sort the population by
  `file_sha`, assign each row the SHA-256 digest of the resulting commit SHA, a
  colon, and its `file_sha`, then select the 50 smallest digests. The merge SHA
  is unknown while the plan is authored and becomes the public random seed.
- Freeze: commit the selected hashes and effective population checksum before
  substantive review begins. Replacements are allowed only for inaccessible or
  non-skill records and must use the next digest in order with a recorded reason.

This deterministic procedure makes the draw independently reproducible while
keeping source ranks and triage labels out of selection.

## Review masking

The review worksheet will initially expose only an opaque sample identifier and
the reconstructed source content. Reviewers must not see rank, repository or
occurrence count, provisional category, triage status, similarity note, owner,
or repository identity—except where identity is inseparable from the skill
instructions—until the substantive decision is locked.

Reviewers may use the existing 11 category definitions because the primary
question is whether a source changes the current synthesis. After the decision
is recorded, provenance and lineage data are unmasked for deduplication and
attribution checks.

## Preregistered outcome definitions

A source is **retained** only when a lineage-independent proposition passes the
repository inclusion test and produces at least one of these material outcomes:

- **New principle:** a generally applicable rule changes an action, decision,
  verification step, or failure response in meaningful category contexts.
- **New mode:** a distinct context requires a different operating strategy or
  branch in an existing decision rule.
- **New constraint:** a previously absent precondition, limit, or boundary
  changes when or how the capability may act.
- **New conflict:** supported guidance is incompatible with an existing rule and
  requires an explicit precedence decision or contextual branch.
- **New safeguard:** a distinct material risk requires prevention, confirmation,
  containment, recovery, or verification behavior.
- **New evaluation case:** a behaviorally distinct scenario can falsify an
  existing rule or expose an untested routing boundary. A new example, product,
  framework, or wording alone does not qualify.
- **New category:** the source participates in a coherent decision system that
  cannot be routed to an existing category without materially weakening its
  trigger, rules, or evaluation boundary.

Stylistic variants, examples of existing rules, product-specific restatements,
and near-duplicate lineage variants are recorded but do not count as retained
information.

## Analysis and reporting

Report, without substituting targeted-review results into the estimate:

1. retained count out of 50;
2. a 95% confidence interval for the population count obtained by inverting the
   hypergeometric distribution for sampling without replacement;
3. that interval expressed as a rate and count among the 805 unreviewed hashes;
4. material outcome types and category routing after unmasking;
5. exclusions, replacements, and lineage duplicates; and
6. rank distribution only after all substantive decisions are locked.

The rank-band targeted-review counts may be shown as review-progress counts but
not used to infer a saturation trajectory. A zero or low probe yield is evidence
about the unreviewed in-frame population, not proof of corpus-wide completeness.
Any new category, material safety constraint, or recurring retained lineage
triggers focused follow-up regardless of the aggregate rate.

## Family-level rerank

The random probe precedes the rerank so its estimate remains independent of a
new ordering. The rerank will:

1. cluster exact and probable near-duplicate hashes into skill families;
2. deduplicate repositories within each family;
3. report unique-owner coverage alongside unique-repository coverage;
4. identify fork networks and concentrated single-owner replication where data
   permits;
5. admit families whose aggregate coverage clears the cutoff even when no
   individual hash appeared in the original top 1,000; and
6. map all 130 retained evidence hashes to their resulting family and report
   whether that family remains inside the reranked frame.

The primary family ranking will use unique-repository coverage, with
unique-owner coverage as a required sensitivity view rather than silently
combining the two measures. Occurrences remain descriptive and do not determine
the primary order.

## No-new-information checkpoints

For future ordered review, a category reaches a **review checkpoint** after 20
consecutive eligible, lineage-independent candidates add none of the material
outcomes defined above. The queue order, eligibility rules, and category routing
must be frozen before the run begins. Interrupted or selectively reordered
sequences do not qualify.

A review checkpoint is not a population-saturation claim. Any stronger claim
must jointly report the random-probe estimate, family-reranked coverage,
owner-level sensitivity, boundary behavior beyond rank 1,000, and unresolved
manual-review records. The current 11 categories remain a revisable taxonomy.
