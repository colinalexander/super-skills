# Connected-service automation synthesis matrix

Evidence: five retained top-1,000 hashes spanning messaging, notes, media playback, cloud files, and permission management. A second Apple Notes variant was reviewed without adding a distinct decision rule.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Capability discovery | Verify available tool, platform, version, auth state, and supported action | Recalled command syntax yields to live help or schema |
| Identity | Resolve service, account, tenant, workspace, device, recipient, channel, timing, and resource explicitly | Ambiguity is a hard stop before a write; tool availability neither implies authority over reachable targets nor justifies service or target substitution |
| Side effects | Distinguish reads, drafts, sends, mutations, sharing, deletion, and device changes | Confirmation scales with ambiguity, external visibility, and recoverability |
| Permissions | Apply the narrowest role to the exact collaborator and object | Successful requests are followed by an authoritative access check |
| Records | Preserve content, hierarchy, identity, and recovery behavior | Search and listings are treated as partial unless completeness is established |
| Reliability | Use state checks, idempotency, bounded retries, pagination, and per-item batch results | Timeouts do not justify blind repetition of sends or creations |
| Verification | Read back the resulting service state and report partial success | Command exit status alone is not completion evidence |

Resulting modes: account/capability discovery, safe state mutation, messaging/sharing, and record/media operation.
