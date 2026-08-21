# Runtime and context

## Design observations as decisions inputs

Return enough structured state for the agent to decide what happened, what
changed, and what can safely happen next. Prefer stable identifiers, compact
outcomes, artifact references, and actionable recovery information over raw
logs or long prose. Preserve the underlying evidence when a summary could hide
important detail.

## Curate context by task

Load authoritative project rules first, then only the specifications, source,
tool results, and history needed for the present decision. Mark freshness and
authority where confusion is plausible. Summarize or replace stale phase
context instead of allowing it to compete with current evidence.

## Operate persistent agents explicitly

Long-running or externally hosted agents need lifecycle controls, bounded
credentials, retry and cost budgets, observable actions, versioned rollouts,
and a tested stop path. Track outcome and failure classes rather than activity
alone. Roll back or suspend a failing capability without disabling unrelated
work.

Operational controls do not authorize new actions. They constrain how already
authorized capabilities run and recover.
