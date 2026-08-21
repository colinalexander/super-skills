# Comparative benchmark protocol

## Status and objective

This document preregisters the comparative design. The repository does not yet
contain benchmark results.

The primary product question is whether a small synthesized suite preserves or
improves task behavior while reducing selection errors and instruction cost
relative to installing the overlapping public source skills from which it was
derived.

## Pre-execution publication gate

Before any benchmark execution, the current active public skill files must pass
`scripts/check_similarity.py` against all 999 eligible baseline-plus-expansion sources at the
preregistered normalized eight-word-shingle and 20% smaller-document
containment threshold. Any qualifying overlap is a publication blocker: stop,
inspect the lineage, and independently rewrite or withdraw the affected
material before collecting benchmark results. Record the corpus checksum,
public-file checksum, command, threshold, and result in `research/VALIDATION.md`.

## Four fixed arms

Every case is run under these conditions with the same host, model, tool access,
task input, and sampling parameters:

1. **Unskilled:** no source or super-skill is installed.
2. **Best individual source:** one source skill is chosen before execution by
   the mechanical rule below.
3. **Source-suite ceiling:** all 119 hashes marked `retained` in
   `research/review-decisions.csv` and routed to an active category are installed
   as separate skills from an external reconstructed corpus. Exact hashes and
   the preregistered active-category list, not researcher-selected conflict sets,
   determine membership.
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
skills.” Arm 3 is an **upper bound on narrow-skill overhead and conflict
exposure**, not a claim about a typical deployment: installing all 119 active-category retained
sources is intentionally exhaustive and unlikely to match ordinary practice.
It tests whether the synthesized suite preserves the retained evidence under
the hardest mechanically reproducible source-suite comparison. Results from
this arm must not be presented as an estimate of a typical user's narrow-skill
cost or behavior.

## Evaluation population

Category cases include positive tasks and close boundary cases. The shared
`true-negatives.yaml` set contains 36 near-miss and ordinary tasks for which
none of the 10 active super-skills should activate. True negatives run with the
complete Arm 3 and Arm 4 installations so activation precision has a real
negative denominator. The set is still modest; report binomial confidence
intervals rather than treating a point estimate as precise.

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

Installed description tokens are the sum of the front-matter description value
for every installed skill, using the pinned tokenizer. They represent the
always-loaded discovery cost before any skill activates. The run manifest must
record both that normalized count and the actual host-rendered discovery input
when the host adds framing or transforms metadata. The preregistration baseline
is 580 tokens for Arm 4 and 5,613 tokens for the externally reconstructed Arm 3
under `cl100k_base` and `tiktoken==0.11.0`; a run must recompute these figures
and explain any difference before execution.

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

No superiority claim may be based on cost, quality, or routing alone. In
particular, a lower instruction bill for Arm 4 does not compensate for a
material quality loss under the matched-budget comparison.

## Independent grading

The primary task-quality outcome is the mean of **two independent human
graders** applying `evals/shared/rubric.yaml`. Graders receive responses in a
random order, remain blind to arm identity, installed skills, token counts, and
latency, and score each response before seeing the other grade.

A third human adjudicator reviews any case where the first two graders disagree
on pass/fail, differ by more than two points on the ten-point rubric total, or
flag different critical side effects. Publish both original grades, the
adjudication, grader instructions, and inter-rater agreement. A fixed model
grader may be reported as a secondary sensitivity analysis, but it cannot
replace the human primary outcome; its provider, model, version, prompt, and
parameters must be disclosed.

## Falsification criteria

The consolidation hypothesis is that Arm 4 preserves task quality within a
preregistered non-inferiority margin while reducing discovery or loaded-context
cost and without increasing false activation or unsafe side effects. The
quality margin is **0.5 points on the ten-point rubric total**.

Consolidation is treated as failed—and the affected category must be split or
returned to narrower skills before a superiority claim—if any of these occurs:

1. Against either Arm 2 or Arm 3 on should-fire cases, the upper bound of the
   paired 95% confidence interval for `Arm 4 minus comparator` is below -0.5.
2. Arm 4 falsely activates on more than 10% of global true-negative trials and
   the lower bound of its 95% binomial confidence interval exceeds 5%.
3. Arm 4 causes a critical unauthorized, destructive, privacy, security, or
   accessibility failure on the same case in at least two repeated runs when
   neither Arm 2 nor Arm 3 does.

If the intervals are too wide to establish non-inferiority or falsification,
the result is **inconclusive**, not evidence for consolidation. Passing these
gates permits a consolidation claim only when the joint quality-and-cost results
also support it; it does not by itself establish superiority.

## Run discipline

- Randomize arm order within each case and record the seed.
- Use repeated runs sufficient to report uncertainty rather than a single
  deterministic demonstration.
- Apply the independent-grading protocol above; blind graders to arm identity
  and randomize response order.
- Publish model, host, tokenizer, prompts, parameters, tool environment, run
  failures, exclusions, and grading instructions.
- Lock the analysis script and case set before unblinding aggregate results.
