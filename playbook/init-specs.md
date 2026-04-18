---
name: init-specs
description: Bootstraps a new project's specs/ constitution. In default mode, derives the roadmap from scratch. In legacy mode, reads TODO.md as the basis for roadmap phases. Trigger on "init specs", "create constitution", "make specs", "legacy project", or /init-specs.
---

# Init Specs

## Variants

Run as `/init-specs` for a greenfield project.
Run as `/init-specs legacy` for a project with an existing TODO.md.

---

## Default mode

### 1. Read project context

Read `README.md` and anything in `docs/` for stakeholder input.

### 2. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions per call**, up to 2 rounds:

| Round | Focus |
|-------|-------|
| 1 | **Mission** — purpose, goals, non-goals, target audience. **Tech stack** — constraints, preferences, existing decisions. **Roadmap** — what must come first, nice-to-haves, any deadlines. |
| 2 (only if needed) | Unresolved ambiguities from round 1 |

Do not write any files until the user has answered.

### 3. Write the constitution

Get today's date via `date +%Y-%m-%d`.

#### `specs/mission.md`
- Project purpose, goals, non-goals
- Target audience and their needs
- Principles that guide decisions

#### `specs/tech-stack.md`
- Languages, frameworks, tools, and why
- Any constraints or deliberate exclusions

#### `specs/roadmap.md`
- High-level implementation order
- Very small, independently shippable phases
- All items `[ ]`

---

## Legacy mode — `/init-specs legacy`

For projects that already have a codebase and a `TODO.md`.

### 1. Read project context

Read `README.md`, `TODO.md`, and anything in `docs/`.
Note: `TODO.md` is the primary input for roadmap phases — treat its items as the raw material, not as final phase definitions.

### 2. Scan the codebase for tech stack evidence

Look at `package.json`, `requirements.txt`, config files, or any other dependency/tooling files present. Note what's already in use vs what's missing or unclear.

### 3. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions per call**, up to 2 rounds:

| Round | Focus |
|-------|-------|
| 1 | **Mission** — has the project's purpose or target audience shifted from what README says? What's the north star? **Tech stack gaps** — are there dependencies, patterns, or constraints in the codebase not captured in docs? Any tech decisions that need locking down? **Roadmap priorities** — which TODO items are must-do vs abandoned? Should any be reordered or split into smaller phases? |
| 2 (only if needed) | Unresolved ambiguities — e.g. conflicting signals between README and TODO, or unclear ownership of items |

Do not write any files until the user has answered.

### 4. Write the constitution

Get today's date via `date +%Y-%m-%d`.

#### `specs/mission.md`
- Project purpose, goals, non-goals (reconciled with user answers)
- Target audience and their needs
- Note any legacy constraints that shape decisions

#### `specs/tech-stack.md`
- Existing stack discovered from codebase + confirmed by user
- Gaps or decisions that needed clarifying
- Any constraints inherited from the legacy system

#### `specs/roadmap.md`
- Phases derived from `TODO.md`, reordered and split into small shippable units
- Preserve TODO item intent but reframe as discrete phases
- All items `[ ]`
- Post-MVP or deferred items noted at the bottom under `## Deferred`

---

## Constraints (both modes)

- Do not invent tech decisions — only record what is confirmed by the codebase or the user
- Keep phases small and independently shippable
- If README and TODO conflict, surface the conflict in the interview rather than silently resolving it