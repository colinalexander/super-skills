---
name: data-science-and-ml
description: Design, analyze, train, evaluate, and operationalize statistical or machine-learning systems. Use for data quality, experiments, causal inference, predictive modeling, deep learning, computer vision, fine-tuning, distributed training, or model monitoring; use application engineering for ordinary product architecture without an analytical or learned-model decision.
---

# Data Science and Machine Learning

Make the decision, estimand, data-generating process, and validation boundary explicit before selecting a method or model. Analytical validity outranks algorithm novelty.

## Frame the problem

Define the decision or product behavior, unit of analysis, target or estimand, population, time horizon, cost of errors, operational constraints, and baseline. Determine whether the task is descriptive, predictive, causal, ranking, generation, detection, or optimization.

Load the relevant reference:

- data quality, statistics, experiments, and causal questions: [data-and-experiments.md](references/data-and-experiments.md);
- features, models, validation, and error analysis: [modeling-and-evaluation.md](references/modeling-and-evaluation.md);
- reproducible training, accelerators, fine-tuning, and distributed scale: [training-and-scale.md](references/training-and-scale.md);
- serving, monitoring, governance, and retraining: [deployment-and-monitoring.md](references/deployment-and-monitoring.md).

## Build an evidence chain

1. Trace data provenance, collection, exclusions, labels, and permissions.
2. Detect leakage, confounding, selection effects, missingness, imbalance, and temporal drift.
3. Establish a simple, credible baseline and a validation design that matches deployment.
4. Choose metrics from decision costs and inspect performance across relevant slices.
5. Track data, code, configuration, environment, randomness, and artifacts for reproducibility.
6. Perform error analysis before adding complexity.
7. Define deployment, fallback, monitoring, and retirement conditions.

Report uncertainty and limitations. Do not treat correlation as causation, test-set iteration as validation, or benchmark gains as production value.

## Respect boundaries

`application-engineering` owns surrounding APIs and product architecture. `software-delivery` owns the code-change workflow. This skill owns the validity and behavior of analytical and learned systems. Check current primary documentation before using version-sensitive framework, accelerator, or model APIs.
