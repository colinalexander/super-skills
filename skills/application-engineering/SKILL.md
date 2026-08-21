---
name: application-engineering
description: Design or implement application architecture across APIs, components, runtimes, frameworks, and persistence. Use for FastAPI, Django, Python, Node.js, React, Next.js, React Native, Postgres, Supabase, database design, and related engineering decisions; use another skill for delivery process or visual direction when those are primary.
---

# Application Engineering

Choose architecture from product contracts, data ownership, and operational constraints. Framework idioms refine the design; they do not replace it.

## Establish the system contract

Identify users, critical journeys, trust boundaries, data lifecycle, availability and latency expectations, deployment environment, and compatibility commitments. Inspect the existing architecture and authoritative documentation before proposing version-sensitive APIs.

Route to the relevant reference:

- system shape, module ownership, and frontend composition: [architecture.md](references/architecture.md);
- HTTP/API contracts and integrations: [api-and-contracts.md](references/api-and-contracts.md);
- schemas, queries, transactions, migrations, and hosted Postgres: [data-and-persistence.md](references/data-and-persistence.md);
- Python, Node, FastAPI, Django, React, Next.js, or React Native details: [runtime-and-frameworks.md](references/runtime-and-frameworks.md).

## Design boundaries first

1. Assign ownership of state and invariants.
2. Define contracts between modules, processes, clients, and services.
3. Model failure, cancellation, retries, idempotency, and partial success.
4. Choose synchronous, asynchronous, local, remote, cached, or persisted execution from measured needs.
5. Expose observability at boundaries where causes can be distinguished.
6. Add abstraction only after identifying real variation or replacement pressure.

## Implement in context

Follow repository conventions and supported framework primitives. Keep validation, authorization, and business invariants on trusted boundaries. Avoid leaking persistence models directly into long-lived external contracts. Make client/server and runtime boundaries explicit.

## Verify the architecture

Test the most important contract at its actual boundary. Exercise invalid input, permission failures, concurrency or retry behavior, migrations, and compatibility where relevant. Measure performance before applying generic optimization advice.

Document consequential decisions and rejected alternatives. Flag any framework guidance that still requires confirmation against the installed version.
