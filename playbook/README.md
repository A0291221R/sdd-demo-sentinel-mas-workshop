# Playbook

Quick reference for all SDD workflow commands.

These files are plain markdown — not tied to any specific AI coding agent.
To use them: paste the file contents as your instruction prompt, or copy
them into `.claude/commands/` to enable Claude Code slash command support.

---

## Commands

### `/init-specs` — bootstrap the constitution

**File:** `init-specs.md`
**Use when:** Starting a new project, or formalising an existing one.

```
/init-specs            ← greenfield project
/init-specs legacy     ← existing project with a TODO.md
```

Reads `README.md` and `docs/`, interviews you, then writes:
- `specs/mission.md`
- `specs/tech-stack.md`
- `specs/roadmap.md`

---

### `/init-from` — bootstrap from an existing project

**File:** `init-from.md`
**Use when:** Starting a new project that shares lineage with an existing one.

Reads both projects' context, interviews you about what carries over vs what
differs, then writes a fresh `specs/` constitution for the new project.

---

### `/feature-spec` — start a feature

**File:** `feature-spec.md`
**Use when:** Beginning any new feature or roadmap phase.

```
/feature-spec          ← next single phase (default)
/feature-spec mvp      ← MVP spec across all roadmap phases
```

Reads the `specs/` constitution, interviews you, creates a branch, then
generates `specs/YYYY-MM-DD-<feature>/` with:
- `requirements.md` — scope, decisions, context
- `plan.md` — numbered task groups, independently shippable
- `validation.md` — definition of done

---

### `/next-phase` — quick feature start

**File:** `next-phase.md`
**Use when:** You want to start the next phase without a full interview.

Finds the next incomplete phase in `specs/roadmap.md`, creates a branch,
and generates the spec directory. Lighter than `/feature-spec` — good for
phases where scope is already clear.

---

### `/review-branch` — pre-merge code review

**File:** `review-branch.md`
**Use when:** Before opening a PR or merging any branch.

Spawns three subagents to analyse the diff in parallel:
1. Correctness and logic
2. Design and architecture
3. Product and requirements (checked against `specs/`)

Produces a prioritised action item list.

---

### `/changelog` — close a feature after merge

**File:** `changelog.md`
**Use when:** After a feature branch has been merged.

Finds the matching in-progress entry in `CHANGELOG.md`, marks it merged,
adds a summary drawn from the spec, and commits the update.

---

## Workflow at a glance

```
/init-specs            ← one-time project setup
      │
      ▼
/feature-spec          ← start each feature
/next-phase            ← or use this for quick starts
      │
      ▼
  implement
      │
      ▼
/review-branch         ← before every PR
      │
      ▼
/changelog             ← after every merge
```
