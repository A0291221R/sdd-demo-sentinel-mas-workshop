# Contributing

Sentinel MAS uses **Spec-Driven Development (SDD)** — a workflow where a
living `specs/` constitution drives every feature from first idea to merged
code. Read this before opening a branch.

---

## The constitution

The `specs/` folder is the source of truth for the project. Before writing
any code, make sure you understand what's in it:

- **`specs/mission.md`** — why the project exists, goals, non-goals, principles
- **`specs/tech-stack.md`** — languages, frameworks, constraints, deliberate exclusions
- **`specs/roadmap.md`** — phases with `[ ]` / `[x]` checkboxes

If `specs/` is empty, run `/init-specs` first (see below).

---

## The workflow

### 1. Start a feature

Run `/feature-spec` in your AI coding agent. It will:
- Read the constitution
- Ask you 3–6 focused questions
- Create a branch (`phase-N-<name>`)
- Generate `specs/YYYY-MM-DD-<name>/` with three files:
  - `requirements.md` — scope, decisions, context
  - `plan.md` — numbered task groups, independently shippable
  - `validation.md` — definition of done

Do not start coding until the spec directory exists.

### 2. Implement

Work through `plan.md` task group by task group. Each group should be
committable independently. Reference `requirements.md` if scope questions
come up during implementation.

### 3. Review

Before opening a PR, run `/review-branch`. Three subagents will analyse
your diff from three perspectives in parallel:
- Correctness and logic
- Design and architecture
- Product and requirements (checked against your spec)

Address the prioritised action items before requesting human review.

### 4. Merge and close

After your PR merges, run `/changelog`. It will:
- Find the matching in-progress entry in `CHANGELOG.md`
- Mark it merged with a summary drawn from your spec
- Commit the update

---

## Playbook commands

The `playbook/` folder contains all workflow commands as plain markdown.
They work with any AI coding agent — paste the file contents as your
instruction prompt, or copy them into `.claude/commands/` for Claude Code
slash command support.

| Command | When to use |
|---------|-------------|
| `/init-specs` | First time setup — generates the `specs/` constitution |
| `/init-specs legacy` | Existing project with a `TODO.md` |
| `/init-from` | New project based on an existing one |
| `/feature-spec` | Starting any new feature or phase |
| `/feature-spec mvp` | Planning an MVP across all roadmap phases |
| `/next-phase` | Quick feature start without the interview |
| `/review-branch` | Before every PR |
| `/changelog` | After every merge |

---

## Ground rules

- **No branch without a spec** — every feature needs a `specs/YYYY-MM-DD-*/` directory
- **No new dependencies without approval** — check `specs/tech-stack.md` first
- **No manual console changes to infrastructure** — Terraform only
- **No secrets in code or environment variables** — Secrets Manager only
- **Specs are living documents** — update `requirements.md` if scope changes during implementation; don't let it drift from reality
