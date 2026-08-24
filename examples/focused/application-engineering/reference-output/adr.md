# ADR: transactional reservation owner

## Decision

Store inventory and reservations in one transactional service backed by a relational database. Lock or atomically update the merchant/product inventory row while creating a reservation. Persist expiry timestamps using the service/database clock. Require an idempotency key scoped to merchant and operation.

## Consequences

- The service can enforce `confirmed + active reservations <= inventory` at one boundary.
- Confirmation, release, and expiry are explicit state transitions.
- Cleanup may be asynchronous, but availability calculations must ignore expired reservations transactionally.
- Hot products may create row contention and require measured partitioning or a different reservation algorithm.

## Rejected alternatives

- Client-side inventory checks cannot enforce concurrency.
- A cache-only lock lacks the durable state needed for confirmation and audit.
- Eventual reconciliation after accepting reservations violates the no-oversell contract.

## Reconsider when

Measured contention prevents the stated throughput or multi-region latency becomes a committed requirement.
