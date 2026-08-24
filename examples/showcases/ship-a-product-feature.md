# Showcase: ship a product feature

## Scenario

Add a reservation-management view to the inventory system in the focused application-engineering example. Operators must see active, expiring, confirmed, and released reservations and safely release one reservation.

## Skill composition

1. **`application-engineering` owns the contract:** reservation states, authorization, concurrency, idempotency, and release semantics.
2. **`interface-design` owns the experience:** information hierarchy, status presentation, confirmation, responsive behavior, accessibility, and error states.
3. **`software-delivery` owns the change workflow:** repository inspection, bounded implementation, behavior-level tests, diff review, and completion evidence.

No skill inherits another skill's authority. The architecture contract precedes UI assumptions; the delivery process verifies both.

## Deliverables

- API and state-transition contract
- Responsive operator interface
- Tests for authorized release, stale state, duplicate requests, and failure recovery
- Rendered desktop/narrow evidence and exact test commands
- Short decision record and remaining risks

## Acceptance

The result must not release the wrong reservation, conceal stale state, rely on color alone, or claim completion without boundary tests and rendered evidence.

This is a showcase specification, not a completed comparative run.
