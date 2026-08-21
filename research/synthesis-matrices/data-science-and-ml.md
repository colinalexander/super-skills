# Data science and machine learning synthesis matrix

Evidence: five retained top-1,000 hashes spanning statistical analysis, reproducible PyTorch, computer vision, distributed training, and parameter-efficient fine-tuning.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Problem framing | Define the decision, estimand or target, population, horizon, and error costs | Technique selection follows the analytical question |
| Data | Trace collection, labels, permissions, exclusions, missingness, and leakage | A large dataset does not cure a biased data-generating process |
| Experiments | Predefine assignment, exposure, outcome, guardrails, and analysis | Significance is reported with effect size, uncertainty, and practical value |
| Validation | Use deployment-shaped splits, simple baselines, isolated tests, and slice analysis | Aggregate benchmark gains do not establish production value |
| Modeling | Diagnose errors and data before adding complexity | Specialist model guidance remains contextual rather than universal |
| Reproducibility | Track data, transformations, code, environment, randomness, and artifacts | Determinism claims state platform and performance limitations |
| Scale | Select precision, sharding, offload, quantization, or adapters from measured bottlenecks | Distributed and fine-tuning methods require recovery and quality validation |
| Operations | Define serving, rollout, monitoring, fallback, retraining, and retirement | Pipeline completion cannot automatically authorize model promotion |

Resulting modes: data and experiments, modeling and evaluation, training and scale, and deployment and monitoring.
