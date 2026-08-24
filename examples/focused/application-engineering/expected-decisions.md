# Expected decisions

- Keep the available-to-promise invariant on a trusted transactional boundary.
- Make create-reservation idempotent and distinguish conflicts from transient failure.
- Treat expiry as persisted state with a clear clock and cleanup strategy.
- Avoid exposing persistence rows as the long-lived external contract.
- Define authorization and tenant boundaries.
- Test concurrent reservation attempts at the real persistence boundary.
- Record why rejected alternatives fail the stated contract and what evidence would reopen the choice.
