# Super Skills

```text
 ____  _   _ ____  _____ ____       ____  _  _____ _     _     ____
/ ___|| | | |  _ \| ____|  _ \     / ___|| |/ /_ _| |   | |   / ___|
\___ \| | | | |_) |  _| | |_) |____\___ \| ' / | || |   | |   \___ \
 ___) | |_| |  __/| |___|  _ <_____|___) | . \ | || |___| |___ ___) |
|____/ \___/|_|   |_____|_| \_\    |____/|_|\_\___|_____|_____|____/
```

**Synthesized agent skills from the patterns, conflicts, and safeguards found across widely used public skills.**

**Super Skills is an open-source project for synthesizing broad agent capabilities from patterns found across widely reused public skills.** The [GitSkills dataset](https://huggingface.co/datasets/mvaccargiu/gitskills) and accompanying [paper](https://arxiv.org/abs/2608.10906) define the project's initial sampling frame.

**These are not bundles of copied prompts or concatenated skills.** The suite currently contains 10 independently installable super-skills. Each combines overlapping guidance, resolves conflicting approaches into contextual modes or decision rules, adds missing safeguards, and defines when the capability should—and should not—activate.

> **Status:** Active research project. Super Skills draws from a ranked top-1,000 GitSkills frame. Of 999 eligible hashes, 194 have been substantively reviewed and 130 retained as research evidence. Eleven retained hashes support the deliberately withheld `document-productivity` category, leaving 119 evidence hashes for the 10-skill active suite; the remaining 805 hashes have received metadata and lineage triage only. The full-corpus similarity gate has passed. Comparative benchmarks, the preregistered random probe, and remaining candidate and upstream-lineage review are pending.

The goal is simple: **fewer, broader, rigorously evaluated skills instead of hundreds of narrowly overlapping ones.**

## What occurrence rank measures

GitSkills occurrence rank measures redistribution as well as individual adoption. In the 99-hash baseline, **34.0% of distinct repository–hash coverage appears in repeated multi-skill collection signatures**, and **41.9% appears in repositories containing at least 10 baseline hashes**. Curated bundles, registries, and mirrors therefore materially amplify occurrence counts.

The frame is not dominated by one owner: deduplicating repository coverage by owner retains 95.8% of repository–hash coverage. But repository counts still must not be read as independent authorship or independent selection decisions.

> “Widely reused public skills” means files redistributed across many non-fork repositories. It does not necessarily mean independently authored or independently selected community practices.

Historical-lineage analysis found 21 exact Anthropic Git blobs among the 99 baseline hashes and two additional near matches, representing 34.1% of repository–hash coverage. Eleven of the 21 exact matches were already older than Anthropic's version at the GitSkills collection cutoff, directly demonstrating stale-copy propagation. Exact and thresholded near matching still provide only a floor on broader lineage because edited descendants can fall below the threshold. Separately, GitSkills retrieved only three artifacts from the origin repository, so origin absence cannot classify a copy as stale. See the [corpus audit](research/CORPUS_AUDIT.md) for methods, counts, and limitations.

## Skills

| Skill | Scope | Description tokens | Core tokens | Full tokens |
| --- | --- | ---: | ---: | ---: |
| [`interface-design`](skills/interface-design/) | UI/UX, frontend, visual, mobile, and brand design | 67 | 614 | 2,197 |
| [`software-delivery`](skills/software-delivery/) | Planning, implementation, debugging, testing, review, and completion | 55 | 516 | 1,970 |
| [`agent-tooling-and-orchestration`](skills/agent-tooling-and-orchestration/) | Skill/tool creation, discovery, evaluation, and agent coordination | 51 | 454 | 1,602 |
| [`application-engineering`](skills/application-engineering/) | Framework, API, runtime, database, and application architecture | 67 | 463 | 1,613 |
| [`game-development`](skills/game-development/) | Game design and engineering across 2D, mobile, PC/console, audio, and XR | 58 | 456 | 1,699 |
| [`reasoning-modes`](skills/reasoning-modes/) | Brainstorming, adversarial review, abstraction shifts, and compressed communication | 48 | 399 | 1,274 |
| [`systems-and-security`](skills/systems-and-security/) | Bash/Linux, PowerShell/Windows, and scoped security assessment | 55 | 432 | 1,182 |
| [`marketing-and-growth`](skills/marketing-and-growth/) | Market research, positioning, pricing, acquisition, conversion, and fundraising | 60 | 558 | 1,968 |
| [`connected-service-automation`](skills/connected-service-automation/) | Safe operation of messaging, notes, media, files, sharing, and connected services | 57 | 463 | 1,164 |
| [`data-science-and-ml`](skills/data-science-and-ml/) | Data quality, experiments, modeling, training, evaluation, and model operations | 62 | 479 | 1,366 |

Description counts measure the always-loaded front-matter discovery text. The 10 active super-skill descriptions total **580 tokens**; the same tokenizer applied to the 119 active GitSkills evidence descriptions yields **5,613 tokens**, a 9.7× normalized discovery-text difference before host framing. This quantifies the cost of making the skills discoverable on every request; it does **not** measure post-activation instruction cost or task quality. Core counts cover `SKILL.md`; full counts include every Markdown reference. All counts use `cl100k_base` with pinned `tiktoken==0.11.0` and exclude host framing, tool schemas, and conversation context. The generated [active-skill](research/token-counts.csv) and [retained-source](research/source-description-token-counts.csv) records are validation-enforced. Each skill loads specialized guidance from `references/` only when the task needs it.

### Detailed skill descriptions

- [`interface-design`](skills/interface-design/): Create, redesign, implement, or critique web and mobile interfaces, graphics, design systems, and brand expression. Use for UI/UX, frontend presentation, image-to-code, logos, brand boards, banners, animation, algorithmic art, or work where visual hierarchy, interaction, or art direction shapes the result; exclude office documents.
- [`software-delivery`](skills/software-delivery/): Plan, implement, diagnose, test, review, and finish software changes with evidence. Use when the main challenge is changing code safely, isolating work, resolving a defect, responding to review, or proving completion; combine with a domain skill for framework- or product-specific decisions.
- [`agent-tooling-and-orchestration`](skills/agent-tooling-and-orchestration/): Design, create, improve, discover, evaluate, or install agent skills and tool interfaces, and coordinate multiple agents. Use when the work concerns reusable agent capabilities, MCP-style tools, capability routing, delegation boundaries, or skill quality rather than ordinary application implementation.
- [`application-engineering`](skills/application-engineering/): Design or implement application architecture across APIs, components, runtimes, frameworks, and persistence. Use for FastAPI, Django, Python, Node.js, React, Next.js, React Native, Postgres, Supabase, database design, and related engineering decisions; use another skill when delivery process or visual direction is primary.
- [`game-development`](skills/game-development/): Design, implement, tune, or critique games and immersive experiences across 2D, mobile, PC/console, audio, VR, and AR. Use when a player loop, feel, progression, real-time simulation, platform input, performance budget, game audio, or embodied interaction is central.
- [`reasoning-modes`](skills/reasoning-modes/): Apply a deliberately requested interaction mode: exploratory brainstorming, adversarial questioning, abstraction and perspective shifts, or extremely compressed plain-language communication. Use when the user asks how the reasoning conversation should proceed, not merely because a task is difficult.
- [`systems-and-security`](skills/systems-and-security/): Operate and troubleshoot Bash/Linux or PowerShell/Windows environments, and perform explicitly requested defensive security assessment. Use when shell semantics, processes, services, permissions, storage, networking, or vulnerability analysis are central; never infer authorization to scan or exploit from a routine systems task.
- [`marketing-and-growth`](skills/marketing-and-growth/): Develop evidence-based marketing, growth, pricing, conversion, positioning, and fundraising work. Use for market research, product marketing, SEO, acquisition, lifecycle optimization, monetization, marketing copy, ads, or investor communications; do not use for visual design, general office-document production, or software implementation.
- [`connected-service-automation`](skills/connected-service-automation/): Operate user-authorized messaging, notes, media, cloud storage, sharing, and similar connected services through available tools or CLIs. Use when the task is to inspect or change state in an external personal or workplace service; use another skill to design a new integration or agent tool.
- [`data-science-and-ml`](skills/data-science-and-ml/): Design, analyze, train, evaluate, and operationalize statistical or machine-learning systems. Use for data quality, experiments, causal inference, predictive modeling, deep learning, computer vision, fine-tuning, distributed training, or model monitoring; use application engineering for ordinary product architecture without an analytical or learned-model decision.

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

In hosts that support named skill invocation, invoke it directly when needed:

```text
Use $software-delivery to diagnose this failing test and verify the repair.
```

The skill determines which modes apply rather than imposing every source practice indiscriminately.

## Synthesis methodology

The research uses a ranked top-1,000 GitSkills frame. Its initial substantive review covered 99 eligible hashes in the top 100; subsequent targeted review covered 95 expansion hashes. Together, those reviews retained 130 hashes and identified 11 capability categories. One category is withheld, leaving 119 evidence hashes across the 10-skill active suite. Categories are analyzed for:

1. recurring principles;
2. distinctive specialist guidance;
3. conflicting recommendations;
4. contextual versus universal rules;
5. missing safeguards and quality gates;
6. trigger and scope boundaries.

Conflicts are not resolved by majority vote. Where multiple approaches are valid in different contexts, they become explicit modes or decision rules. Popularity discovers candidate practices; it does not establish correctness.

See [research/METHODOLOGY.md](research/METHODOLOGY.md) for the full process.

### Worked conflict: minimalist versus industrial interfaces

The retained [`minimalist-ui`](https://github.com/30Sativa/EXE201-PetOmi-Platform/blob/372f420e1c07852b5a3ef31e4cd6ebf6083752b3/apps/web/.agents/skills/minimalist-ui/SKILL.md) source favors restrained monochrome, generous whitespace, soft geometry, and almost no shadow. [`industrial-brutalist-ui`](https://github.com/30x-llc/Monet/blob/7d8cc7a3349de13f472601a8c7ab4f068e5dff46/skills/craft/brutalist-skill/SKILL.md)—the upstream front-matter name for the file stored at `brutalist-skill/SKILL.md`—favors rigid square geometry, visible compartmentalization, aggressive type, and dense telemetry.

The synthesis resolves them with an explicit rule:

1. Preserve an existing product design system or supplied reference unless change is authorized.
2. For focused reading or calm productivity, use the minimalist profile when hierarchy and whitespace reduce cognitive load.
3. For expert operational scanning, dense status comparison, or an explicitly mechanical identity, use the industrial-brutalist profile.
4. If neither audience/task pattern applies, choose neither; derive another visual thesis. Accessibility, platform behavior, legibility, and performance override either profile.

A majority-vote pipeline would make whichever profile appeared more often the default and silently discard the other. Super Skills retains both as contextual modes. The full decision record is in [research/conflict-decisions/interface-aesthetic-profiles.md](research/conflict-decisions/interface-aesthetic-profiles.md).

## Provenance and reproducibility

The repository includes the artifacts used to make synthesis decisions:

```text
research/
├── source-ledger.csv
├── review-decisions.csv
├── token-counts.csv
├── source-description-token-counts.csv
├── CORPUS_AUDIT.md
├── TOP_1000_EXPANSION.md
├── SAMPLING_PLAN.md
├── synthesis-matrices/
├── conflict-decisions/
├── ATTRIBUTION.md
└── METHODOLOGY.md

evals/
├── BENCHMARK.md
├── shared/
└── category-specific/
```

The [source ledger](research/source-ledger.csv) records the 130 retained research hashes, including the 11 withheld records, along with representative or verified upstream locations, available commit lineage, and the best available license metadata. The separate [review-decision register](research/review-decisions.csv) records all 194 substantive decisions: 130 retained and 64 not retained, with decision codes, hash-level reasons, the synthesis rule covering a rejection, and direct near-duplicate links where available. The [corpus audit](research/CORPUS_AUDIT.md) adds historical-blob, near-match, staleness, owner, and collection-signature analysis; verified exact-lineage findings are recorded in the ledger itself.

Per-category synthesis matrices record retained rules, contextual decisions, conflict resolutions, and added safeguards. Evaluation specifications cover intended behavior and important non-trigger cases so broad skills do not become broad **always-on** prompts.

## Evaluation status

The repository currently contains 56 active-category cases, 12 global true negatives, a shared rubric, and a [comparative protocol](evals/BENCHMARK.md). These are 68 evaluation **specifications**, not benchmark results.

Before claiming that a super-skill outperforms its sources, the project will compare:

1. an unskilled-agent baseline;
2. the mechanically selected highest-ranked source skill;
3. all 119 retained sources supporting active categories installed concurrently as an upper bound on narrow-skill overhead and conflict exposure, not as a typical deployment; and
4. all 10 active super-skills installed concurrently.

The protocol freezes arm composition before execution, includes true negatives for activation precision, and reports both natural-host behavior and a matched-token-budget sensitivity analysis. Results must be independently graded and published with the model, task, run, cost, token, latency, activation, and failure metadata needed to reproduce the comparison. No performance claim will be made before those results exist.

## Independent authorship

The Super Skills files are newly authored. The repository does **not** contain third-party skill text, scripts, templates, or assets.

Source material is used to identify underlying ideas, procedures, conflicts, and recurring patterns. Before release, the mandatory similarity gate checks every distributable skill file against the full externally held raw-source corpus for unintended textual overlap.

A provenance entry records research influence. It does not imply incorporation, relicensing, endorsement, or ownership of the referenced source.

## Withheld category: document productivity

`document-productivity` is deliberately not distributed as a skill. Ten of its 11 retained evidence hashes exactly match historical Anthropic blobs; eight belong to Anthropic's source-available DOCX, PDF, PPTX, and XLSX set. That evidence supports a category boundary, but not a defensible claim that the implementation synthesizes independent community practice.

Repository-level license metadata on a copied file is not a relicensing event. Rather than publish a category whose evidence is overwhelmingly vendor-derived, the project preserves the provenance and synthesis decision under `research/` while withholding the installable skill and its benchmark cases. It will not return to the active suite unless a new, independently sourced evidence base supports it.

The boundary remains explicit: `marketing-and-growth` may own the commercial argument in investor communications, and `reasoning-modes` may change how a response is compressed, but neither owns office-file construction, formatting, PDF handling, slides, spreadsheets, knowledge Markdown, or general workplace-document production.

## Expanding the evidence base

The top-100 review established the initial architecture; it did not establish corpus-wide completeness. Work within the top-1,000 frame added three category boundaries. The resulting 10-skill active suite and one withheld category are neither claimed to be saturated nor assumed to be complete. The remaining evidence is being screened for:

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
