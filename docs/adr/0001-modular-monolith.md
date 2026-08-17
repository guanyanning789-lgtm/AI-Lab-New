# ADR 0001 — Modular Monolith First

**Status:** Accepted

## Decision

AI Lab OS starts as one deployable Python application with explicit internal modules and ports/adapters.

## Why

The primary risk is product and cognitive complexity, not horizontal scale. A distributed design would add deployment, network, versioning and consistency problems before the understanding loop is proven.

## Consequences

- One process may host API and orchestration initially; workers may be separate processes when required.
- Domain models cannot import concrete framework or provider adapters.
- Modules may be extracted later only after a measured scaling or isolation need.
