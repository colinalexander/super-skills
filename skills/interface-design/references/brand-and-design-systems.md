# Brand and design systems

## Separate identity from components

Translate brand attributes into operational choices: voice, typography roles, palette roles, image treatment, shape language, density, and motion character. Then encode those choices as tokens and component contracts. A logo and a color list alone are not a usable system.

## Define tokens by role

Prefer semantic roles such as `surface`, `text-muted`, `action-primary`, `danger`, and `focus` over color-named tokens. Establish a compact scale for spacing, typography, radius, elevation, and motion. Document when an exception is legitimate.

## Specify component behavior

For every reusable component, cover:

- anatomy and content limits;
- variants and size decisions;
- interaction and keyboard behavior;
- focus, hover, pressed, disabled, loading, and error states;
- responsive changes;
- accessibility name and relationship requirements.

Use composition for structural variation; avoid a single component with many interacting flags.

## Preserve expressive range

A system should make common work consistent without making every surface identical. Define stable foundations and a bounded set of expressive zones for campaigns, editorial moments, or product tiers.

## Govern change

Record why a token or component exists, designate its owner, and provide a migration path for breaking changes. Audit actual product usage before deleting an apparent duplicate.
