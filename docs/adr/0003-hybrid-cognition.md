# ADR 0003 — Hybrid Cloud Cognition, Local Execution

**Status:** Accepted

## Decision

Use provider-neutral model ports. High-ambiguity understanding and strategic planning may route to a frontier cloud model; privacy-sensitive extraction, embeddings and specialized execution may run locally.

## Why

A local model provides privacy, control and low marginal cost, but architecture alone cannot guarantee frontier-level language understanding. Sending the entire personal memory to a cloud model is also unnecessary and unsafe.

## Consequences

- Context selection and redaction happen locally.
- The model router selects by task, risk, privacy and quality requirement.
- A local fallback must lower confidence and may trigger preview or clarification.
- No provider-specific object appears in domain models.
