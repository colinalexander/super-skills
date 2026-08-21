# API and contracts

## Model resources and operations

Use stable domain language. Choose identifiers, representations, and operations that remain meaningful across implementation changes. Use action endpoints when a domain command is clearer than pretending every behavior is CRUD.

## Specify behavior

Define request validation, authentication, authorization, status/error semantics, pagination, filtering, sorting, idempotency, concurrency control, rate limits, and versioning. Provide machine-readable error codes and safe human context.

## Protect boundaries

Validate untrusted data at ingress and enforce authorization on the server. Do not rely on a client hiding controls. Avoid returning secrets, internal stack traces, or persistence fields merely because they are convenient.

## Manage evolution

Prefer additive compatible changes. Treat removals and semantic reinterpretations as migrations with telemetry and a deprecation window. Keep generated clients and documentation derived from the same contract when possible.

## Integrate resiliently

Set explicit timeouts, retry only safe/transient operations, and bound retry amplification. Verify webhook signatures, deduplicate deliveries, and retain enough correlation data to diagnose failures without logging sensitive payloads.
