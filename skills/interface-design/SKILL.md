---
name: interface-design
description: Create, redesign, implement, or critique web and mobile interfaces, visual artifacts, design systems, and brand expression. Use for UI/UX, frontend presentation, image-to-code, logos, brand boards, banners, animated graphics, algorithmic art, or other work where visual hierarchy, interaction, or art direction materially shapes the result.
---

# Interface Design

Build an intentional interface from evidence and constraints. Do not impose a fashionable house style.

## Establish authority

Resolve decisions in this order:

1. explicit user requirements and supplied references;
2. the product's existing design system, brand, and interaction conventions;
3. platform behavior, accessibility, and technical constraints;
4. the selected creative direction;
5. conservative defaults.

Ask only when a missing choice would materially change the result. Otherwise state the assumption and proceed.

## Choose the mode

- For a new experience, define audience, job, emotional register, and one coherent visual direction. Read [creative-direction.md](references/creative-direction.md).
- For an existing product, preserve what works and diagnose the highest-impact weaknesses before changing style. Read [audit-and-redesign.md](references/audit-and-redesign.md).
- For a design system or brand, define reusable tokens, component behavior, governance, and expressive range. Read [brand-and-design-systems.md](references/brand-and-design-systems.md).
- For a logo, brand board, banner, social image, animated graphic, canvas composition, or algorithmic artwork, read [visual-artifacts.md](references/visual-artifacts.md).
- For screenshot or visual-reference implementation, infer structure separately from decoration. Read [mobile-and-image-to-code.md](references/mobile-and-image-to-code.md).
- For production implementation, always apply [implementation-and-quality.md](references/implementation-and-quality.md).

## Work from structure outward

1. Identify the primary user journey and the page's dominant action.
2. Define content hierarchy and states before surface styling.
3. Choose a visual thesis that supports the product rather than competing with it.
4. Implement a small token vocabulary for color, type, spacing, shape, elevation, and motion.
5. Build reusable components only where behavior or appearance truly repeats.
6. Cover loading, empty, error, success, long-content, and narrow-screen states.
7. Render and inspect at representative breakpoints. Test keyboard flow, focus, contrast, labels, reduced motion, and touch targets.

## Keep decisions contextual

Bold, minimal, editorial, playful, industrial, and restrained directions are modes, not universal rules. A typeface, gradient, border radius, animation, or layout device is valid only when it supports the chosen direction and existing authority. Avoid generic “AI-looking” composition by making a specific thesis, not by banning individual ingredients.

## Deliver evidence

Explain the direction in one sentence. Identify the system decisions that make it coherent. When code or design artifacts are changed, report what was rendered or tested and any unresolved fidelity or accessibility risks.
