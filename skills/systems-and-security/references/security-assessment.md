# Security assessment

## Confirm authorization and scope

Record the authorized systems, identities, methods, time window, data-handling limits, and stop conditions. Begin with passive or read-only inspection. Do not test adjacent assets discovered during assessment unless they are explicitly added to scope.

## Build a threat-informed inventory

Identify assets, trust boundaries, exposed interfaces, identities, dependencies, secrets, and security controls. Map plausible attacker capabilities to abuse paths. Tool findings are leads until verified in context.

Include software and build dependencies, package provenance, CI/CD identities, artifact signing, deployment channels, and cloud shared-responsibility boundaries. Check whether exceptional states fail open, bypass authorization, leak information, or leave partially applied security decisions.

## Validate safely

Prefer configuration review, version and dependency analysis, static inspection, and non-destructive proof. Avoid payloads that modify data, create persistence, degrade availability, or access real sensitive records. Stop if impact exceeds the agreed method.

Cover the applicable risk classes—access control, authentication, injection, insecure design, misconfiguration, cryptography, integrity and supply chain, logging/alerting, and exceptional-condition handling—without treating a generic checklist as evidence that every class applies.

## Triage findings

For each finding, state affected asset, prerequisite, evidence, impact, likelihood, existing controls, confidence, and remediation. Distinguish exploitable defects from best-practice gaps and scanner noise. Avoid severity claims unsupported by the actual deployment.

## Close responsibly

Remove temporary test artifacts, protect evidence, and report urgent exposure through the agreed channel. Provide verification steps for remediation and note residual risk. Never publish sensitive exploit details or credentials in a general report.
