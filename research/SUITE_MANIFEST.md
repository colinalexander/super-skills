# Suite manifest

The eight skills divide work by the decision system required, not by file extension or fashionable tool name.

| Skill | Owns | Routes elsewhere when |
| --- | --- | --- |
| `interface-design` | User-facing interaction, visual language, brand expression, responsive behavior, and standalone visual artifacts | The central problem is backend architecture, document-file mechanics, or game interaction |
| `software-delivery` | How a code change is planned, isolated, tested, debugged, reviewed, and proven complete | The central problem is which application architecture or framework pattern to use |
| `agent-tooling-and-orchestration` | Agent capabilities, skill/tool interfaces, discovery, evaluation, and delegation topology | The agents are merely implementing ordinary application work |
| `application-engineering` | Runtime, framework, API, component, and persistence architecture | The request is principally aesthetic design or delivery-process governance |
| `document-productivity` | Creating, editing, converting, and validating office and knowledge artifacts | The artifact is a product UI or ordinary source-code module |
| `game-development` | Player experience and game-specific engineering across platforms | The work is a conventional application with no game loop or immersive constraints |
| `reasoning-modes` | Explicitly requested ways of exploring, challenging, reframing, or compressing a response | The request needs a domain workflow but no special interaction mode |
| `systems-and-security` | Shell/OS operation and explicitly scoped defensive security assessment | The task is ordinary application coding or security was not requested |

## Composition

Skills may compose. Name a primary skill and add only the secondary skill whose decisions materially matter. For example:

- a responsive React page: `interface-design` primary, `application-engineering` secondary;
- a failing FastAPI endpoint: `software-delivery` primary, `application-engineering` secondary;
- a branded presentation: `document-productivity` primary, `interface-design` secondary;
- a VR build pipeline failure: `game-development` primary, `software-delivery` secondary;
- a security review of a Bash deployment script: `systems-and-security` primary, `software-delivery` secondary.

Do not invoke every possibly relevant skill. More instructions can create conflicting authorities and weaker execution.
