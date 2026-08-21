# Software delivery synthesis matrix

Evidence: 19 baseline hashes plus 1 retained top-1,000 expansion hash.

Evidence labels: `verification-before-completion`, `webapp-testing`, `systematic-debugging`, `receiving-code-review`, `test-driven-development`, `diagnose`, `finishing-a-development-branch`, `using-git-worktrees`, `executing-plans`, `writing-plans`, `requesting-code-review`, `e2e-testing`, `caveman-review`.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Planning | Define outcomes, dependencies, and current-state validation | Plans scale to uncertainty and risk; one-step work does not require ceremony |
| Debugging | Reproduce, trace boundaries, test hypotheses, confirm cause | Retries, timeouts, and silenced errors are not presumed fixes |
| Testing | Test at the lowest faithful behavior boundary | Test-first is preferred for reproducible behavior but not imposed where no reliable oracle exists yet |
| Browser/E2E | Reconnoiter the live surface, use stable semantic selectors, synchronize on observable state, and retain failure artifacts | Browser automation validates critical journeys; it does not replace lower-level edge tests |
| Review | Prioritize correctness, security, state, contracts, and evidence | Feedback is verified, neither dismissed nor implemented mechanically |
| Review expression | Findings remain concise and labeled when useful | A persistent compressed persona belongs to `reasoning-modes`, not the delivery invariant |
| Completion | Obtain current command and behavior evidence immediately before claims | Stale or partial checks cannot support “done” |
| Isolation | Parallelize only independent work and integrate explicitly | Worktrees and agents are tools, not mandatory workflow rituals |
| Omission repair | Preserve unrelated user work and report skipped validation | A clean workspace may never be manufactured destructively |
| Durable guardrails | Place narrow policy checks before repeated destructive or publishing operations | Guardrails require project/global scoping and allowed-path tests; they do not replace authorization |

Resulting modes: planning/execution, testing/debugging, browser/E2E, review/completion, and parallelism/isolation.
