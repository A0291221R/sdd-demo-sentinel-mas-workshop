# ADR 002 — Sentinel policy as infrastructure guardrail, not prompt instruction

**Date:** 2025-10-15
**Status:** Accepted

---

## Context

Sentinel MAS agents can call tools that interact with live security systems:
tracking APIs, event databases, and knowledge bases. The system needed a way
to prevent unauthorised tool access — for example, the FAQ/SOP agent should
not be able to call the Sentinel Server tracking API.

Two approaches were considered:

1. **Prompt-level instructions** — tell each agent in its system prompt which
   tools it is and is not allowed to call
2. **Infrastructure-level policy** — enforce access control at the tool call
   boundary in code, before the tool executes

## Decision

Implement **Sentinel policy as an infrastructure layer** that intercepts all
tool calls and enforces access control, rate limiting, and authentication
before execution.

## Reasoning

Prompt instructions are not reliable security boundaries. An LLM may ignore,
misinterpret, or be manipulated into bypassing prompt-level restrictions —
particularly via adversarial inputs in the query or tool results. This is
well-documented as prompt injection.

An infrastructure guardrail operates at the code boundary. The tool function
never executes if the policy rejects the call. This is analogous to enforcing
authorisation in middleware rather than in application logic.

Infrastructure enforcement also produces structured rejection records that
are loggable and auditable. Prompt-level failures produce unstructured LLM
output that is harder to monitor and alert on.

The cost is additional code complexity and a new abstraction layer that
developers must understand when adding tools. This is acceptable given the
security requirements.

## Consequences

- Every new tool must be registered with a permitted agent list in the policy
  configuration
- Policy rejections are logged as structured `PolicyRejection` events with
  agent, tool, and reason fields — these feed CloudWatch alarms
- The policy layer adds one function call to every tool invocation (~0ms overhead)
- Developers cannot bypass the guardrail by editing a prompt — changes require
  a code change, review, and deployment
