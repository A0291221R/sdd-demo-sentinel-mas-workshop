---
name: changelog
description: Updates CHANGELOG.md when a branch is merged. Finds the matching in-progress entry and marks it done with a summary. Trigger on "update changelog", "close changelog", "mark merged", or /changelog.
---

# Changelog

## Workflow

### 1. Identify the branch

Run `git branch --show-current` to get the current branch name.
If not on a feature or mvp branch, ask the user which branch was just merged.

### 2. Read context

Read `CHANGELOG.md` and find the entry whose branch matches.
Read the corresponding `specs/YYYY-MM-DD-<feature-name>/requirements.md` and `validation.md` for a summary of what shipped.

### 3. Update the entry

Replace the matched entry's `Status: in progress` line with:

`````
- Status: merged
- Summary: <1-2 sentence description of what was built, drawn from requirements.md>
`````

Move the updated entry from `## Unreleased` into a dated release section:

`````
## YYYY-MM-DD

### <feature-name or mvp>
- Branch: `...`
- Spec: `specs/.../`
- Status: merged
- Summary: ...
`````

Leave `## Unreleased` in place (empty) for future entries.

### 4. Commit the changelog

`````
git add CHANGELOG.md
git commit -m "changelog: close <feature-name>"
`````

## Constraints

- Never delete or rewrite existing merged entries
- Keep summaries factual and brief — drawn from the spec, not invented
- Date format is always YYYY-MM-DD via `date +%Y-%m-%d`