# Mobile and image-to-code

## Reconstruct visual references

Treat a screenshot as evidence of one state at one viewport. Infer:

1. structural regions and reading order;
2. container and alignment rules;
3. recurring tokens and component families;
4. likely responsive transformations;
5. which elements are assets versus reproducible UI.

Match high-salience geometry, typography, spacing rhythm, color, and imagery before low-impact decoration. Use available assets when authorized; do not fabricate hidden behavior as fact.

## Design for mobile context

Account for safe areas, dynamic text, virtual keyboards, reachability, touch targets, connectivity changes, and platform navigation expectations. Keep the primary action reachable without crowding persistent controls. Test rotation or window resizing when the product supports it.

## Choose fidelity deliberately

Pixel fidelity is appropriate for an implementation reference; behavioral and platform fidelity still take precedence when the reference conflicts with accessibility or actual product requirements. Record intentional deviations.
