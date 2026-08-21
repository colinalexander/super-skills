# Accounts and capabilities

## Discover before acting

Determine which connector, CLI, or API is actually available and whether it supports the requested operation. Check platform and version prerequisites, authentication state, required local permissions, and known limitations. Prefer capability discovery or help/schema output to recalled syntax.

## Resolve identity explicitly

Identify the active account, tenant, workspace, device, and locale. Resolve recipients and resources with stable identifiers where possible. If a label matches multiple targets, stop before mutation and disambiguate.

Treat local operating-system access, application automation permission, service authentication, and object-level permission as separate grants. Never print tokens, session cookies, or sensitive configuration. Ask only for the minimum additional authorization needed for the requested action.
