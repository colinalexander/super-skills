# Testing and debugging

## Diagnose systematically

1. Capture the exact symptom, environment, inputs, and expected behavior.
2. Reproduce it with the narrowest reliable command or case.
3. Trace the failing path and collect evidence at boundaries.
4. Form a falsifiable hypothesis.
5. Change one causal variable or add one discriminating observation.
6. Confirm the cause before implementing the durable repair.
7. Re-run the reproduction and relevant regression checks.

Do not confuse a correlated change, silenced error, retry, or broadened timeout with a root-cause fix.

## Choose test level by contract

- Use a unit test for local logic and edge conditions.
- Use a component or integration test for boundaries, serialization, persistence, or framework behavior.
- Use end-to-end testing for critical journeys and cross-system confidence.

Prefer the lowest level that faithfully covers the regression, then add a higher-level check only when the integration risk justifies it.

## Use test-first work when it adds signal

For behavior changes and reproducible defects, write or identify a failing check before the repair when practical. For exploratory spikes, generated artifacts, or inaccessible external failures, first create the smallest reliable oracle. Do not write tests that merely duplicate implementation details.

## Handle flaky or environmental failures

Repeat selectively, compare environments, inspect timing and shared state, and record whether the failure is deterministic. Quarantine only with an owner and follow-up; never treat “passed once” as evidence that flakiness is resolved.
