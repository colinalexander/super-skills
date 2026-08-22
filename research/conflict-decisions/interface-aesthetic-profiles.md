# Interface aesthetic profiles: context instead of voting

## Source disagreement

Two retained exact-hash sources prescribe incompatible defaults:

- [`minimalist-ui`](https://github.com/30Sativa/EXE201-PetOmi-Platform/blob/372f420e1c07852b5a3ef31e4cd6ebf6083752b3/apps/web/.agents/skills/minimalist-ui/SKILL.md)
  favors restrained warm monochrome, generous whitespace, soft geometry, and
  almost no shadow.
- [`industrial-brutalist-ui`](https://github.com/30x-llc/Monet/blob/7d8cc7a3349de13f472601a8c7ab4f068e5dff46/skills/craft/brutalist-skill/SKILL.md)
  favors rigid square geometry, visible compartmentalization, aggressive type,
  and dense telemetry.

`industrial-brutalist-ui` is the source's upstream front-matter name; the
repository stores that skill at `skills/craft/brutalist-skill/SKILL.md`.

The linked files reproduce GitSkills hashes
`44ead27ef04ffe79ade0c6df7fd696dbcf7b246b` and
`f5375b908340e1376ed391232a31c5d82d5babfb`, respectively.

These are not stronger and weaker settings on one style control. They answer
different questions about audience, task, and product identity.

## Explicit selection rule

Resolve the profile in this order:

1. **Existing product authority:** an established design system, supplied
   reference, or explicit user requirement wins. Preserve it unless change is
   authorized and the reason for departure is documented.
2. **Audience and task:** use the minimalist profile for focused reading or
   calm productivity where hierarchy and whitespace should reduce cognitive
   load. Use the industrial-brutalist profile for expert operational scanning,
   dense status comparison, or an explicitly mechanical/technical identity.
3. **Mismatch:** when neither audience/task pattern applies, choose neither
   profile and derive a different visual thesis from the product context.
4. **Non-negotiable constraints:** accessibility, platform behavior, content
   legibility, and performance can override devices from either profile.

The rule is inspectable: a reviewer can challenge the audience, task, authority,
or constraint evidence rather than accepting “the model decides.”

## Why majority vote fails

A voting pipeline would count profile-aligned retained sources, make whichever
profile appeared more often the default, and silently discard the other. That
would turn corpus frequency into an aesthetic mandate even though both profiles
are valid in different contexts. Super Skills retains both as modes and makes
the contextual branch explicit.
