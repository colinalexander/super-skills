# Implementation and quality

## Inspect the environment

Before changing code, identify the framework, styling method, component library, tokens, route structure, assets, and local validation commands. Reuse established primitives when they satisfy the design; do not recreate them for novelty.

## Build a coherent slice

Keep semantic HTML and platform controls whenever possible. Establish layout and responsive structure before micro-styling. Centralize repeated values as tokens. Preserve behavior while refactoring presentation.

## Required checks

- Render at narrow, medium, and wide viewports.
- Exercise keyboard order, visible focus, labels, landmarks, and dialog behavior.
- Check text and non-text contrast, zoom/reflow, touch targets, and reduced motion.
- Test long, short, missing, loading, error, and empty data.
- Watch for layout shift, oversized media, unnecessary client work, and animation jank.
- Confirm that interactions remain usable without hover.

Use automated checks as a floor. Visually inspect the rendered result and exercise the primary journey.

## Report honestly

Distinguish verified behavior from design intent. If the environment prevents rendering or interaction testing, say so and identify the highest-risk unverified areas.
