# Sentinel MAS

A multi-agent security monitoring and remediation system — and a working
demonstration of **Spec-Driven Development (SDD)** using Claude Code.

---

## What this project demonstrates

This repository serves two purposes:

1. **A real system** — Sentinel MAS coordinates specialised AI agents for
   security monitoring, intent routing, and automated remediation, deployed
   on AWS ECS Fargate.

2. **A workshop reference** — the project structure shows how to use SDD
   with Claude Code: a development workflow where a living `specs/`
   constitution drives every feature from first idea to merged code.

---

## Spec-Driven Development (SDD)

SDD is a workflow pattern where Claude Code commands read a set of project
constitution files before doing any work. This keeps every generated spec,
plan, and implementation grounded in your project's actual goals, constraints,
and progress — rather than producing generic output.

### The constitution (`specs/`)

| File | Purpose |
|------|---------|
| `specs/mission.md` | Why the project exists, goals, non-goals, principles |
| `specs/tech-stack.md` | Languages, frameworks, constraints, deliberate exclusions |
| `specs/roadmap.md` | Phases with `[ ]` / `[x]` checkboxes — source of truth for progress |

### The commands (`playbook/`)

| Command | Trigger | What it does |
|---------|---------|--------------|
| `/init-specs` | Greenfield project | Reads `README.md` + `docs/`, interviews you, generates `specs/` |
| `/init-specs legacy` | Existing project | Reads `TODO.md` + codebase, generates `specs/` from what exists |
| `/init-from` | New project from existing | Inherits constitution from a base project, adapts for new context |
| `/feature-spec` | Start a feature | Reads constitution, interviews you, creates branch + spec directory |
| `/feature-spec mvp` | MVP planning | Synthesises a spec across all roadmap phases |
| `/next-phase` | Quick feature start | Lightweight version of `/feature-spec` — no interview |
| `/review-branch` | Before merging | Multi-perspective code review against specs |
| `/changelog` | After merge | Closes the CHANGELOG entry for the merged feature |

### The workflow

```
/init-specs                    ← greenfield project
/init-specs legacy             ← existing project with TODO.md
/init-from                     ← new project based on existing one
      │
      ▼
/feature-spec                  ← start a feature (full, with interview)
/feature-spec mvp              ← MVP spec across all phases
/next-phase                    ← start a feature (quick, no interview)
      │
      ▼
  implement
      │
      ▼
/review-branch                 ← review before merging
      │
      ▼
/changelog                     ← close the entry after merge
```

### Why it works

Claude reads `specs/mission.md` before writing requirements — so it knows
not to suggest features that conflict with your non-goals. It reads
`specs/tech-stack.md` before suggesting implementations — so it never
recommends a library you've deliberately excluded. It reads `specs/roadmap.md`
to find the next incomplete phase — so you always work in the right order.

The `docs/` folder feeds `/init-specs`. The `specs/` folder feeds
`/feature-spec`. Each layer builds on the last.

---

## Sentinel MAS — system overview

Sentinel MAS uses a **router + tool use** architecture built on LangGraph,
with agent configuration following a CrewAI-inspired template pattern that
separates prompts from code.

### Services

| Service | Language | Purpose |
|---------|----------|---------|
| `central` | Python 3.11 | Orchestrator — routes intents, manages agent lifecycle |
| `api` | Python 3.11 / FastAPI | REST interface for the UI and external consumers |
| `ui` | TypeScript / React 18 | Operator dashboard |

### Agent routing

```
Incoming query
     │
     ▼
  Router node  ──── intent: TRACKING  ──▶  Tracking Agent
               ──── intent: EVENTS    ──▶  Event Agent
               ──── intent: SOP       ──▶  FAQ / SOP Agent
```

### Key innovations

**Sentinel policy** — a guardrail layer that enforces tool access control at
the infrastructure level, not in the prompt. Every tool call is authenticated,
authorised, and rate-limited before it executes.

**Agent templates** — agents are defined declaratively in `AGENT_REGISTRY`.
Model, temperature, system prompt, and tools are configuration — not code.
Non-engineers can tune agent behaviour without touching Python.

---

## Project structure

