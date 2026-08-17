# ADR 0002 — IntentContract Is the Planning Boundary

**Status:** Accepted

## Decision

Raw user text and unverified memory cannot be sent directly to planning or execution. The Understanding Kernel must first produce a validated `IntentContract` with evidence, assumptions, success criteria, risk and autonomy mode.

## Why

Natural language is ambiguous. Tool execution based only on text or keyword classification makes hidden assumptions impossible to inspect and unsafe to automate.

## Consequences

- Planner interfaces accept `IntentContract`, not `str`.
- Contract schema changes require contract tests and eval migration.
- UI can show the user what the system understood without exposing internal model reasoning.
