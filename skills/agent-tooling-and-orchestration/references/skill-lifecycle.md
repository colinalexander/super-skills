# Skill lifecycle

## Decide whether a skill is warranted

A skill is useful when a recurring task benefits from specialized procedure, resources, tools, or quality gates that the agent would not apply reliably from general knowledge. Avoid skills that merely restate common sense or force one interaction style globally.

## Design from evals

Write representative requests before instructions. Include clear triggers, close non-triggers, difficult cases, and failure conditions. Define what a better result looks like. Use this set to shape the skill and to catch regressions.

## Structure for staged loading

- Metadata should answer when the skill applies.
- The entry file should contain invariants, routing, and the default workflow.
- References should contain mode-specific detail.
- Scripts should perform deterministic or repeatedly useful work.
- Assets should exist only when they are meant to be used in outputs.

Avoid deep reference chains and duplicate rules.

## Improve empirically

Run the same cases with and without the skill, inspect differences, and revise the smallest instruction that explains the failure. Watch for over-triggering, excessive ceremony, invented authority, tool fixation, and instructions that hide rather than resolve ambiguity.

## Package cleanly

Validate metadata and links. Keep temporary source material outside the skill. Document dependencies and permissions. Use an open license only for material you are entitled to license.
