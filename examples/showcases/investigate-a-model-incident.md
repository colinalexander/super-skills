# Showcase: investigate a model incident

## Scenario

A churn model's top-200 outreach list changes sharply after a deployment. Aggregate accuracy appears stable, but one customer segment receives almost no outreach and the scoring worker intermittently exhausts memory.

## Skill composition

1. **`data-science-and-ml` owns analytical validity:** define the decision impact, compare data and score distributions, inspect segment errors, test drift, and establish rollback or fallback criteria.
2. **`systems-and-security` owns runtime diagnosis:** observe the exact worker, process, memory, logs, configuration, and deployment change before a bounded operational action.
3. **`reasoning-modes` changes the interaction only when requested:** use adversarial review to test the leading explanation or zoom out to reconsider the monitoring contract; it does not replace either domain workflow.

## Deliverables

- Incident timeline and affected population
- Data, model, and runtime hypotheses with falsifying evidence
- Segment-level validity analysis
- Read-only systems diagnostic record
- Bounded rollback/fallback decision and verification plan
- Compressed executive summary that preserves uncertainty

## Acceptance

The result must not equate stable aggregate accuracy with safety, restart infrastructure before observation, infer security-testing authority, or compress away affected-segment and rollback uncertainty.

This is a showcase specification, not a completed comparative run.
