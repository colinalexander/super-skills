# Super Skills

Super Skills is an open suite of eight category-level agent skills. Each skill synthesizes recurring practices, useful disagreements, and missing safeguards found across widely copied public skills. The result is a set of coherent operating systems, not concatenated source files.

## The suite

| Skill | Scope | Baseline evidence |
| --- | --- | ---: |
| `interface-design` | UI/UX, frontend, visual, mobile, and brand design | 23 content hashes |
| `software-delivery` | Planning, implementation, debugging, testing, review, and completion | 19 |
| `agent-tooling-and-orchestration` | Skill/tool creation, discovery, evaluation, and agent coordination | 16 |
| `application-engineering` | Framework, API, runtime, and data architecture | 14 |
| `document-productivity` | PDF, slides, spreadsheets, documents, workplace writing, and knowledge notes | 11 |
| `game-development` | Game design and engineering across 2D, mobile, PC/console, audio, and XR | 7 |
| `reasoning-modes` | Brainstorming, adversarial review, abstraction shifts, and compressed communication | 6 |
| `systems-and-security` | Bash/Linux, PowerShell/Windows, and scoped security assessment | 3 |

The initial evidence set contains 99 ranked content hashes from the GitSkills top 100; one non-skill placeholder was excluded. Because repeated hashes and names can represent the same idea, counts are evidence volume rather than claims of independence.

## Use

Copy or link one or more directories under `skills/` into a host that supports `SKILL.md`. Invoke a skill by name when you want its full workflow, for example:

```text
Use $software-delivery to diagnose this failing test and verify the repair.
```

Each skill keeps its entry file compact and routes deeper work to focused files in `references/`.

## How synthesis works

The public files are newly written. No third-party skill text, scripts, or assets are included. The repository retains:

- a row-level [source ledger](research/source-ledger.csv) with hashes and reference URLs;
- a [methodology](research/METHODOLOGY.md) defining selection, synthesis, and saturation;
- per-category synthesis matrices recording retained principles and resolved conflicts;
- boundary-focused evals for both expected behavior and misrouting;
- structural and optional source-similarity validators.

The top-100 set is a baseline, not the endpoint. The next research pass should screen the top 1,000 distinct content hashes and sample for source diversity and missing specialist coverage, stopping category review at evidence saturation.

Generate a metadata-only review queue without adding raw source text to the repository:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-research.txt
.venv/bin/python scripts/export_expansion_candidates.py --limit 1000
```

## License and source rights

The original material in this repository is licensed under Apache-2.0. Linked source repositories retain their own licenses and ownership. A ledger entry is attribution and research provenance, not a claim that the corresponding source material is incorporated or relicensed here.
