# Orchestration

## Use delegation for topology, not theater

Delegate when tasks are independent, context can be bounded, and parallel or specialist work materially improves the outcome. Keep work local when coordination would cost more than execution.

## Write bounded assignments

Each assignment should specify objective, inputs, allowed scope, required evidence, output contract, and known dependencies. Pass only the context needed to act. Do not ask a worker to infer permissions or resolve a cross-cutting product decision alone.

## Preserve ownership

The coordinator owns decomposition, conflict resolution, integration, and final validation. Agent conclusions are evidence to inspect, not automatically authoritative results. Avoid simultaneous writes to the same files or mutable external object.

## Synchronize at meaningful boundaries

Collect results when a dependency is ready or an integration decision is required. Compare contradictions explicitly. Re-run combined checks after integrating independently produced work.

## Bound failure

Set a retry or escalation policy. Stop spawning work when the same missing input blocks all branches. Cancel obsolete assignments when new evidence changes the plan.
