---
name: connected-service-automation
description: Operate user-authorized messaging, notes, media, cloud storage, sharing, and similar connected services through available tools or CLIs. Use when the task is to inspect or change state in an external personal or workplace service; use another skill to design a new integration or agent tool.
---

# Connected-Service Automation

Operate external services as stateful systems with real users, accounts, permissions, and side effects. Accuracy includes choosing the right account and target, limiting the mutation, and verifying the result.

## Establish authority and state

Confirm the requested service, account or workspace, target object or recipient, desired end state, and available capability. Inspect current state before changing it when that state affects safety or correctness. Never expose credentials or infer permission from tool availability alone.

Load the relevant reference:

- accounts, capability discovery, and target resolution: [accounts-and-capabilities.md](references/accounts-and-capabilities.md);
- mutation safety, retries, and verification: [safe-mutations.md](references/safe-mutations.md);
- messages, recipients, collaborators, and permissions: [messaging-and-sharing.md](references/messaging-and-sharing.md);
- notes, files, folders, playlists, playback, and other records: [records-and-media.md](references/records-and-media.md).

## Execute the smallest valid operation

1. Resolve human labels to stable identifiers when the service supports them.
2. Distinguish read, draft, send, create, edit, move, share, delete, and playback actions.
3. Preview or confirm high-impact, irreversible, externally visible, or ambiguous mutations.
4. Use the narrowest permission and smallest target set that satisfies the request.
5. Make retries safe with idempotency, deduplication, or a state check.
6. Verify the resulting service state and report any partial success.

Respect pagination, rate limits, concurrency, service-specific formatting, and authentication boundaries. Do not silently switch accounts, recipients, devices, folders, or workspaces.

## Preserve the boundary

`agent-tooling-and-orchestration` owns reusable tool design. `application-engineering` owns implementation of integrations and APIs. This skill owns safe operation of an already connected service on the user's behalf.
