# Modeling and evaluation

## Establish a credible baseline

Start with a rule, historical rate, simple statistical model, or current production system. Split data by the boundary the model will face—often time, entity, site, or geography rather than a random row split. Keep the final test set isolated from model and threshold selection.

Choose metrics from operational error costs. Calibration, ranking, threshold behavior, latency, memory, and slice performance may matter more than a single aggregate score. Compare uncertainty, not just point estimates.

## Diagnose before increasing complexity

Inspect label quality, feature leakage, residuals, confusion patterns, difficult slices, outliers, and errors under distribution shift. Use ablations to determine which data or components create value. Tune against validation data with a recorded search budget; never tune on the test set.

For vision and other perception systems, include capture conditions, annotation policy, geometry where relevant, and edge deployment constraints. For generative systems, define task-specific quality, safety, factuality, robustness, and human-review protocols rather than relying on one automatic metric.

Produce a model card or equivalent record covering intended use, excluded use, data, evaluation, limitations, and known failure modes.
