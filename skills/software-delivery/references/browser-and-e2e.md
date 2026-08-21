# Browser and end-to-end testing

## Choose E2E for system journeys

Use browser-level tests for critical workflows, routing, authentication boundaries, browser integration, and confidence across components. Keep most edge-case logic at lower test levels so the E2E suite remains focused and diagnosable.

## Reconnoiter before automating

Confirm how the application starts, whether a server is already running, the test environment and accounts, and which selectors and routes are stable. Inspect the rendered page before inventing selectors. Prefer roles, accessible names, labels, and deliberate test identifiers over fragile DOM position or styling hooks.

## Synchronize on observable state

Wait for a specific user-visible or network state instead of fixed delays. Keep each test independent, control data setup, and clean up only what the test owns. Treat retries as a signal-gathering aid, not proof that flakiness is solved.

## Preserve failure evidence

Capture the relevant trace, screenshot, video, console, and network information on failure while protecting secrets and personal data. Report the journey, environment, first failed expectation, and artifact locations.

## Validate representative conditions

Cover primary success and recovery paths, meaningful viewport/input variants, and high-risk integrations. Run focused tests while iterating, then the appropriate suite in the same deployment topology used for the claim. Always close owned browser and server resources.
