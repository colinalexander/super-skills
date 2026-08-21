# Data and experiments

## Audit the data-generating process

Document sources, collection rules, units, timestamps, joins, labels, exclusions, consent, and retention. Check schema and range validity, missingness mechanisms, duplication, survivorship, delayed outcomes, selection bias, and target leakage. Preserve a raw immutable layer when feasible and make transformations reproducible.

## Match inference to design

For descriptive work, define denominators, cohorts, and uncertainty. For causal questions, state the treatment, outcome, estimand, assignment mechanism, interference assumptions, and plausible confounders. Prefer randomized assignment when ethical and practical; otherwise explain what assumptions identification requires.

Predefine experiment population, randomization unit, exposure, primary metric, guardrails, power assumptions, duration, and analysis plan. Account for repeated looks, multiple outcomes, noncompliance, attrition, and novelty effects. Statistical significance does not establish material value.

Communicate effect sizes and intervals alongside assumptions. Separate exploratory findings from confirmatory evidence.
