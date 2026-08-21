# GitSkills occurrence, lineage, and concentration audit

Date: 2026-08-20 (US/Pacific)

## Headline finding

GitSkills occurrence rank measures **bundle inclusion as well as individual
adoption**. In the 99-hash baseline:

- 10,690 of 31,405 distinct repository–hash pairs (34.04%) belong to repeated
  multi-hash collection signatures;
- 13,153 pairs (41.88%) occur in repositories containing at least 10 baseline
  hashes; and
- deduplicating repository coverage by owner retains 30,100 owner–hash pairs
  (95.84%), so the concentration is not explained by one owner operating many
  repositories.

Anyone using raw GitSkills occurrence counts as a popularity proxy is therefore
partly counting curated collections, mirrors, registries, and bundled skill
sets. Repository reuse is real, but it is not equivalent to independent
authorship or an independent selection decision.

> “Widely reused public skills” means files redistributed across many non-fork
> repositories. It does not necessarily mean independently authored or
> independently selected community practices.

## Grain and population

The baseline contains 99 eligible hashes from the ranked top 100; rank 24 is a
non-skill placeholder. Its intended analytical grain is one distinct
repository–hash pair:

| Measure | Count |
| --- | ---: |
| Distinct repository–hash pairs | 31,405 |
| Distinct repositories | 9,222 |
| Distinct owner–hash pairs | 30,100 |
| Path-level artifact rows | 42,684 |

The 42,684 figure is not repository coverage: it counts multiple paths for the
same hash in the same repository. All coverage percentages in this audit use
the deduplicated 31,405-pair denominator.

Across the full GitSkills `repos` table, only 3 of 282,200 rows are marked as
forks; 515 are unknown. The baseline has no marked-fork repository–hash pairs.
This near-constant field follows from GitHub Code Search's restricted indexing
of forks, which the [GitSkills dataset card](https://huggingface.co/datasets/mvaccargiu/gitskills)
identifies as a limitation. It must not be interpreted as evidence that GitHub
forks are rare. `is_fork` is not useful for further independence analysis in
this frame.

## Collection concentration

A repository collection signature is the exact set of baseline hashes found in
that repository. For the repeated-signature statistic, singleton signatures
are excluded and a multi-hash signature must appear in at least two
repositories.

| Baseline hashes in repository | Repositories | Repository–hash pairs | Share |
| --- | ---: | ---: | ---: |
| 1 | 4,964 | 4,964 | 15.81% |
| 2–4 | 2,289 | 6,110 | 19.46% |
| 5–9 | 1,111 | 7,178 | 22.86% |
| 10–24 | 786 | 10,621 | 33.82% |
| 25+ | 72 | 2,532 | 8.06% |

Repeated multi-hash signatures account for 2,303 repositories and 10,690
repository–hash pairs. This is a distribution-path indicator, not proof that
every repository with the same set was copied from the same collection.

## Anthropic historical lineage

The 99 baseline hashes were compared with every `SKILL.md` blob reachable from
the `main` history of `anthropics/skills`. Exact matching uses Git blob identity.
Near matching uses normalized eight-word shingle containment, consistent with
`scripts/check_similarity.py`, at a 20% smaller-document threshold.

| Result | Hashes | Repository–hash coverage |
| --- | ---: | ---: |
| Exact historical blob | 21 of 99 | 10,107 of 31,405 (32.2%) |
| Exact or qualifying near match | 23 of 99 | 10,712 of 31,405 (34.1%) |

The two near matches are a `frontend-design` variant with 100.0% smaller-file
containment and a `skill-creator` variant with 74.8% containment.

Of the 21 exact historical matches, 10 were still present at Anthropic's last
`main` commit before the GitSkills collection cutoff. The other **11 were frozen
older versions**, demonstrating that copy-based distribution can propagate a
snapshot after upstream guidance changes.

GitSkills contains only three artifact rows for the origin repository
`anthropics/skills`. Origin absence therefore cannot be used to classify every
copy as stale. The 21 exact and two thresholded near matches are a **floor** on
broader Anthropic lineage because byte changes break exact identity and more
distant descendants can fall below the near-match threshold; the near-match
view reduces but does not eliminate that limitation.

## Withheld document category

Ten of the 11 `document-productivity` evidence hashes exactly match historical
Anthropic blobs. Eight are versions of the DOCX, PDF, PPTX, or XLSX skills whose
upstream file-level terms are source-available rather than open-source; see, for
example, the current [PPTX license](https://github.com/anthropics/skills/blob/main/skills/pptx/LICENSE.txt).

Some observed copies sit in repositories labeled MIT. Repository-level license
metadata does not relicense a copied file and must not override verified
file-level origin terms. Because this category is overwhelmingly vendor-derived,
Super Skills preserves its research records but withholds the installable skill
and evaluation cases. This is a provenance and product decision, not a legal
determination.

## Reranking rule

**Lineage family is the ranking unit.** The future rerank will:

1. cluster exact and probable near-duplicate hashes into families;
2. deduplicate repositories within each family; and
3. rank families by unique-repository coverage, with unique-owner coverage as a
   sensitivity view.

Collection signature is correlated with lineage propagation, so it will not be
applied as a second multiplicative discount. Instead, every family will report
its share of coverage arising from repeated collection signatures and from
repositories containing at least 10 frame hashes. This keeps provenance
consolidation and distribution concentration analytically distinct.

## Interpretation

The fork-contamination hypothesis is not supported. The stronger finding is
that bundle amplification and stale-copy propagation materially shape the top
of the occurrence distribution. The baseline is more defensible than a fork
count suggested, but less independent than raw repository counts imply.
