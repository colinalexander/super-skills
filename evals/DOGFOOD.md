# Dogfood smoke report

This report records the first installed-host smoke pass. It answers a narrow question: can each active skill be discovered and used on one representative prompt, while its closest category boundary avoids the wrong behavior?

It is not a benchmark. The run has no baseline arm, repeated sampling, blinded grading, matched token budget, or task-quality comparison with source skills. Empty read-only workspaces also prevented implementation cases from exercising real repositories. Results must not be used to claim that Super Skills outperform their sources.

## Environment

- Date: 2026-08-22
- Host: Codex CLI 0.136.0
- Model: `gpt-5.5`; low reasoning for the primary sweep, medium for explicit-invocation follow-ups
- Installation: all 10 skills under `~/.agents/skills`
- Isolation: one fresh ephemeral session and empty read-only working directory per case
- Configuration: `--ignore-user-config --skip-git-repo-check --sandbox read-only`
- Prompts: unchanged representative and boundary cases from `evals/category-specific/*.yaml`

The installed CLI could not run its default GPT-5.6 model because the client was too old, so this report is specific to the pinned runner above. Host framing and tool schemas dominated input-token usage; those counts are not evidence about the suite's discovery-token efficiency and are omitted here.

## Results

| Skill | Representative case | Boundary case | Result |
| --- | --- | --- | --- |
| `agent-tooling-and-orchestration` | automatic route and expected read/write tool separation passed | ordinary code change did not load the skill | pass |
| `application-engineering` | automatic route and inventory concurrency contract passed | visual-direction request routed to interface design | pass |
| `connected-service-automation` | initial run attempted the wrong messaging service; repaired core now stops to resolve service and recipient | OAuth architecture repeat routed to application engineering | pass after repair |
| `data-science-and-ml` | automatic route rejected a p-value-only launch decision | ordinary CRUD request did not load the skill | pass |
| `game-development` | automatic route proposed a small playable loop test | loyalty-dashboard request did not load the skill | pass |
| `interface-design` | automatic route preserved the sober operational brand and dispatcher task | backend endpoint request did not load the skill | pass |
| `marketing-and-growth` | explicit invocation now loads pricing guidance and avoids fabricated prices; automatic selection remained intermittent | visual campaign direction did not load the skill | explicit pass; automatic routing open |
| `reasoning-modes` | automatic route generated distinct mechanisms before ranking | complex pricing request did not load the skill | pass |
| `software-delivery` | automatic route passed; implementation behavior was not scored because the isolated workspace had no project fixture | architecture comparison did not load the skill | routing-only pass |
| `systems-and-security` | explicit invocation produced exact ACL verification; automatic runs loaded the skill but did not consistently follow that safeguard | repeated package-administration case stopped safely when the package and service were unspecified | explicit pass; automatic adherence open |

The boundary result is about the target skill: another appropriate domain or delivery skill may load. One OAuth run loaded both connected-service automation and application engineering before a repeat loaded application engineering alone; this is recorded as routing variance, not hidden as a clean one-shot result.

## Repairs made from the run

1. Pricing tiers, plans, and packages are explicit front-matter triggers for `marketing-and-growth`.
2. Pricing work must load the monetization reference, must not treat a bare strategy request as arbitrary file-edit authority, and must not fabricate numeric prices without commercial evidence.
3. Ambiguous messaging is a hard stop before any write tool; an available service cannot substitute for the requested channel.
4. ACL changes require an independent exact check of principal, access type, rights, inheritance, and propagation on every target.

The installed copies were updated before the repair checks. The repository token records were regenerated after the changes.

## Current gate

The suite is usable through explicit invocation. Automatic routing is promising but not established as reliable across hosts or models. Before a future claim of dependable automatic selection or broad task-quality improvement, run the preregistered comparative protocol with current clients, realistic fixtures, repeated trials, and published outputs.
