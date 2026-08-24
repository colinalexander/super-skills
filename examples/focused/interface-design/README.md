# Interface design: dispatcher dashboard

This example asks the agent to redesign a deliberately weak operations dashboard while preserving the supplied product identity and dispatcher workflow.

- **Trigger:** hierarchy, responsive behavior, interaction states, accessibility, and art direction determine success.
- **Non-trigger:** changing the dispatch API or data model belongs to `application-engineering`.
- **Fixture:** [`fixture/dashboard.html`](fixture/dashboard.html) is a runnable single-file dashboard.
- **Reference artifact:** [`reference-output/decisions.md`](reference-output/decisions.md) records the minimum coherent design decisions; it is not a completed model run.
- **Verification:** render the changed page at desktop and narrow widths, then inspect keyboard flow, focus, contrast, status semantics, overflow, and empty/error states.

Open the fixture directly in a browser. The task permits changes only inside this example directory.
