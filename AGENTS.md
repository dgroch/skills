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

The daily watchdog runs the executing reconciliation command, not audit-only mode. It checkpoints
tracked changes, rebases or fast-forwards onto current `origin/main`, validates the repository,
pushes a fast-forward `main` update, and verifies remote equality. It must refuse and alert on
unknown untracked files, conflicts, invalid skills, shadows, generated clutter, failed validation,
authentication failure, or a non-fast-forward push.
