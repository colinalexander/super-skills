# Agent tooling and orchestration synthesis matrix

Baseline: 16 ranked hashes, 10 distinct names.

Evidence labels: `mcp-builder`, `skill-creator`, `dispatching-parallel-agents`, `writing-skills`, `find-skills`, `using-superpowers`, `write-a-skill`, `setup-matt-pocock-skills`, `skill-installer`, `subagent-driven-development`.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Skill creation | Design from triggers, outcomes, resources, and evals | More instructions are not presumed better; progressive loading controls context |
| Tool design | Expose task-level, typed, side-effect-aware contracts | Neither endpoint-per-tool nor one universal tool is a default |
| Orchestration | Delegate bounded independent work with explicit outputs | The coordinator retains integration and final accountability |
| Discovery | Match capability, trust, dependencies, and permissions | Keyword match and popularity are insufficient selection evidence |
| Installation | Explain and validate the installed capability | Discovery never implies permission to install or run bundled code silently |
| Evaluation | Compare baseline behavior and test boundaries/failures | Task quality includes avoiding excess invocation and side effects |
| Omission repair | Added authorization preservation and retry/stop rules | Agents and tools cannot widen user authority |

Resulting modes: skill lifecycle, tool-interface design, orchestration, and capability discovery/installation.
