# Application engineering synthesis matrix

Baseline: 14 ranked hashes, 13 distinct names.

Evidence labels: `fastapi`, `vercel-composition-patterns`, `supabase-postgres-best-practices`, `vercel-react-best-practices`, `vercel-react-native-skills`, `design-an-interface`, `next-best-practices`, `api-design`, `api-patterns`, `python-patterns`, `nodejs-best-practices`, `database-design`, `django-patterns`.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Architecture | Decompose by capability, state ownership, and directional contracts | Framework file layout does not substitute for system boundaries |
| APIs | Use stable domain language and explicit error/evolution semantics | CRUD purity yields to clearer domain commands where appropriate |
| Data | Enforce durable invariants in the database and design from access paths | Normalize authority; denormalize only for evidenced needs |
| Runtimes | Make blocking, cancellation, errors, and resource lifetimes explicit | Python and Node idioms remain contextual rather than cross-runtime absolutes |
| Frontend | Prefer composition, local state, and explicit runtime boundaries | Optimization follows profiling; effects and memoization are not ritual |
| Boundary correction | Interface option generation is routed to `interface-design`, with agent coordination only when genuinely useful | A source's observed category does not override the suite's decision ownership |
| Hosted platforms | Use native security and lifecycle primitives deliberately | Platform advice must be checked against current primary docs and installed versions |
| Omission repair | Added compatibility, migrations, observability, and failure contracts | Happy-path framework patterns alone are insufficient architecture |

Resulting modes: system architecture, API contracts, data/persistence, and runtime/framework implementation.
