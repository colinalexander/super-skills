# Suite manifest

The 10 active skills divide work by the decision system required, not by file extension or fashionable tool name.

| Skill | Owns | Routes elsewhere when |
| --- | --- | --- |
| `interface-design` | User-facing interaction, visual language, brand expression, responsive behavior, and standalone visual artifacts | The central problem is backend architecture, document-file mechanics, or game interaction |
| `software-delivery` | How a code change is planned, isolated, tested, debugged, reviewed, and proven complete | The central problem is which application architecture or framework pattern to use |
| `agent-tooling-and-orchestration` | Agent capabilities, skill/tool interfaces, discovery, evaluation, and delegation topology | The agents are merely implementing ordinary application work |
| `application-engineering` | Runtime, framework, API, component, and persistence architecture | The request is principally aesthetic design or delivery-process governance |
| `game-development` | Player experience and game-specific engineering across platforms | The work is a conventional application with no game loop or immersive constraints |
| `reasoning-modes` | Explicitly requested ways of exploring, challenging, reframing, or compressing a response | The request needs a domain workflow but no special interaction mode |
| `systems-and-security` | Shell/OS operation and explicitly scoped defensive security assessment | The task is ordinary application coding or security was not requested |
| `marketing-and-growth` | Market evidence, positioning, pricing, acquisition, conversion, lifecycle, and fundraising decisions | The primary work is visual design, artifact mechanics, or implementation architecture |
| `connected-service-automation` | Safe user-authorized operation of existing messaging, notes, media, file, sharing, and similar services | The task is designing or implementing a reusable connector or tool |
| `data-science-and-ml` | Analytical validity, experiments, learned-model behavior, training, evaluation, and model operations | The task is ordinary deterministic application architecture or delivery process |

## Composition

Skills may compose. Name a primary skill and add only the secondary skill whose decisions materially matter. For example:

- a responsive React page: `interface-design` primary, `application-engineering` secondary;
- a failing FastAPI endpoint: `software-delivery` primary, `application-engineering` secondary;
- a VR build pipeline failure: `game-development` primary, `software-delivery` secondary;
- a security review of a Bash deployment script: `systems-and-security` primary, `software-delivery` secondary;
- an SEO landing-page experiment: `marketing-and-growth` primary, `interface-design` secondary;
- a new calendar integration: `application-engineering` primary, while operating an existing calendar connector uses `connected-service-automation`;
- productionizing a churn model: `data-science-and-ml` primary, `application-engineering` secondary.

Do not invoke every possibly relevant skill. More instructions can create conflicting authorities and weaker execution.

## Deliberately withheld boundary

Document and office-artifact production remains a recognized category boundary, but it has no active public skill. Ten of its 11 retained evidence hashes exactly match historical Anthropic blobs, including eight from the source-available DOCX, PDF, PPTX, and XLSX set. The research record is preserved in [`synthesis-matrices/document-productivity.md`](synthesis-matrices/document-productivity.md), while the installable implementation and evaluation cases are withheld. Other active skills must not absorb document-format mechanics merely to hide this gap.
