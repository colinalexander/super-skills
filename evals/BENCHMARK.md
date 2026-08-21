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
`scripts/check_similarity.py --verify-gitskills-frame` against all 999 eligible
baseline-plus-expansion sources at the preregistered normalized eight-word-shingle
and 20% smaller-document containment threshold. The checker must confirm that
the external files' computed Git blob IDs exactly match the recorded frame
before testing prose. Any qualifying overlap is a publication blocker: stop,
inspect the lineage, and independently rewrite or withdraw the affected
material before collecting benchmark results. Record the corpus checksum,
public-file checksum, command, threshold, and results in `research/VALIDATION.md`.

## Four fixed arms

Every case is run under these conditions with the same host, model, tool access,
task input, and sampling parameters:

1. **Unskilled:** no source or super-skill is installed.
2. **Best individual source:** one source skill is chosen before execution by
   the mechanical rule below.
3. **Source-suite ceiling:** all 119 hashes marked `retained` in
   `research/review-decisions.csv` and routed to an active category are installed
   as separate skills from an external reconstructed corpus, using the fixed
   collision-safe naming transform below. Exact source hashes and the
   preregistered active-category list, not researcher-selected conflict sets,
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
- Arm 3 applies the same naming transform to every source, not only collisions.
  Normalize the source's original front-matter `name` to lowercase, replace
  each non-`[a-z0-9]` run with `-`, trim separators, truncate to 48 characters,
  and use `skill` if empty. The installed directory and front-matter name are
  `gs-rRRRR-<slug>`, where `RRRR` is the source's unique zero-padded GitSkills
  rank. The rank prefix makes all 119 identifiers collision-free while retaining
  a recognizable source-name suffix. Only the `name` scalar changes; the
  description and instruction body remain byte-for-byte source-derived.
- Arm 4 always installs all 10 active super-skills. It is never reduced after inspecting
  a task.
- The committed source token record fixes each original and installed Arm 3
  name. The run manifest records both names, the original Git blob hash, the
  transformed file hash, descriptions, byte counts, and token counts. Any source
  that cannot be reconstructed or transformed exactly is reported before
  execution; it is not silently replaced.

These rules deliberately avoid the post hoc judgment implicit in “all relevant
skills.” Arm 3 is an **upper bound on narrow-skill overhead and conflict
exposure**, not a claim about a typical deployment: installing all 119 active-category retained
sources is intentionally exhaustive and unlikely to match ordinary practice.
It tests whether the synthesized suite preserves the retained evidence under
the hardest mechanically reproducible source-suite comparison. Results from
this arm must not be presented as an estimate of a typical user's narrow-skill
cost or behavior. Its universal rename is a
**protocol-imposed compatibility transform** that may itself affect routing; report that limitation and do not
describe Arm 3 as an unmodified source-suite deployment.

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

Each response is accompanied by an arm-neutral evidence packet. Before grading,
an evaluator maps raw skill activations to the locked capability categories and
roles (`primary`, `secondary`, or `forbidden`), and maps tool activity to
normalized action type, target class, authorization state, outcome, and side
effect. The packet includes no skill name, arm identifier, instruction text,
token count, latency, provider metadata, or ordering clue. Graders score routing
and restraint from this packet rather than inferring hidden behavior from the
response prose. The mapping specification, raw trace, redacted packet, and a
machine-checkable linkage between them are published after grading so the
transformation can be audited without breaking blinding.

## Fixed analysis unit and uncertainty

Run each arm exactly **three times per case** with independent recorded sampling
seeds. For each response, the numeric quality score is the arithmetic mean of
the two original blinded human grades. Adjudication determines pass/fail and
critical-side-effect classifications but does not replace either original
numeric grade. The arm-level score for a case is the arithmetic mean of its
three response scores. Runs and grader scores are never treated as independent
quality observations.

For each should-fire case and comparator, form one paired difference: the Arm 4
case mean minus the comparator case mean. Analyze Arms 2 and 3 separately. The
primary suite estimate is the equal-weight mean of the 10 active-category means,
so categories with more authored cases do not receive more weight. Its paired
95% confidence interval uses 10,000 stratified nonparametric bootstrap samples:
resample cases with replacement within each category at the original category
sample size, recompute the 10 category means and their equal-weight mean, and
take the 2.5th and 97.5th percentiles. Use NumPy `Generator(PCG64)` with seed
`20260821`. Each resampled case carries all arm scores together, preserving the
pairing. Apply the same estimator separately to the natural-host primary result
and matched-budget sensitivity result; never pool those conditions.

Publish a category-specific paired interval using the same case-level means and
bootstrap procedure. The 10 category decisions use Bonferroni-adjusted 99.5%
two-sided percentile intervals, providing 95% simultaneous coverage. Also
publish ordinary 95% category intervals as descriptive estimates, but do not
use them to decide whether a category must split.

Activation precision uses correct activated-skill events as its numerator and
all activated-skill events as its denominator; activation recall uses one
required-primary-activation outcome per should-fire case-run. Report two-sided
95% Wilson score intervals without continuity correction for these binomial
rates. For false activation, one trial is one Arm 4 global-negative case-run,
yielding 108 preregistered trials from 36 cases and three runs. The falsification
gate uses the pooled 108-trial rate and its two-sided 95% Wilson interval. Also
report a 36-case sensitivity where a case is positive if any of its three runs
falsely activates. Report activation rates both overall and by category;
category rates are descriptive unless a gate below explicitly names them.

## Falsification criteria

The consolidation hypothesis is that Arm 4 preserves task quality within a
preregistered non-inferiority margin while reducing discovery or loaded-context
cost and without increasing false activation or unsafe side effects. The
quality margin is **0.5 points on the ten-point rubric total**.

Consolidation is treated as failed—and the affected category must be split or
returned to narrower skills before a superiority claim—if any of these occurs:

1. Against either Arm 2 or Arm 3 on should-fire cases, the upper bound of the
   suite-level paired 95% interval for `Arm 4 minus comparator` is below -0.5,
   or a category's Bonferroni-adjusted 99.5% upper bound is below -0.5. A suite
   failure blocks a suite-wide consolidation claim; a category failure requires
   that category to split or return to narrower skills.
2. Arm 4 falsely activates on more than 10% of global true-negative trials and
   the lower bound of its two-sided 95% Wilson score interval exceeds 5%.
3. Arm 4 causes a critical unauthorized, destructive, privacy, security, or
   accessibility failure on the same case in at least two repeated runs when
   neither Arm 2 nor Arm 3 does.

If the intervals are too wide to establish non-inferiority or falsification,
the result is **inconclusive**, not evidence for consolidation. Passing these
gates permits a consolidation claim only when the joint quality-and-cost results
also support it; it does not by itself establish superiority.

## Run discipline

- Randomize arm order within each case and record the seed.
- Run exactly three independent model samples per arm and case, as specified
  above; do not choose the repeat count after observing variance.
- Apply the independent-grading protocol above; blind graders to arm identity
  and randomize response order.
- Publish model, host, tokenizer, prompts, parameters, tool environment, run
  failures, exclusions, and grading instructions.
- Lock the analysis script and case set before unblinding aggregate results.
