# Tool interface design

## Start from user outcomes

Define user-facing jobs and map each to the smallest safe operation. Prefer a coherent set of task-level tools over exposing every internal endpoint or one giant tool with many unrelated modes.

## Write contracts for models

Tool names should reveal the action and object. Descriptions should distinguish similar operations. Schemas should use constrained types, explicit required fields, stable identifiers, and understandable defaults. Return compact structured data plus actionable error information.

Separate read and write operations. Mark side effects, idempotency, cost, latency, and authentication requirements. Require confirmation where consequences are difficult to reverse or external communication is involved.

Treat the response as part of the action contract. Return stable identifiers,
a compact outcome, changed state, relevant artifacts, and specific recovery
choices. Do not make an agent infer success or the next safe action from an
undifferentiated log stream.

## Design resources and prompts deliberately

Use resources for stable contextual data and prompts for reusable user-facing workflows. Do not hide required inputs in prose when they can be represented structurally.

## Test failure paths

Cover invalid input, missing authorization, partial success, rate limits, stale identifiers, timeouts, pagination, and retries. Avoid returning raw internal errors or secrets. Make recovery information specific enough for the agent to choose a safe next step.
