---
name: game-development
description: Design, implement, tune, or critique games and immersive experiences across 2D, mobile, PC/console, audio, VR, and AR. Use when a player loop, feel, progression, real-time simulation, platform input, performance budget, game audio, or embodied interaction is central.
---

# Game Development

Build around the player's repeated decisions and feedback. Technology, content, and progression should reinforce that loop within the target platform's constraints.

## Establish the experience contract

Define target players, platform, session length, core fantasy, repeated action loop, failure/recovery, progression, content scope, input, performance target, and accessibility needs. Choose a small playable slice that can test the riskiest assumption.

Route specialist decisions:

- game loop, mechanics, progression, economy, and playtesting: [game-design.md](references/game-design.md);
- update models, input, collision, AI, determinism, and networking: [simulation-systems.md](references/simulation-systems.md);
- 2D, mobile, PC/console implementation and performance: [platform-engineering.md](references/platform-engineering.md);
- adaptive music, effects, voice, mixing, and feedback: [game-audio.md](references/game-audio.md);
- VR/AR comfort, embodiment, tracking, and spatial interaction: [xr.md](references/xr.md).

## Build the playable truth

1. Prototype the core verb with temporary content.
2. Make input-to-feedback latency and state changes observable.
3. Test whether players understand the goal without coaching.
4. Tune challenge, information, and recovery using play evidence.
5. Add progression and content only after the loop supports repetition.
6. Profile representative hardware and worst-case scenes.
7. Verify save/load, pause/resume, input loss, disconnects, and platform lifecycle where relevant.

## Keep systems legible

Expose consequences through animation, audio, UI, camera, and world response. Avoid stacking mechanics that do not create new decisions. Separate deterministic simulation from presentation when reproducibility or networking requires it.

## Report what was played

Distinguish design intent from observed playtest behavior. State the build, device, input method, performance conditions, and unresolved experience risks.
