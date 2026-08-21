# Parallelism and isolation

## Decide whether work is independent

Parallelize only when tasks have clear outputs, minimal shared state, and no unresolved dependency on one another. If two tasks will edit the same files or one result changes the other's design, sequence them.

## Isolate changes safely

Use the repository's preferred branch or worktree convention. Base new isolated work on the correct integration branch, verify the target path, and avoid destructive cleanup. Record which workspace owns each change.

## Define bounded assignments

Each parallel assignment needs a concrete objective, relevant context, allowed scope, expected evidence, and a return format. The coordinator remains responsible for integrating results and resolving contradictions.

## Integrate deliberately

Review each result in the current repository state, run combined checks, and inspect interactions that were impossible to observe in isolation. Parallel completion does not imply integrated correctness.