```
sentinel-mas/
├── README.md                        ← you are here
├── CHANGELOG.md                     # Auto-maintained by /feature-spec + /changelog
│
├── playbook/                        # SDD workflow commands (agent-agnostic)
│   ├── init-specs.md                # /init-specs — bootstrap specs/
│   ├── init-from.md                 # /init-from — bootstrap from existing project
│   ├── feature-spec.md              # /feature-spec — start a feature
│   ├── next-phase.md                # /next-phase — lightweight feature start
│   ├── review-branch.md             # /review-branch — pre-merge review
│   └── changelog.md                 # /changelog — close a feature
│
├── specs/                           # Living project constitution (generated by /init-specs)
│   ├── mission.md                   # Why, goals, principles
│   ├── tech-stack.md                # How, constraints, exclusions
│   └── roadmap.md                   # What, phases, progress
│
├── docs/                            # Architecture and operational docs
│   ├── architecture.md              # System design and decisions
│   ├── deployment.md                # Deploy, rollback, promote
│   ├── runbook.md                   # On-call incident procedures
│   ├── local-dev.md                 # Local setup guide
│   └── adr/                         # Architecture Decision Records
│       ├── 001-ecs-over-k8s.md
│       └── 002-sentinel-policy-as-infrastructure.md
│
├── services/
│   ├── api/                         # FastAPI service
│   ├── ui/                          # React operator dashboard
│   └── central/                     # Orchestrator + agent registry
│       ├── agents/
│       │   ├── crew_agents.py       # Agent template definitions
│       │   └── crew.py              # LangGraph graph
│       ├── state/
│       │   └── graph_state.py       # Shared TypedDict state
│       └── policy/
│           └── sentinel_policy.py   # Tool access guardrail
│
├── infra/
│   └── terraform/
│       ├── modules/                 # networking, iam, rds, alb, ecs, codedeploy
│       └── environments/            # dev, prod
│
└── docker-compose.yml               # Local development stack
```

---

## Quick start

### Prerequisites

- Docker Desktop 24+
- Python 3.11+
- Node.js 20 LTS
- AWS CLI 2.x (for deployment)
- Terraform 1.6+ (for infrastructure)

### Run locally

```bash
git clone https://github.com/<your-org>/sentinel-mas
cd sentinel-mas
make setup          # creates .env and symlinks playbook/ → .claude/commands/
docker compose up
```

| Service | URL |
|---------|-----|
| UI dashboard | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| API health | http://localhost:8000/health |

See [docs/local-dev.md](docs/local-dev.md) for the full local setup guide.

### Run tests

```bash
make test
```

### Deploy

Deployments trigger automatically on merge to `main`. See
[docs/deployment.md](docs/deployment.md) for manual steps, rollback, and
production promotion.

---

## Documentation

| Doc | What it covers |
|-----|---------------|
| [docs/architecture.md](docs/architecture.md) | System design, agent architecture, data flow, key decisions |
| [docs/deployment.md](docs/deployment.md) | Normal deploy, rollback, promote to prod, smoke tests |
| [docs/runbook.md](docs/runbook.md) | On-call: symptoms → diagnosis → remediation |
| [docs/local-dev.md](docs/local-dev.md) | Local setup, seeding, common issues |
| [docs/adr/](docs/adr/) | Architecture Decision Records |
| [specs/mission.md](specs/mission.md) | Product goals and principles *(generated by `/init-specs`)* |
| [specs/tech-stack.md](specs/tech-stack.md) | Technical constraints and decisions *(generated by `/init-specs`)* |
| [specs/roadmap.md](specs/roadmap.md) | Phase tracking and progress *(generated by `/init-specs`)* |
| [playbook/](playbook/) | SDD workflow commands — agent-agnostic |

---

## Workshop: try the SDD workflow

If you are using this repository as a workshop reference, here is the
suggested sequence to see SDD in action:

1. **Bootstrap the constitution** — run `/init-specs` in Claude Code (or paste
   `playbook/init-specs.md` as your prompt in any AI coding agent). Watch it
   read this `README.md` and `docs/`, ask you a few focused questions, then
   generate `specs/mission.md`, `specs/tech-stack.md`, and `specs/roadmap.md`.

2. **Start a feature** — run `/feature-spec`. Watch it read the constitution,
   interview you, create a branch, and produce a complete
   `specs/YYYY-MM-DD-*/` directory with `requirements.md`, `plan.md`, and
   `validation.md`.

3. **Inspect the output** — note how `requirements.md` respects the non-goals
   in `mission.md` and how `plan.md` avoids libraries excluded in
   `tech-stack.md`. The constitution is doing the work.

4. **Review before merge** — run `/review-branch`. Three subagents analyse
   the diff from correctness, design, and product perspectives in parallel.

5. **Close the loop** — run `/changelog` after merging. The CHANGELOG entry
   closes automatically with a summary drawn from the spec.

### Using the playbook with other AI agents

The `playbook/` commands are plain markdown — not tied to Claude Code. To use
them with Cursor, Copilot, Windsurf, or any other agent: open the relevant
file and paste its contents as your instruction prompt. The workflow is
identical; only the trigger mechanism differs.

To use with Claude Code specifically, copy the files into `.claude/commands/`
to enable slash command auto-triggering.

---

## Status

> Update the badge URLs below after creating your GitHub repository.

![CI](https://github.com/<your-org>/sentinel-mas/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/<your-org>/sentinel-mas/actions/workflows/deploy.yml/badge.svg)
