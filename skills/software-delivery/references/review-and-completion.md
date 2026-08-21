# Review and completion

## Review against risk

Understand the requested behavior and inspect the actual diff in context. Prioritize:

1. correctness and data loss;
2. security and permission boundaries;
3. concurrency, state, and failure handling;
4. contract and compatibility changes;
5. missing or misleading tests;
6. maintainability that has concrete future cost.

Make findings specific, actionable, and tied to a file, path, or observable scenario. Separate blockers from suggestions.

## Receive feedback analytically

Translate each comment into a technical claim. Verify it against code, tests, and constraints. Implement correct feedback, explain evidence when declining, and ask only where intent is genuinely ambiguous. Do not perform agreement as a substitute for evaluation.

## Completion gate

Immediately before claiming success:

- run the relevant current command;
- inspect its exit status and output;
- inspect the final diff and workspace state;
- exercise the repaired or added behavior when tests do not fully cover it;
- report any skipped checks or known limitations.

Words such as “done,” “fixed,” “passing,” and “ready” must be backed by evidence from the current state.

## Finish the branch without assuming publication

After validation, identify the integration base and report the branch, worktree, and diff state. Merging, pushing, opening a pull request, discarding a branch, and deleting a worktree are distinct choices with different side effects; perform only the option the user requested or approved. Never clean up a workspace you did not create merely because its branch appears finished.
