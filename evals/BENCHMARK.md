# Comparative benchmark protocol

## Status and objective

This document preregisters the comparative design. The repository does not yet
contain benchmark results.

The primary product question is whether a small synthesized suite preserves or
improves task behavior while meeting an absolute false-activation threshold and
reducing instruction cost
relative to installing the overlapping public source skills from which it was
derived.

## Pre-execution publication gate

Before any benchmark execution, the current active public skill files must pass
`scripts/check_similarity.py --verify-gitskills-frame` against all 999 eligible
baseline-plus-expansion sources at the preregistered normalized eight-word-shingle
and 20% smaller-document containment threshold. The checker must confirm that
the external files' computed Git blob IDs exactly match the recorded frame
before testing prose. It also checks exact bytes and falls back to normalized
shorter-sequence containment whenever either file cannot form an eight-word
shingle. Partial short matches require at least four normalized tokens; files
with fewer tokens still receive exact-byte and normalized-exact checks. Unicode
word tokenization, non-Latin character segmentation within mixed-script tokens,
and a normalized non-ASCII
character fallback prevent non-ASCII text from becoming an empty comparison.
In frame-verification mode, the checker rejects
any shingle-size or threshold override and emits its effective parameters.
Any qualifying overlap is a publication blocker: stop,
inspect the lineage, and independently rewrite or withdraw the affected
material before collecting benchmark results. Record the corpus checksum,
public-file checksum, command, threshold, and results in `research/VALIDATION.md`.

## Four fixed arms

Every case is run under these conditions with the same host, model, tool access,
task input, and sampling parameters:

1. **Unskilled:** no source or super-skill is installed.
2. **Highest-ranked source:** one source skill is chosen before execution by
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
  a recognizable source-name suffix. Transform bytes deterministically with
  `PyYAML==6.0.2`: decode the entry as UTF-8, compose its front matter, locate
  the top-level `name` value node's exact character span, and replace only that
  span with `json.dumps(installed_name, ensure_ascii=False, separators=(",", ":"))`.
  Re-encode as UTF-8 without changing any other character. A missing, duplicate,
  non-scalar, or unlocatable `name` blocks execution. The transform validator
  recomputes the result and digest independently before any run; the manifest
  records the pinned PyYAML version and algorithm identifier
  `arm3-name-span-json-v1`. The description,
  instruction body, comments, quoting outside the value span, and all other
  bytes remain source-derived.
- Arm 4 always installs all 10 active super-skills. It is never reduced after inspecting
  a task.
- The committed source token record fixes each original and installed Arm 3
  name. The run manifest records both names, the original Git blob hash, the
  transformed file hash, description SHA-256, semantic description byte and
  token counts, entry byte counts, and entry token counts. It never publishes
  the third-party description text. Any source that cannot be reconstructed or
  transformed exactly is reported before execution; it is not silently
  replaced.

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

## Source dependency-closure gate

Arms 2 and 3 may not run until every one of the 119 active retained entry hashes
has a complete, pinned file-dependency closure from one deterministic
occurrence. Use the ledger's repository, path, and commit when it records a
verified exact Git blob. Otherwise, enumerate the GitSkills occurrences for
that hash, sort by case-sensitive `(repository_full_name, path)`, and choose the
first reachable occurrence whose resolved default-branch commit contains the
exact entry blob; pin that repository, path, and commit in the pre-execution
manifest. If no candidate qualifies, execution is blocked. Never switch to a
different occurrence after inspecting its sibling files. From the selected
entry, include every file beneath that skill directory and recursively include
each relative file or directory referenced outside it. Record declared runtime packages and tools separately;
they are environment dependencies, not substitutes for missing files. An
unresolved commit, missing path, submodule, generated asset, or inaccessible
dependency blocks benchmark execution rather than silently shrinking an arm.

Raw closure files remain external. The run manifest records, for every source,
the entry Git blob, pinned repository and commit, repository-relative path,
every dependency path, byte size, Git blob or SHA-256 digest, executable bit,
and a checksum over the sorted closure records. The Arm 3 name transform changes
only the entry file's front-matter `name`; all dependency bytes remain unchanged,
and the manifest records both the original and transformed entry digests.

After all closures are pinned, rerun the originality gate with
`--closure-sources /absolute/path/to/pinned-closure-files` and
`--closure-manifest /absolute/path/to/closure-records.jsonl`. The checker verifies
the 999-entry GitSkills population separately, scans every closure file as an
additional comparison corpus, and emits the closure file count and canonical
record checksum. Each JSONL record contains exactly `source_file_sha`,
`repository`, `commit`, `repository_path`, `sha256`, `executable`, and
`staged_path`. `staged_path` maps the external file but is excluded from the
checksum; the other fields are serialized as UTF-8 JSON with sorted keys and
compact separators, sorted lexicographically by complete record, joined with a
trailing newline, and hashed with SHA-256. That count and checksum must equal
the same canonical records in the run manifest. The manifest must cover exactly
the 119 active retained source hashes and include at least one staged entry whose
computed Git blob equals each `source_file_sha`. All records for one source use
one pinned repository and commit, and each staged file's actual executable bits
must equal its record. Missing, extra, duplicate, mode-mismatched, or otherwise
mismatched closure files block benchmark
execution. Closure prose remains external and is never committed or published.

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

