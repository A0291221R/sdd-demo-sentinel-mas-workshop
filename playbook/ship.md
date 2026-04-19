---
name: ship
description: Commits changes, merges the branch, deletes it only after verifying the merge succeeded, then updates CHANGELOG.md. Trigger on "ship", "ship it", "merge and close", "commit and merge", or /ship.
---

# Ship

Commits the current branch, merges it into the base branch, verifies the
merge, deletes the branch only if verification passes, then closes the
CHANGELOG entry.

---

## Workflow

### 1. Pre-flight checks

Before touching git, verify the branch is ready to ship:

```bash
git status
git diff --stat
```

- If there are untracked or unstaged files, ask the user whether to include them before proceeding.
- If the working tree is clean, skip to step 2.
- Do not proceed if there are merge conflicts.

### 2. Commit

Stage and commit all changes:

```bash
git add -A
git commit -m "<message>"
```

Derive the commit message from the current branch name and the spec in
`specs/YYYY-MM-DD-<feature-name>/requirements.md` if it exists.

Commit message format:

```
<type>(<scope>): <short summary>

<optional body — 1-2 sentences from requirements.md scope section>
```

Where `<type>` is one of: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.
Keep the subject line under 72 characters.

Ask the user to confirm the commit message before running `git commit`.

### 3. Identify the base branch

```bash
git remote show origin | grep "HEAD branch"
```

The base branch is typically `main`. Confirm with the user if ambiguous.

### 4. Merge

Switch to the base branch and merge:

```bash
git checkout <base>
git pull origin <base>
git merge --no-ff <feature-branch> -m "merge: <feature-branch>"
git push origin <base>
```

Use `--no-ff` to preserve the merge commit and keep history readable.

### 5. Verify the merge

Confirm the feature branch commits are present in the base branch:

```bash
git log <base> --oneline | head -10
git branch --merged <base> | grep <feature-branch>
```

**Only proceed to step 6 if both checks pass** — the feature branch must
appear in `git branch --merged`. If verification fails, stop and report
the failure to the user. Do not delete the branch.

### 6. Delete the branch

Only runs if step 5 verification passed.

```bash
git branch -d <feature-branch>
git push origin --delete <feature-branch>
```

Use `-d` (not `-D`) — this is a safety check that refuses deletion if the
branch is not fully merged.

### 7. Update CHANGELOG.md

Read `CHANGELOG.md` and find the entry matching the shipped branch.
Read `specs/YYYY-MM-DD-<feature-name>/requirements.md` for the summary.

Replace the matched entry's status line:

```
- Status: in progress
```

with:

```
- Status: merged
- Summary: <1-2 sentences drawn from requirements.md>
```

Move the entry from `## Unreleased` into a dated release section:

```markdown
## YYYY-MM-DD

### <feature-name>
- Branch: `<feature-branch>`
- Spec: `specs/YYYY-MM-DD-<feature-name>/`
- Status: merged
- Summary: ...
```

Get today's date via `date +%Y-%m-%d`.
Leave `## Unreleased` in place (empty) for future entries.

### 8. Commit the changelog

```bash
git add CHANGELOG.md
git commit -m "changelog: close <feature-name>"
git push origin <base>
```

### 9. Confirm

Report back to the user:

```
✓ committed: <commit message>
✓ merged:    <feature-branch> → <base>
✓ verified:  branch found in git log
✓ deleted:   <feature-branch> (local + remote)
✓ changelog: <feature-name> marked merged
```

---

## Constraints

- Never delete the branch before verifying the merge — step 5 is a hard gate
- Never use `git merge --ff-only` — the no-ff merge commit is required
- Never use `-D` for branch deletion — only `-d`
- Never invent the commit message — derive it from the branch name and spec
- If no CHANGELOG entry exists for the branch, create one before closing it
- If the spec directory does not exist, summarise from the branch name and commit message instead
