# Research attribution

Parts of the research metadata in this directory are adapted from:

**GitSkills: A Dataset of Agent Skills on GitHub**

Giuseppe Destefanis, Daniel Graziotin, Matteo Vaccargiu, and Marco Ortu

- Dataset: https://huggingface.co/datasets/mvaccargiu/gitskills
- Paper: https://arxiv.org/abs/2608.10906
- Archive DOI: https://doi.org/10.5281/zenodo.21875637
- Dataset metadata license: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

## Modifications

Super Skills makes the following changes to the GitSkills metadata and aggregation:

- selects the ranked top-100 baseline and excludes one non-skill placeholder;
- ranks the top 1,000 distinct content hashes and publishes a metadata-only expansion queue;
- adds provisional category routing, review decisions, and content-similarity lineage flags without redistributing descriptions or source text;
- groups the remaining 99 content hashes into eight initial synthesized capability categories;
- promotes 31 expansion hashes to the provenance ledger after substantive review and establishes three additional capability categories;
- adds super-skill mappings, representative source URLs, upstream-verification status, repository-license metadata, and reuse-policy fields;
- derives category counts, synthesis matrices, conflict decisions, and evaluation specifications; and
- reformats selected metadata into repository-specific CSV and Markdown artifacts.

The GitSkills dataset card states that its collected metadata and aggregation are CC BY 4.0, while reproduced source-file contents remain subject to their originating repositories' licenses. Super Skills does not redistribute those source-file contents.

Representative repositories in `source-ledger.csv` are evidence locations, not necessarily original authors or upstream sources. Rows without verified lineage are explicitly marked as observed copies.

No endorsement by the GitSkills authors, dataset maintainers, or referenced repository owners is implied.
