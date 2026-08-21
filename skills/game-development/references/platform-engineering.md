# Platform engineering

## Shared foundations

Use a stable update model, explicit game states, pooled or bounded high-frequency allocations, and data-driven tuning where it improves iteration. Keep rendering, input, audio, and persistence failures from corrupting simulation state.

## 2D games

Define world and pixel coordinate rules, camera scaling, sprite filtering, collision layers, draw order, and animation timing. Test multiple aspect ratios and avoid sub-pixel artifacts when the art direction depends on pixel precision.

## Mobile

Design for touch ambiguity, safe areas, interruption, thermal limits, memory pressure, and varied GPU/CPU classes. Minimize startup and resume friction. Test on representative low- and mid-tier physical devices, not only an editor or flagship emulator.

Account for store review, privacy disclosures, platform services, offline behavior, update size, and regional requirements. If the game uses ads, purchases, subscriptions, or rewarded mechanics, model their effect on pacing and trust; never let monetization obscure price, consent, probability, or the ability to recover from a purchase failure.

## PC and console

Support keyboard/mouse and controller navigation, device hot-swapping, display modes, resolution scaling, platform suspend/resume, save requirements, and certification constraints. Profile representative minimum-spec hardware and input latency.

## Performance budgets

Set frame-time, memory, loading, draw-call, and asset budgets appropriate to the target. Profile CPU and GPU separately using representative content. Optimize measured bottlenecks and validate that visual or simulation behavior remains correct.
