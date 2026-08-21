# Safe mutations

## Classify the side effect

Reads are generally reversible; sends, shares, edits, moves, playback changes, and creations affect external state; deletions, permission removal, bulk actions, and overwrites may be difficult to recover. Increase confirmation and verification in proportion to impact, ambiguity, and audience.

Before mutation, capture enough current state to detect races and explain recovery. Prefer a dry run, draft, preview, trash operation, conditional update, or service-native undo when available.

## Handle failure without duplication

Use idempotency keys when supported. Otherwise search for the intended result before retrying a timed-out creation or send. Respect rate-limit and retry guidance; use bounded backoff and do not retry authorization or validation failures unchanged.

For batches, define the target set first, process in bounded units, and retain per-item results. Report partial completion precisely. After any mutation, read back the affected object or inspect authoritative status rather than assuming a successful command produced the intended state.
