# Runtime and frameworks

## Verify the installed reality

Inspect dependency versions, runtime targets, project configuration, and current primary documentation. Do not assume that a remembered framework API, rendering mode, or deployment default still applies.

## Python services

Keep domain logic independent of transport and ORM details. Use explicit types and validation at boundaries. In asynchronous services, avoid blocking the event loop; make cancellation and resource cleanup reliable. Use dependency injection where it clarifies lifetimes, not as ceremony.

## Node.js services

Make promise ownership and error propagation explicit. Bound concurrency, stream large data, handle shutdown signals, and avoid synchronous work on request paths. Validate runtime input despite static types.

## FastAPI and Django

Use supported dependency, validation, transaction, middleware, and lifecycle primitives. Preserve clear separation among request parsing, authorization, domain behavior, and persistence. Test through the framework boundary where routing, serialization, or middleware behavior matters.

## React, Next.js, and React Native

Keep state as local as practical and derive rather than synchronize duplicated values. Make server/client and native/platform boundaries explicit. Avoid effects for pure derivation. Optimize rendering and bundling from profiles, not folklore. Preserve accessibility semantics across web and native controls.
