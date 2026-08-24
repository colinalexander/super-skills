# Agent tooling: support-ticket tool contract

This example designs a small tool surface for an agent that reads, comments on, and changes the status of support tickets.

- **Trigger:** reusable agent tools, side-effect boundaries, schemas, and evaluation are the primary work.
- **Non-trigger:** implementing an ordinary support UI belongs to application and interface engineering.
- **Fixture:** [`fixture/requirements.md`](fixture/requirements.md).
- **Reference artifact:** [`reference-output/tool-contract.yaml`](reference-output/tool-contract.yaml).
- **Verification:** inspect whether reads and writes are distinct, identifiers are stable, authority is explicit, and errors are recoverable.
