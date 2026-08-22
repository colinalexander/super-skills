# PowerShell and Windows

## Work with objects

Use cmdlets and object properties rather than parsing formatted tables. Quote paths, prefer literal-path parameters when names may contain wildcard characters, and make error behavior explicit. Avoid aliases in reusable scripts.

## Inspect the right subsystem

Use the service manager, event logs, scheduled tasks, registry, ACLs, network stack, package source, or performance counters according to the symptom. Confirm whether the session is Windows PowerShell or PowerShell and which architecture and privilege context it uses.

## Change safely

Read the current value and export or record recovery information before registry, policy, ACL, service-startup, firewall, or boot changes. Scope remoting commands to verified hosts and avoid placing secrets in script text or transcript output.

After changing an ACL, re-read it on every target and verify the exact principal, rights, inheritance, and access type. A constructed rule or successful `Set-Acl` return is not independent verification.

## Write reliable automation

Use advanced-function parameter validation where appropriate, structured output, terminating errors for unrecoverable failures, and `ShouldProcess` support for impactful changes. Test paths with spaces, empty pipeline input, partial failures, and reruns.
