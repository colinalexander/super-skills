# Comparative benchmark protocol

## Status and objective

This document preregisters the comparative design. The repository does not yet
contain benchmark results.

The primary product question is whether a small synthesized suite preserves or
improves task behavior while reducing selection errors and instruction cost
relative to installing the overlapping public source skills from which it was
derived.

## Four fixed arms

Every case is run under these conditions with the same host, model, tool access,
task input, and sampling parameters:

1. **Unskilled:** no source or super-skill is installed.
2. **Highest-ranked source:** one source skill is chosen before execution by
   the mechanical rule below.
3. **Source-suite ceiling:** all 119 retained hashes routed to an active category
   are installed as separate skills from an external reconstructed corpus.
   Exact hashes, not researcher-selected conflict sets, determine membership.
4. **Super suite:** all 10 active independently authored super-skills are installed.

Third-party source text remains outside this repository and is not redistributed
with prompts, traces, or results.

## Preregistered composition rules

Arm membership is frozen before any model run.

- Arm 2 uses the lowest GitSkills rank among retained sources routed to the
  case's expected category. The expected category is locked in the evaluation
  specification before execution. A global true-negative case has no Arm 2
  skill; this arm then equals the unskilled condition and is excluded from the
  Arm 2 activation estimate.
- Arm 3 always installs all 119 active-category retained exact-hash sources. It is never reduced
  after inspecting a task or observed conflict.
- Arm 4 always installs all 10 active super-skills. It is never reduced after inspecting
  a task.
- The installed names, descriptions, content hashes, byte counts, and token
  counts are recorded in the run manifest. Any source that cannot be reconstructed
  is reported before execution; it is not silently replaced.

These rules deliberately avoid the post hoc judgment implicit in “all relevant
skills.” Arm 3 is an upper bound on narrow-skill overhead and conflict exposure,
not a typical deployment estimate; Arm 4 represents the consolidated suite.

## Evaluation population

Category cases include positive tasks and close boundary cases. The shared
`true-negatives.yaml` set contains tasks for which none of the 10 active super-skills
should activate. True negatives run with the complete Arm 3 and Arm 4
installations so activation precision has a real negative denominator.

Before execution, each case must declare:

- whether any skill should activate;
- the expected primary category, if any;
- allowed secondary categories;
- forbidden activations; and
- the observable behavior and failure signals used for grading.

## Outcome measures

Report arm-level and case-level results for:

- blinded task-quality score under `evals/shared/rubric.yaml`;
- activation precision: correct activations divided by all activations;
- activation recall: required primary activations divided by should-fire cases;
- global true-negative rate and false activations per negative task;
- installed description tokens, loaded instruction tokens, total input tokens,
  output tokens, latency, and cost; and
- conflict symptoms, tool calls, side effects, and verification failures.

The unskilled and individual-source arms establish behavioral baselines. The
source-suite and super-suite arms answer the product question.

## Natural and matched-budget comparisons

The primary comparison uses each arm's natural host behavior and reports its
actual token and latency cost. Efficiency is not itself evidence of equal task
quality.

A matched-budget sensitivity analysis compares Arms 3 and 4 on should-fire
cases. The budget equals the super suite's actual loaded instruction tokens for
that case. For Arm 3, eligible sources are those routed to the locked expected
category, ordered by GitSkills rank; whole source skills are included in that
order until the next file would exceed the budget. Files are never truncated,
and unused budget is reported. This subset is computed before model execution.

Report quality against cost jointly:

- lower cost with equivalent or better quality supports consolidation;
- lower cost with worse quality measures the consolidation cost; and
- higher quality bought with more context is not described as an efficiency
  improvement.

No superiority claim may be based on cost, quality, or routing alone.

## Run discipline

- Randomize arm order within each case and record the seed.
- Use repeated runs sufficient to report uncertainty rather than a single
  deterministic demonstration.
- Blind graders to arm identity and randomize response order.
- Publish model, host, tokenizer, prompts, parameters, tool environment, run
  failures, exclusions, and grading instructions.
- Lock the analysis script and case set before unblinding aggregate results.
