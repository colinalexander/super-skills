---
name: software-delivery
description: Plan, implement, diagnose, test, review, and finish software changes with evidence. Use when the main challenge is changing code safely, isolating work, resolving a defect, responding to review, or proving completion; combine with a domain skill for framework or product-specific decisions.
---

# Software Delivery

Move from an explicit contract to verified evidence. Scale ceremony to risk, but never replace proof with confidence.

## Read the operating context

Inspect repository instructions, current changes, relevant code, tests, and available commands. Preserve user work. Identify the requested outcome, non-goals, authority boundaries, and completion evidence.

Choose the primary mode:

- planning or executing a multi-step change: [planning-and-execution.md](references/planning-and-execution.md);
- diagnosing a failure or choosing tests: [testing-and-debugging.md](references/testing-and-debugging.md);
- testing a web journey or browser behavior: [browser-and-e2e.md](references/browser-and-e2e.md);
- reviewing work, addressing feedback, or finishing: [review-and-completion.md](references/review-and-completion.md);
- isolating branches or coordinating independent work: [parallelism-and-isolation.md](references/parallelism-and-isolation.md).
- installing durable protections around destructive or publishing operations: [safety-guardrails.md](references/safety-guardrails.md).

## Deliver the smallest complete change

1. Restate the observable outcome and how it will be checked.
2. Inspect before editing; distinguish facts from hypotheses.
3. Choose the smallest coherent change that satisfies the contract.
4. Add or adjust tests at the behavior boundary most likely to regress.
5. Implement without overwriting unrelated work.
6. Run focused checks, then broader checks proportional to blast radius.
7. Inspect the diff and runtime behavior for unintended changes.
8. Report what changed, the exact evidence obtained, and remaining risk.

## Apply hard gates

- Do not claim a bug is fixed without reproducing the original failure or proving the repaired behavior through an equivalent test.
- Do not claim completion based on stale, partial, or unrelated checks.
- Do not broaden scope to clean up adjacent code unless required for correctness or explicitly authorized.
- Do not accept review feedback mechanically; verify that it is correct in the repository's context.
- Do not discard, reset, or overwrite user changes to create a clean workspace.

When a required check cannot run, describe the constraint and provide the strongest available substitute without presenting it as equivalent.
