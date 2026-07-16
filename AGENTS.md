# Skills Repository Operating Rules

## Source of truth

This Git repository is the canonical source for every skill below it. Hermes profiles load it directly through `skills.external_dirs`; profile-local directories are not deployment targets for repository-owned skills.

## Mandatory preflight

Before editing any repository-owned skill, run from the repository root:

```bash
python3 tools/skill_repo_guard.py preflight --fetch
```

Do not begin editing until the command is silent and exits zero. Create a task branch from current `origin/main` only after preflight passes.

## Editing and completion

- Edit repository-owned skills only in this repository.
- Never create a profile-local skill with the same frontmatter `name` as a repository skill.
- Keep generated output, dependencies, caches, backups and execution state outside the repository.
- Test, commit, fetch again, reconcile upstream movement and push every durable change.
- Verify `HEAD`, `origin/main` and the GitHub API resolve to the same commit before reporting completion.
- A profile automatically sees the checked-out repository through `skills.external_dirs`; no copy step is required.

## Drift guard

```bash
# Silent when healthy; non-zero with stable alert codes when unhealthy
python3 tools/skill_repo_guard.py audit --fetch

# Automatically resolve safe tracked drift; alert only on unsafe reconciliation
python3 tools/skill_repo_guard.py reconcile --fetch --execute

# Preview duplicate profile shadows
python3 tools/skill_repo_guard.py remove-shadows

# Remove shadows only from a clean repository synchronized with origin/main
python3 tools/skill_repo_guard.py remove-shadows --execute
```

The managed topology is declared in `tools/skill-repo-manifest.json`.

The daily no-agent watchdog runs `reconcile --fetch --execute` and is silent only when the live checkout is clean and equal to verified `origin/main`.

Automatic publication is deliberately narrow: the checkout must be on `main`, there must be no pre-existing local commits, and dirty paths must be unstaged, non-binary modifications to files already owned by an existing skill. Deletions, renames, mode/type changes, untracked or staged paths, guard/config changes, merge commits, conflicts, validation failures, concurrent edits, non-fast-forward pushes, and failed remote readback stop without overwriting the live checkout and produce an alert. Candidate integration and validation occur in an isolated worktree; publication is an exact non-force update to `refs/heads/main`, and live synchronization uses `git reset --keep`.