The unskilled and highest-ranked-source arms establish behavioral baselines. The
source-suite and super-suite arms answer the product question.

Installed description tokens are the sum of the front-matter description value
for every installed skill, using the pinned tokenizer. They represent the
always-loaded discovery cost before any skill activates. The run manifest must
record both that normalized count and the actual host-rendered discovery input
when the host adds framing or transforms metadata. The preregistration baseline
is 580 tokens for Arm 4 and 5,613 tokens for the externally reconstructed Arm 3
under `cl100k_base` and `tiktoken==0.11.0`; a run must recompute these figures
and explain any difference before execution.

## Natural and fixed-budget comparisons

The primary comparison uses each arm's natural host behavior and reports its
actual token and latency cost. Efficiency is not itself evidence of equal task
quality.

A fixed-budget sensitivity analysis compares Arms 3 and 4 on should-fire cases.
Before any run, each case's permitted Arm 4 set is its locked primary category
plus every locked allowed secondary category. Its budget is the sum of those
skills' generated `full_tokens` counts in `research/token-counts.csv`; it is not
selected from observed activations. The same permitted set, budget, and Arm 3
subset apply to all three repetitions and do not depend on observed Arm 4
activation, tokens, latency, or quality. Any Arm 4 activation outside the
permitted set automatically fails the fixed-budget consolidation decision; it
is not a reason to raise the budget, rerun, or exclude the case. For Arm 3,
eligible source bundles are those routed
to a permitted category, ordered by GitSkills rank;
each bundle's budget cost uses the same file classes as the generated Arm 4
`full_tokens` value: the transformed installed `SKILL.md` bytes plus every
unchanged Markdown file directly in its `references/` directory, counted with
`cl100k_base` under pinned `tiktoken==0.11.0` after the name transform is
validated. The original entry token count remains descriptive and never selects
the prefix. Other closure content remains installed and is
reported, but scripts, assets, nested references, and non-Markdown dependencies
are excluded from both arms' fixed instruction-budget calculation. Whole
bundles are included in order until the next would exceed the budget. Files are
never truncated, and unused budget is reported. Natural-host results separately
report the actual loaded tokens for every run.

The fixed-budget Arm 3 condition is an isolated installation containing only
the selected whole-bundle prefix; the other retained source skills are neither
installed nor activatable in that condition. The exhaustive 119-source Arm 3
installation applies only to the natural-host comparison. The run manifest
records both installations and verifies that fixed-budget activations belong to
the selected prefix.

Report quality against cost jointly:

- lower cost with equivalent or better quality supports consolidation;
- lower cost with worse quality measures the consolidation cost; and
- higher quality bought with more context is not described as an efficiency
  improvement.

No superiority claim may be based on cost, quality, or routing alone. In
particular, a lower instruction bill for Arm 4 does not compensate for a
material quality loss under the fixed-budget comparison.

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

A scheduled run is one analysis observation. Retry it at most once, and only
for a transport, host, model-service, or tool-runtime failure that occurs before
a gradable response exists; use the same recorded seed and identical inputs.
A tool error represented in a response is task behavior and is not retried. If
the one permitted retry also produces no gradable response, retain the scheduled
observation with a numeric quality score of 0/10, failed pass/fail status, no
successful activation credit, and its observed tokens, latency, cost, and error
metadata. Never exclude, replace, or add runs after seeing an outcome. A
benchmark-wide environment-integrity failure discovered before arm execution
blocks the benchmark rather than creating arm observations.

For each should-fire case and comparator, form one paired difference: the Arm 4
case mean minus the comparator case mean. Analyze Arms 2 and 3 separately. The
primary suite estimate is the equal-weight mean of the 10 active-category means,
so categories with more authored cases do not receive more weight. Its paired
95% confidence interval uses 10,000 stratified nonparametric bootstrap samples:
resample cases with replacement within each category at the original category
sample size, recompute the 10 category means and their equal-weight mean, and
take the 2.5th and 97.5th percentiles. Use NumPy `Generator(PCG64)` with seed
`20260821`. Each resampled case carries all arm scores together, preserving the
pairing. Apply the same estimator to three decision-bearing contrasts: Arm 4
versus Arm 2 under natural-host behavior, Arm 4 versus Arm 3 under natural-host
behavior, and Arm 4 versus the fixed-budget Arm 3 subset. Never pool those
conditions.

Global true-negative quality is a separate decision family. For every negative
case, compute the paired difference between the three-run Arm 4 case mean and
the corresponding Arm 1 mean, and separately between Arm 4 and Arm 3. For each
of these two contrasts, average the 36 case differences equally and use 10,000
paired nonparametric bootstrap samples over cases with NumPy `Generator(PCG64)`
seed `20260822`. Use Bonferroni-adjusted 97.5% two-sided percentile intervals,
providing at least 95% simultaneous coverage across both contrasts. This makes
incorrect bounded answers and withheld-boundary failures decision-bearing even
when no skill falsely activates.

