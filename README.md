# Super Skills

```text
 ____  _   _ ____  _____ ____       ____  _  _____ _     _     ____
/ ___|| | | |  _ \| ____|  _ \     / ___|| |/ /_ _| |   | |   / ___|
\___ \| | | | |_) |  _| | |_) |____\___ \| ' / | || |   | |   \___ \
 ___) | |_| |  __/| |___|  _ <_____|___) | . \ | || |___| |___ ___) |
|____/ \___/|_|   |_____|_| \_\    |____/|_|\_\___|_____|_____|____/
```

**Synthesized agent skills from the patterns, conflicts, and safeguards found across widely used public skills.**

**Super Skills is an open-source project for synthesizing broad agent capabilities from patterns found across widely reused public skills.** The [GitSkills dataset](https://huggingface.co/datasets/mvaccargiu/gitskills) provides the initial empirical foundation.

**These are not bundles of copied prompts or concatenated skills.** The suite currently contains 11 independently installable super-skills. Each combines overlapping guidance, resolves conflicting approaches into contextual modes or decision rules, adds missing safeguards, and defines when the capability should—and should not—activate.

> **Status:** Private research build. Super Skills is sourced from a ranked top-1,000 GitSkills frame. Of 999 eligible hashes, 194 have been substantively reviewed and 130 retained as synthesis evidence; the remaining 805 have received metadata and lineage triage only. Comparative benchmarks, remaining candidate review, and full upstream-lineage verification continue.

The goal is simple: **fewer, broader, rigorously evaluated skills instead of hundreds of narrowly overlapping ones.**

## Skills

| Skill | Scope |
| --- | --- |
| [`interface-design`](skills/interface-design/) | UI/UX, frontend, visual, mobile, and brand design |
| [`software-delivery`](skills/software-delivery/) | Planning, implementation, debugging, testing, review, and completion |
| [`agent-tooling-and-orchestration`](skills/agent-tooling-and-orchestration/) | Skill/tool creation, discovery, evaluation, and agent coordination |
| [`application-engineering`](skills/application-engineering/) | Framework, API, runtime, database, and application architecture |
| [`document-productivity`](skills/document-productivity/) | PDFs, slides, spreadsheets, documents, workplace content, and knowledge notes |
| [`game-development`](skills/game-development/) | Game design and engineering across 2D, mobile, PC/console, audio, and XR |
| [`reasoning-modes`](skills/reasoning-modes/) | Brainstorming, adversarial review, abstraction shifts, and compressed communication |
| [`systems-and-security`](skills/systems-and-security/) | Bash/Linux, PowerShell/Windows, and scoped security assessment |
| [`marketing-and-growth`](skills/marketing-and-growth/) | Market research, positioning, pricing, acquisition, conversion, and fundraising |
| [`connected-service-automation`](skills/connected-service-automation/) | Safe operation of messaging, notes, media, files, sharing, and connected services |
| [`data-science-and-ml`](skills/data-science-and-ml/) | Data quality, experiments, modeling, training, evaluation, and model operations |

Each skill keeps its main `SKILL.md` compact and loads specialized guidance from `references/` only when the task needs it.

## Installation

Copy the directory for the skill you want into the skills directory scanned by your agent host. For example:

```bash
cp -R skills/software-delivery /path/to/your-agent/skills/
```

You can install any subset of the suite. Consult your host's documentation for its skills-directory location and discovery rules.

## Why Super Skills?

Public agent-skill ecosystems contain substantial duplication. Similar skills often:

- solve the same problem with slightly different wording;
- disagree on defaults that are actually context-dependent;
- mix universal rules with framework-, tool-, or aesthetic-specific advice;
- omit important verification, accessibility, safety, or boundary conditions;
- evolve through copying rather than through an explicit dependency or versioning model.

Super Skills treats those files as a **research corpus**, not as components to concatenate.

For each category, the project identifies recurring principles, useful disagreements, specialist techniques, failure modes, and missing safeguards, then authors a new skill from that evidence. The result is intended to behave like a coherent capability rather than a greatest-hits prompt.

## Example

Instead of installing separate skills for debugging, TDD, code review, worktrees, E2E testing, and delivery discipline, copy:

```text
software-delivery/
```

Then invoke it directly when needed:

```text
Use $software-delivery to diagnose this failing test and verify the repair.
```

The skill determines which modes apply rather than imposing every source practice indiscriminately.

## Synthesis methodology

The research uses a ranked top-1,000 GitSkills frame. Its initial substantive review covered 99 eligible hashes in the top 100; subsequent targeted review covered 95 expansion hashes. Together, those reviews retained 130 hashes as synthesis evidence and established the current 11 capability categories. All categories are analyzed for:

1. recurring principles;
2. distinctive specialist guidance;
3. conflicting recommendations;
4. contextual versus universal rules;
5. missing safeguards and quality gates;
6. trigger and scope boundaries.

Conflicts are not resolved by majority vote. Where multiple approaches are valid in different contexts, they become explicit modes or decision rules. Popularity discovers candidate practices; it does not establish correctness.

See [research/METHODOLOGY.md](research/METHODOLOGY.md) for the full process.

## Provenance and reproducibility

The repository includes the artifacts used to make synthesis decisions:

```text
research/
├── source-ledger.csv
├── TOP_1000_EXPANSION.md
├── SAMPLING_PLAN.md
├── synthesis-matrices/
├── conflict-decisions/
├── ATTRIBUTION.md
└── METHODOLOGY.md

evals/
├── shared/
└── category-specific/
```

The [source ledger](research/source-ledger.csv) records 99 baseline hashes and 31 promoted expansion hashes, along with representative repository locations, available commit lineage, and repository-license metadata. Verified upstream lineage is currently available for ten baseline entries; remaining entries are explicitly marked as observed copies pending resolution.

Per-category synthesis matrices record retained rules, contextual decisions, conflict resolutions, and added safeguards. Evaluation specifications cover intended behavior and important non-trigger cases so broad skills do not become broad **always-on** prompts.

## Evaluation status

The repository currently contains 60 behavioral evaluation cases and a shared rubric. These are evaluation **specifications**, not comparative benchmark results.

Before claiming that a super-skill outperforms its sources, the project will compare:

1. an unskilled-agent baseline;
2. the most relevant individual source skill;
3. the corresponding super-skill.

Results must be independently graded and published with the model, task, run, cost, and failure metadata needed to reproduce the comparison.

## Independent authorship

The Super Skills files are newly authored. The repository does **not** contain third-party skill text, scripts, templates, or assets.

Source material is used to identify underlying ideas, procedures, conflicts, and recurring patterns. Optional similarity checks can be run against source material held outside the repository to detect unintended textual overlap.

A provenance entry records research influence. It does not imply incorporation, relicensing, endorsement, or ownership of the referenced source.

## Expanding the evidence base

The top-100 review established the initial architecture; it did not establish corpus-wide completeness. Work within the top-1,000 frame added three category boundaries, but the current 11-category taxonomy is neither claimed to be saturated nor assumed to be complete. The remaining evidence is being screened for:

- additional specialist coverage;
- genuinely distinct approaches;
- underrepresented ecosystems and authors;
- new conflicts or constraints;
- new evaluation cases.

The committed [top-1,000 expansion queue](research/expansion-queue.csv) contains 900 new eligible content hashes plus the non-skill placeholder excluded from the initial baseline. The additions have provisional category routing and near-duplicate flags, while ambiguous records remain in an explicit review queue. See [research/TOP_1000_EXPANSION.md](research/TOP_1000_EXPANSION.md) for the profile, quality checks, and interpretation limits.

Targeted-review yield is not treated as evidence of saturation: candidate selection confounds yield with the quality of the targeting signal, and the reviewed counts within rank bands are too small for a meaningful trend test. Before further ordered review, the project will run the preregistered random probe in [research/SAMPLING_PLAN.md](research/SAMPLING_PLAN.md). Family-level reranking and any future no-new-information claim must also follow that plan.

Regenerate the metadata-only review queue without adding third-party source text to the repository:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-research.txt
.venv/bin/python scripts/export_expansion_candidates.py --limit 1000
```

## Repository structure

```text
super-skills/
├── skills/
│   ├── interface-design/
│   ├── software-delivery/
│   ├── agent-tooling-and-orchestration/
│   ├── application-engineering/
│   ├── document-productivity/
│   ├── game-development/
│   ├── reasoning-modes/
│   ├── systems-and-security/
│   ├── marketing-and-growth/
│   ├── connected-service-automation/
│   └── data-science-and-ml/
├── research/
├── evals/
├── scripts/
├── README.md
└── LICENSE
```

## Licensing

Unless otherwise noted, independently authored implementation materials—including `skills/`, `scripts/`, and `evals/`—are licensed under the [Apache License 2.0](LICENSE).

Research materials under `research/` are licensed under [Creative Commons Attribution 4.0 International](research/LICENSE). Material derived from GitSkills metadata carries the attribution and modification notice in [research/ATTRIBUTION.md](research/ATTRIBUTION.md).

Referenced third-party repositories retain their own copyrights and licenses. Their source text is not distributed by this repository.
