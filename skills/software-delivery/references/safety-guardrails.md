# Safety guardrails

## Guard the actual hazard

Use a durable policy hook or wrapper when a repeated developer operation can
irreversibly discard work, publish externally, or mutate a protected target.
Match the hazardous operation narrowly. Broad string blocks are easy to evade
and can also prevent legitimate read-only work.

## Choose scope deliberately

Decide whether the policy belongs to one repository, one workspace, or the
operator's whole environment. Preserve existing policy entries and document
who owns exceptions. A local project must not silently install a global rule.

## Verify both directions

Exercise a representative blocked operation and a nearby allowed operation.
Confirm the failure is clear before the side effect begins, and that the user
has a documented path to change the policy. A guardrail supplements—not
replaces—authorization checks, review, backups, and branch protection.