Publish a category-specific paired interval using the same case-level means and
bootstrap procedure. Every category case carries a locked `analysis_category`
equal to its `expected_primary_category`; file location does not determine its
stratum. Resampling, category means, and split decisions use that field. The
decision family contains 30 category contrasts: 10
categories across the three contrasts above. Every category decision therefore
uses a Bonferroni-adjusted 99.8333% two-sided percentile interval
(`1 - 0.05 / 30`), providing at least 95% simultaneous coverage across the full
family. Also publish ordinary 95% category intervals as descriptive estimates,
but do not use them to decide whether a category must split.

Activation precision uses correct activated-skill events as its numerator and
all activated-skill events as its denominator; activation recall uses one
required-primary-activation outcome per should-fire case-run. Report two-sided
95% Wilson score intervals without continuity correction for these binomial
rates. For false activation, one trial is one Arm 4 global-negative case-run,
yielding 108 preregistered trials from 36 cases and three runs. The falsification
gate uses the pooled 108-trial rate and its two-sided 95% Wilson interval. Report
the same rates for comparator arms descriptively, but do not interpret their
difference as the preregistered gate. Also report a 36-case sensitivity where a
case is positive if any of its three runs falsely activates. Report activation
rates both overall and by category;
category rates are descriptive unless a gate below explicitly names them.

## Falsification criteria

The consolidation hypothesis is that Arm 4 preserves task quality within a
preregistered non-inferiority margin while reducing discovery or loaded-context
cost, keeping its absolute false-activation rate acceptable, and avoiding unsafe
side effects. The quality margin is **0.5 points on the ten-point rubric total**;
the absolute false-activation threshold is **10%**.

A suite-wide consolidation claim requires the lower bound of the paired 95%
interval for `Arm 4 minus comparator` to exceed -0.5 in all three
decision-bearing contrasts. A category-specific claim additionally requires
that category's lower 99.8333% bound to exceed -0.5 in all three contrasts. Arm
4's upper two-sided 95% Wilson bound for false activation must be at most 10%.
The lower bound of both global-negative quality intervals must exceed -0.5.
Arm 4 must also have no critical-failure event meeting gate 3 below. These are
success conditions, not merely the absence of a failure signal. The
fixed-budget claim additionally requires no out-of-permitted-set Arm 4
activation in any fixed-budget case-run.

Consolidation is treated as failed—and the affected category must be split or
returned to narrower skills before a superiority claim—if any of these occurs:

1. In any decision-bearing contrast, the upper bound of the suite-level paired
   95% interval for `Arm 4 minus comparator` is below -0.5, or a category's
   Bonferroni-adjusted 99.8333% upper bound is below -0.5. A suite
   failure blocks a suite-wide consolidation claim; a category failure requires
   that category to split or return to narrower skills.
2. The lower bound of Arm 4's two-sided 95% Wilson false-activation interval
   exceeds 10%.
3. Arm 4 causes a critical unauthorized, destructive, privacy, security, or
   accessibility failure on the same case in at least two repeated runs. This
   is an absolute blocker regardless of comparator behavior; matching Arm 2 or
   Arm 3 failures are reported separately as context, not used to waive it.
4. Arm 4 activates any skill outside the case's preregistered permitted set in
   a fixed-budget case-run. This fails the fixed-budget consolidation decision
   regardless of the resulting quality score.
5. The upper bound of either global-negative quality interval is below -0.5.
   This fails the suite-wide consolidation decision even when Arm 4 correctly
   avoids skill activation.

If a quality lower bound is at or below -0.5 without its upper bound falling
below -0.5, including either global-negative quality interval, or the
false-activation interval crosses 10%, the affected result is
**inconclusive**, not evidence for consolidation. Meeting the success conditions
permits a consolidation claim only when the joint quality-and-cost results also
support it; it does not by itself establish superiority.

## Run discipline

- Randomize arm order within each case and record the seed.
- Before every scheduled arm-run, recreate an isolated mutable tool environment
  from the case's preregistered baseline snapshot and verify its canonical state
  hash, account or tenant identity, target identities, permissions, and fixture
  versions. Arms and repetitions never share a mutable namespace. Discard the
  environment after the observation; a permitted infrastructure retry receives
  a fresh verified copy of the same snapshot. If an external service cannot
  provide a resettable sandbox or the reset cannot be verified, block that case
  before execution rather than run it against residual state.
- Run exactly three independent model samples per arm and case, as specified
  above; do not choose the repeat count after observing variance.
- Apply the independent-grading protocol above; blind graders to arm identity
  and randomize response order.
- Publish model, host, tokenizer, prompts, parameters, tool environment, run
  failures, exclusions, and grading instructions.
- Lock the analysis script and case set before unblinding aggregate results.
