# Example gallery

This gallery shows what each Super Skill is intended to change in a concrete task. Each focused example includes a task, supplied evidence or a runnable fixture, expected decisions, a reference artifact, and a skill-specific rubric.

These are **demonstrations, not benchmark results**. A reference artifact makes the contract inspectable; it does not prove that a model will produce the artifact, that the skill caused an improvement, or that the skill outperforms its sources. Comparative claims remain governed by [`evals/BENCHMARK.md`](../evals/BENCHMARK.md).

## Focused examples

| Skill | Demonstration | Artifact |
| --- | --- | --- |
| [`interface-design`](focused/interface-design/) | Redesign an operations dashboard without discarding its sober, information-dense identity | Runnable HTML fixture and design decision record |
| [`software-delivery`](focused/software-delivery/) | Repair a seeded order-total defect without weakening the tests | Runnable Python fixture and verified repair |
| [`agent-tooling-and-orchestration`](focused/agent-tooling-and-orchestration/) | Design safe support-ticket tools for an agent | Tool contract |
| [`application-engineering`](focused/application-engineering/) | Design a concurrent inventory-reservation service | API contract and architecture decision record |
| [`game-development`](focused/game-development/) | Critique and tune a browser microgame's core loop | Playable HTML fixture and tuning plan |
| [`reasoning-modes`](focused/reasoning-modes/) | Apply exploration, adversarial review, reframing, and compression to one proposal | Mode sequence transcript |
| [`systems-and-security`](focused/systems-and-security/) | Diagnose a Linux service failure from a bounded evidence pack | Diagnostic and recovery plan |
| [`marketing-and-growth`](focused/marketing-and-growth/) | Develop positioning and a pricing test without inventing market evidence | Commercial decision memo |
| [`connected-service-automation`](focused/connected-service-automation/) | Safely share a file and notify a collaborator in a mocked workspace | Mutation plan and verification receipt |
| [`data-science-and-ml`](focused/data-science-and-ml/) | Detect target leakage in a churn-model proposal | Analysis and validation redesign |

## Integrated showcases

- [Ship a product feature](showcases/ship-a-product-feature.md): `application-engineering` + `interface-design` + `software-delivery`
- [Investigate a model incident](showcases/investigate-a-model-incident.md): `data-science-and-ml` + `systems-and-security` + `reasoning-modes`
- [Prepare and execute a launch](showcases/prepare-and-execute-a-launch.md): `marketing-and-growth` + `interface-design` + `connected-service-automation`

## Running an example

Open a focused example and give the contents of `TASK.md` to an agent with the named skill installed. When the host supports named invocation, invoke the skill explicitly:

```text
Use $software-delivery to complete examples/focused/software-delivery/TASK.md.
```

Keep the supplied evidence fixed, preserve the example's stated authority boundary, and record the model, host, skill version or commit, commands, output, and limitations. Score the result with the local `rubric.yaml`; do not replace the repository's comparative benchmark protocol with these demonstration scores.
