# Systems and security: bounded Linux service diagnosis

This example provides terminal evidence from a service that stopped accepting connections after a deploy.

- **Trigger:** Linux service, process, socket, configuration, and least-disruptive recovery are central.
- **Non-trigger:** routine administration does not authorize a vulnerability scan.
- **Fixture:** [`fixture/evidence.txt`](fixture/evidence.txt).
- **Reference artifact:** [`reference-output/diagnostic-plan.md`](reference-output/diagnostic-plan.md).
- **Verification:** derive a specific hypothesis from read-only evidence, preview a narrow repair, and verify service and network state independently.

The evidence is synthetic. Do not run commands against a real host for this example.
