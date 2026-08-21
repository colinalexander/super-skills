# Simulation systems

## Choose an update model

Separate input sampling, simulation, presentation, and slow/background work. Use fixed steps where physics, deterministic replay, or networking needs consistent time; interpolate presentation when required. Bound catch-up work so a slow frame does not create an unrecoverable spiral.

## Abstract player intent

Map devices to semantic actions and keep remapping, accessibility, multiple devices, and device loss in scope. Preserve responsive local feedback even when the authoritative result is delayed by animation or networking.

## Keep collision purposeful

Use the simplest shape and query strategy that produces the intended gameplay. Define layers and ownership clearly, avoid high-frequency expensive broad queries, and test tunneling, stacked contacts, spawn overlap, and fast-moving objects.

## Scale AI to the decision

Use direct rules or state machines for legible bounded behavior, behavior trees for reusable hierarchical choices, planners for dynamic goal selection, and navigation systems for movement. Spend computation on decisions players can perceive. Instrument state and transitions for debugging.

## Design networking explicitly

Choose authority, replication, prediction, reconciliation, interpolation, lag compensation, and disconnect recovery from the game's fairness and responsiveness needs. Keep security decisions server-authoritative where clients have an incentive to cheat. Test latency, jitter, loss, reconnect, version mismatch, and duplicate messages.

## Preserve determinism where promised

Control random seeds, ordering, time sources, and floating-point assumptions. Record enough inputs and state to reproduce a desynchronization or gameplay bug.
