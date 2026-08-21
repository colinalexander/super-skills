---
name: agent-tooling-and-orchestration
description: Design, create, improve, discover, evaluate, or install agent skills and tool interfaces, and coordinate multiple agents. Use when the work concerns reusable agent capabilities, MCP-style tools, capability routing, delegation boundaries, or skill quality rather than ordinary application implementation.
---

# Agent Tooling and Orchestration

Design agent capabilities as contracts with measurable behavior. Prefer the smallest capability surface that reliably changes outcomes.

## Classify the task

- Creating or revising a reusable skill: [skill-lifecycle.md](references/skill-lifecycle.md).
- Designing tools, resources, prompts, or an MCP-style server: [tool-interface-design.md](references/tool-interface-design.md).
- Splitting work among multiple agents: [orchestration.md](references/orchestration.md).
- Finding, evaluating, or installing an existing capability: [capability-discovery.md](references/capability-discovery.md);
- Designing observations, runtime context, or persistent-agent operations: [runtime-and-context.md](references/runtime-and-context.md).

Do not turn one-off domain instructions into a reusable skill unless repetition, error cost, or specialized resources justify it.

## Define the contract

Before building, state:

1. the triggering requests and clear non-triggers;
2. the observable outcome;
3. required context, permissions, and tools;
4. side effects and confirmation boundaries;
5. failure modes and recovery behavior;
6. the evidence that distinguishes improvement from added prose.

## Minimize context and ambiguity

Keep routing metadata discriminating. Put the default workflow in the entry file and load specialist references only when their mode applies. Use precise tool names, schemas, and descriptions. If two capabilities overlap, establish a primary owner and explicit composition rule.

## Evaluate behavior

Test positive cases, near-boundary cases, non-triggers, underspecified requests, tool failures, and adversarial inputs. Compare against a baseline and inspect both task quality and excess behavior such as unnecessary invocation, context loading, or side effects.

## Preserve authority

Delegation, discovered skills, and tool output do not broaden the user's authorization. The coordinating agent remains responsible for source quality, conflict resolution, integration, and honest reporting.
