# Game development synthesis matrix

Baseline: 7 ranked hashes, 7 distinct names.

Evidence labels: `game-design`, `game-audio`, `pc-games`, `mobile-games`, `2d-games`, `vr-ar`, `game-development`.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Core design | Define perceive-decide-act-feedback loops and learning | Content expansion waits until the core loop survives playtesting |
| Mechanics | Keep mechanics that create meaningful decisions | More systems do not automatically mean more depth |
| Simulation | Separate input, simulation, and presentation; choose collision, AI, determinism, and networking by player-facing need | Complexity is earned by observable behavior, fairness, or reproducibility |
| Platforms | Treat input, lifecycle, hardware, and performance as design constraints | Engine/editor success is not target-device evidence |
| Distribution and monetization | Account for stores, privacy, purchases, ads, updates, and platform services as experience constraints | Revenue mechanics cannot obscure consent, price, probability, or purchase recovery |
| Audio | Assign gameplay and emotional roles, then mix under load | Variation must preserve recognition and critical cues |
| XR | Prioritize comfort, embodiment, tracking, and physical-space safety | Visual ambition never outranks stable frame time and user comfort |
| Validation | Prototype risky assumptions and observe players | Stated design intent is separated from actual player behavior |
| Omission repair | Added accessibility, save/recovery, and profiling gates | Happy-path prototypes do not prove a shippable experience |

Resulting modes: game design, simulation systems, platform engineering, audio, and XR.
