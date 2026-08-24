# Expected decisions

- Separate ticket reads, comment creation, and status changes.
- Use stable ticket identifiers rather than free-form search results for writes.
- Keep comment drafting separate from publishing.
- Require explicit transition targets and preserve authorization checks.
- Make retries safe with idempotency keys or state inspection.
- Return actionable partial-success and conflict errors.
- Test non-triggers, ambiguous targets, unauthorized writes, duplicate retries, and stale status.
