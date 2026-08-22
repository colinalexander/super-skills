# Systems and security synthesis matrix

Baseline: 3 ranked hashes, 3 distinct names.

Evidence labels: `vulnerability-scanner`, `powershell-windows`, `bash-linux`.

| Decision area | Retained synthesis | Conflict resolution or added safeguard |
| --- | --- | --- |
| Shell operation | Identify actual shell and use exact, quoted targets | Convenience does not justify ambiguous destructive scope |
| Linux | Diagnose services and resources by layer; verify permission changes with native ownership, mode, and ACL semantics | Restarting or reinstalling is not a default root-cause method |
| PowerShell | Operate on objects, expose safe script semantics, and re-read exact Windows ACL principal, type, rights, inheritance, and propagation after mutation | Formatted text parsing, aliases, and partial ACL matches are excluded from reusable automation |
| Security | Confirm authorized assets, methods, time, and stop conditions | Routine administration never implicitly authorizes scanning or exploitation |
| Attack surface | Include dependencies, delivery pipeline, cloud boundaries, and exceptional states | Generic web checklists are prompts for investigation, not proof of applicability |
| Findings | Verify context, impact, likelihood, controls, and confidence | Scanner output is evidence to triage, not a final vulnerability claim |
| Secrets and privilege | Apply least privilege and keep secrets out of commands/logs | Disabling controls is not a generic troubleshooting step |
| Omission repair | Added recovery, evidence handling, and adjacent-asset boundaries | Low source volume requires conservative safety expansion |

Resulting modes: shell/Linux, PowerShell/Windows, and defensive security assessment.
