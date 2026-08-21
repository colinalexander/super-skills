# Data and persistence

## Model invariants in the database

Use types, nullability, unique constraints, foreign keys, and checks to express rules that must survive every application path. Normalize authoritative transactional data; denormalize intentionally for measured read or reporting needs.

## Query for the access path

Start from real query shapes and cardinality. Select only required fields, avoid unbounded scans and N+1 access, and use indexes that match filters, joins, and ordering. Confirm improvements with query plans and representative data.

## Use transactions around invariants

Choose transaction boundaries that preserve business correctness. Account for concurrent writers and select an isolation or locking strategy deliberately. Avoid holding database transactions open across slow remote calls.

## Evolve safely

Use reversible or forward-compatible migrations where possible: expand schema, deploy compatible code, backfill observably, switch reads/writes, then contract. Plan for large-table locking, retries, and rollback limitations.

## Hosted Postgres and access control

Treat row-level security and database roles as authorization boundaries, not optional filtering. Test policies with multiple roles. Keep privileged credentials server-side and scope them narrowly. Verify platform-specific recommendations against current primary documentation.
