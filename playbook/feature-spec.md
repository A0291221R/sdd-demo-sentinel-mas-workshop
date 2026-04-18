---
name: feature-spec
description: Kicks off a new feature from specs/roadmap.md. In default mode, picks the next incomplete phase. In MVP mode, synthesizes a spec across all roadmap phases. Trigger on "feature spec", "next phase", "start the next feature", "mvp spec", "mvp branch", or /feature-spec.
---

# Feature Spec

## Variants

Run as `/feature-spec` for the next single phase (default).
Run as `/feature-spec mvp` to synthesize an MVP spec across all roadmap phases.

---

## Default mode

### 1. Find the next phase

Read `specs/roadmap.md`. The next phase is the first section whose items are all `[ ]`. Note its name to derive the branch and directory name.

### 2. Create the branch

```
git checkout -b phase-N-<kebab-name>
```

### 3. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions per call**, up to 2 rounds:

| Round | Focus |
|-------|-------|
| 1 | **Scope** — fields, behaviour, data shape. **Decisions** — storage, visibility, validation, UX pattern. **Context** — tone, stack limits, open questions. |
| 2 (only if needed) | Unresolved ambiguities from round 1 |

Do not write any files until the user has answered.

### 4. Read guidance files

Read `specs/mission.md`, `specs/tech-stack.md`, and any existing `specs/*/requirements.md` before drafting.

### 5. Create the spec directory

Get today's date via `date +%Y-%m-%d`. Name: `specs/YYYY-MM-DD-<feature-name>/`

#### `requirements.md`
- Scope: what is and is not included; field/data table if applicable
- Decisions: choices made and why
- Context: tone rules, stack pointers, existing patterns to follow

#### `plan.md`
- Numbered task groups (e.g. Data → Components → Page & Route → Navigation → Tests)
- Each group has numbered sub-tasks; groups should be independently implementable

#### `validation.md`
- Automated: tests and typecheck pass; specific assertions required
- Manual: walkthrough, behaviour, edge cases
- Tone check if user-facing copy is involved
- Definition of done

### 6. Update CHANGELOG.md

Open `CHANGELOG.md` at the project root. Create the file if it doesn't exist.
Ensure an `## Unreleased` section exists at the top. Append under it:

```
### phase-N-<feature-name> — YYYY-MM-DD
- Branch: `phase-N-<feature-name>`
- Spec: `specs/YYYY-MM-DD-<feature-name>/`
- Status: in progress
```

---

## MVP mode — `/feature-spec mvp`

### 1. Read the full roadmap and existing specs

Read `specs/roadmap.md` in full. Read all existing `specs/*/requirements.md` for context.

### 2. Create the branch

```
git checkout -b mvp
```

### 3. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions per call**, up to 2 rounds:

| Round | Focus |
|-------|-------|
| 1 | **MVP scope** — which phases are must-have vs nice-to-have? **Constraints** — timeline, team size, quality bars? **Definition of done** — what does shippable mean for this project? |
| 2 (only if needed) | Borderline features within phases that need a final in/out call |

Do not write any files until the user has answered.

### 4. Read guidance files

Read `specs/mission.md` and `specs/tech-stack.md` before drafting.

### 5. Create the spec directory

Get today's date via `date +%Y-%m-%d`. Name: `specs/YYYY-MM-DD-mvp/`

#### `requirements.md`
- In/out scope table covering every roadmap phase
- For each included phase: which subset of features is required for MVP
- Decisions: rationale for what was cut and why
- Context: constraints and definition of shippable

#### `plan.md`
- Task groups organised by roadmap phase
- Each group marked **[MVP]** or **[post-MVP]**
- MVP sub-tasks numbered and independently implementable
- Post-MVP items listed but not broken down

#### `validation.md`
- Automated: tests and typecheck pass; assertions per included phase
- Manual: end-to-end MVP user journey walkthrough
- Pass criteria for each included phase
- Definition of done: what must be true before MVP can be merged and shipped

### 6. Update CHANGELOG.md

Open `CHANGELOG.md` at the project root. Create the file if it doesn't exist.
Ensure an `## Unreleased` section exists at the top. Append under it:

```
### mvp — YYYY-MM-DD
- Branch: `mvp`
- Spec: `specs/YYYY-MM-DD-mvp/`
- Included phases: <comma-separated list of MVP phases>
- Status: in progress
```

---

## Constraints (both modes)

- Respect `specs/tech-stack.md` — no new dependencies without user approval
- Follow existing conventions and patterns in the codebase
- Reference existing `specs/*/` rather than restating covered ground
- Keep scope focused and independently shippable