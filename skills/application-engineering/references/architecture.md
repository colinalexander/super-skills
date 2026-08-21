# Architecture

## Decompose by responsibility

Create modules around stable business capabilities and data ownership, not arbitrary technical layers alone. Keep dependencies directional and make side effects visible. A shared abstraction should reduce meaningful duplication without coupling unrelated change rates.

## Place state deliberately

Identify the source of truth, writers, readers, consistency requirement, retention, and recovery path for each state class. Distinguish durable domain state from cache, view state, workflow state, and derived data.

## Compose frontend systems

Prefer explicit component composition and narrow interfaces. Keep server-only work, client interaction, and data fetching in their appropriate runtime boundaries. Avoid boolean-prop combinations that create hidden state machines; use named variants or composed children when structures differ.

## Design for failure

Specify timeouts, cancellation, retry eligibility, idempotency keys, and degraded behavior. Retries belong where the operation is safe and the caller has enough context. Use backpressure or queues when production rate can exceed consumption.

## Earn distribution

Start with the simplest deployment topology that meets the contract. Split processes or services when independent scaling, isolation, ownership, regulatory boundaries, or deployment cadence justify the operational cost.
