# Deployment and monitoring

## Define the serving contract

Specify inputs, outputs, preprocessing, model and feature versions, latency and resource budgets, concurrency, failure behavior, fallback, privacy, and human oversight. Keep training-serving transformations aligned and test the packaged artifact in a production-like path.

Roll out through offline checks, shadow or replay evaluation where appropriate, a bounded canary, and explicit promotion criteria. Separate model quality from pipeline availability and product impact.

## Observe changing behavior

Monitor input validity, missing features, distribution shift, prediction or generation quality, calibration where applicable, slice performance, latency, resource use, failures, and downstream outcomes. Define alert thresholds and owners before launch.

Ground-truth delay can make immediate quality monitoring impossible; use proxies cautiously and backfill outcome evaluation when labels arrive. Log enough to investigate behavior without retaining unnecessary sensitive data.

Define retraining triggers, approval and validation gates, rollback, audit history, and retirement conditions. Automated retraining must not silently promote a model solely because a pipeline completed.
