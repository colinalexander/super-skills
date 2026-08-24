# Connected-service automation: mocked file share

This example plans and records a safe mutation across a mocked cloud-drive and messaging workspace.

- **Trigger:** selecting the exact account, file, recipient, permission, message, and verification state is primary.
- **Non-trigger:** designing a new drive integration belongs to `application-engineering` and `agent-tooling-and-orchestration`.
- **Fixture:** [`fixture/workspace.json`](fixture/workspace.json).
- **Reference artifacts:** [`reference-output/mutation-plan.md`](reference-output/mutation-plan.md) and [`reference-output/receipt.json`](reference-output/receipt.json).
- **Verification:** the fixture is read-only; compare the proposed operation and receipt with its stable identifiers and least-privilege boundary.
