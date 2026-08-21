# Training and scale

## Reproduce the run

Track dataset identity and splits, preprocessing, code revision, environment, configuration, seeds, hardware, checkpoints, and metrics. Deterministic execution may have performance costs and platform limits; state the reproducibility level actually achieved.

Validate the single-device training loop before distributing it. Confirm tensor shapes, loss behavior, gradient flow, evaluation mode, checkpoint restoration, and a small overfit test. Profile memory, compute, input, and communication before choosing an optimization.

## Choose scale from the bottleneck

Use mixed precision, accumulation, activation checkpointing, sharding, offload, quantization, or distributed data/model parallelism only when their tradeoffs match measured constraints. Define checkpoint format, world-size portability, failure recovery, and numerical validation.

For parameter-efficient fine-tuning, compare against prompting, retrieval, and full fine-tuning. Specify base model, data rights and quality, adapter method, target modules, evaluation, merge or multi-adapter serving strategy, and rollback. Reduced trainable parameters do not remove data, safety, or evaluation obligations.

Verify all version-sensitive framework and accelerator APIs against primary documentation for the installed environment.
