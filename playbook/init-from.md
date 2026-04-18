---
name: init-from
description: Bootstrap a new project's specs/ constitution using an existing project as a reference base. Trigger on "new project from", "init from", "base on existing project", or /init-from.
---

# Init From Existing Project

## Workflow

### 1. Read the new project context

Read `README.md` and anything in `docs/` for stakeholder input on the new project.

### 2. Read the base project's constitution

The user will provide a path or repo to the base project. Read its:
- `specs/mission.md`
- `specs/tech-stack.md`  
- `specs/roadmap.md`

Use these as **reference templates**, not as copy-paste. Note what carries over vs what differs.

### 3. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions per call**, up to 2 rounds:

| Round | Focus |
|-------|-------|
| 1 | **Similarity** — what should be inherited from the base (stack, patterns, conventions)? **Divergence** — what is intentionally different (domain, scope, audience)? **Roadmap** — does the phase structure carry over or start fresh? |
| 2 (if needed) | Unresolved ambiguities from round 1 |

Do not write any files until the user has answered.

### 4. Create the constitution

Write `specs/` with:

#### `mission.md`
- New project's own purpose, goals, non-goals
- Note where it shares lineage with the base project if relevant

#### `tech-stack.md`
- Inherited stack decisions (with note: "carried over from <base project>")
- Any deliberate divergences and why

#### `roadmap.md`
- Fresh phase list shaped for this project's scope
- Phases adapted from base project where applicable, new ones added as needed
- All items `[ ]`

## Constraints

- Do not blindly copy the base constitution — every section must be validated against the new project's README
- Flag any base decisions that may not apply and ask before inheriting them
- Keep phases small and independently shippable