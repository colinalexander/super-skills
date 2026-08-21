# Architecture

## Decompose by responsibility

Create modules around stable business capabilities and data ownership, not arbitrary technical layers alone. Keep dependencies directional and make side effects visible. A shared abstraction should reduce meaningful duplication without coupling unrelated change rates.

## Stabilize domain language

Name concepts, state transitions, and invariants in the language used by the
people who own the domain. Test ambiguous terms against concrete scenarios,
then align code, APIs, persistence, and documentation around the resolved
meaning. A glossary is useful only when it exposes distinctions and remains
consistent with actual behavior.

## Place state deliberately

Identify the source of truth, writers, readers, consistency requirement, retention, and recovery path for each state class. Distinguish durable domain state from cache, view state, workflow state, and derived data.

## Compose frontend systems

Prefer explicit component composition and narrow interfaces. Keep server-only work, client interaction, and data fetching in their appropriate runtime boundaries. Avoid boolean-prop combinations that create hidden state machines; use named variants or composed children when structures differ.

## Design for failure

Specify timeouts, cancellation, retry eligibility, idempotency keys, and degraded behavior. Retries belong where the operation is safe and the caller has enough context. Use backpressure or queues when production rate can exceed consumption.

## Earn distribution

Start with the simplest deployment topology that meets the contract. Split processes or services when independent scaling, isolation, ownership, regulatory boundaries, or deployment cadence justify the operational cost.

## Define the deployment unit

Package only the runtime and assets the process needs. Inject environment
configuration and secrets at launch, run with the least required privilege,
and make startup, readiness, liveness, resource limits, and graceful shutdown
observable. Development convenience such as host mounts or broad ports must
not silently become the production boundary.

## Record consequential choices

For a choice that is expensive to reverse or likely to be questioned later,
record the decision condition, constraints, viable alternatives, material
tradeoffs, and selected rationale. Include the evidence or future signal that
would justify revisiting it. A decision record preserves reasoning; it does not
turn a preference into a permanent rule.
