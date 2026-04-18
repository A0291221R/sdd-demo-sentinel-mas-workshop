# Mission

_Last updated: 2026-04-19_

## Purpose

Sentinel MAS is a production multi-agent system for security monitoring and
automated remediation. It coordinates specialised AI agents through a central
orchestrator, routes natural language queries to the correct domain agent, and
enforces tool access via an infrastructure-level policy guardrail — not prompt
instructions.

## Goals

- Receive security events from external triggers (CloudWatch alarms, operator
  queries, API calls) and route them to the right specialist agent automatically
- Allow operators to query live security data (tracking, events, SOPs) in
  natural language via a dashboard and REST API
- Enforce strict access control at the tool call boundary so no agent can
  exceed its authorised scope, regardless of prompt content
- Produce auditable records of every tool call, rejection, and remediation
  outcome
- Support non-engineer tuning of agent behaviour (model, temperature, system
  prompt, tools) through declarative configuration — without touching Python

## Non-goals

- Multi-cloud portability — the system is AWS-only by deliberate choice
- General-purpose LLM assistant — every agent has a fixed domain and tool set
- Real-time sub-second latency — at-least-once SQS delivery is acceptable;
  idempotency is enforced in agents
- Self-modifying agent behaviour — agents do not rewrite their own prompts or
  tool access policies at runtime

## Target audience

**Primary:** Security operations teams who need an intelligent, auditable
interface to live security data without writing custom integrations per query.

**Secondary:** Platform engineers maintaining and extending the agent
infrastructure (adding new specialist agents, registering new tools, tuning
policy rules).

## Principles

1. **Security at the boundary** — guardrails are enforced in code at the tool
   call boundary, not in prompts. Prompt-level instructions are not a
   reliable security control.

2. **Configuration over code** — agent behaviour (model, temperature, system
   prompt, tools) is declared in `AGENT_REGISTRY`. Adding a new agent should
   not require new Python logic.

3. **Auditability by default** — every tool call, policy rejection, and
   remediation outcome is written to a structured log. No security action is
   silent.

4. **Small team, managed complexity** — prefer AWS-native services (ECS,
   SQS, RDS, CodeDeploy) over operationally heavier alternatives. The system
   must be runnable by a two-to-three person team.

5. **Independently shippable phases** — each roadmap phase produces a working,
   testable increment. No phase depends on a future phase to be runnable.
