# Shell and Linux

## Respect shell semantics

Identify the actual shell before relying on syntax. Quote paths and expansions, handle spaces and newlines, and avoid parsing human-formatted output when a machine-readable interface exists. Use strict modes only after checking how expected nonzero statuses and unset variables should behave.

## Diagnose by layer

For a failing service, inspect process state, service-manager status, recent logs, configuration, permissions, listening sockets, dependencies, resource pressure, and upstream/downstream reachability. Change the first layer with causal evidence rather than restarting everything.

## Manage files and packages narrowly

Resolve exact paths and inspect ownership, links, mounts, and available space before mutation. Use the platform package manager and repository policy. Avoid recursive permission changes and global package installs unless they are the intended scope.

## Script for repeatability

Make inputs explicit, validate them, use meaningful exit codes, clean up temporary resources, and keep repeated runs safe. Separate informational output from structured results when another program consumes the script.
