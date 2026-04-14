---
name: operations-output-to-drive
description: Upload agent output files to Google Drive with idempotent manifests, hourly reconciliation, and 7-day local GC. Use this skill when an agent task produces files in an outputs/ directory that need to be synced to the Paperclip shared drive. Covers post-task upload hook, hourly catch-up reconciliation, and daily garbage collection.
author: Dan Groch
license: MIT
---

# Output-to-Drive Pipeline

Implements the approved output workflow for Paperclip agents:

1. Generate a per-issue artifact manifest with checksums.
2. Upload outputs to the shared drive at `09 - Shared Resources/Cross-Team Projects/<Project>/Outputs/<ISSUE-ID>/`.
3. Hourly reconciliation to catch anything the event path missed.
4. Daily GC: move uploaded files to `.trash/<ISSUE-ID>/` then hard-delete after 7 days.

This skill is project-agnostic. Set `OUTPUT_PROJECT_NAME` to match your project and the pipeline will handle the rest.

---

## Requirements

- `node` 18+
- `gws` CLI installed and authenticated (see **GWS Credential Setup** below)
- Access to the Paperclip shared drive (`0AFJ_DrnFD4bbUk9PVA`)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OUTPUT_PROJECT_NAME` | *(required)* | Drive folder name under `Cross-Team Projects/` |
| `OUTPUTS_DIR` | `outputs` | Local directory where agent output subdirs live |
| `OUTPUT_RETENTION_DAYS` | `7` | Days before `.trash` snapshots are hard-deleted |
| `PAPERCLIP_SHARED_DRIVE_ID` | `0AFJ_DrnFD4bbUk9PVA` | Shared drive ID |
| `PAPERCLIP_SHARED_RESOURCES_FOLDER_ID` | `1NT15AiujwHllLu0dlr2Exy_BGD88kErJ` | Drive folder ID for `09 - Shared Resources` |
| `OUTPUT_GWS_CONFIG_DIR` | value of `GWS_USER_ADMIN` | Override the gws config directory for Drive access |
| `GWS_USER_ADMIN` | *(none)* | Standard profile path for admin gws credentials — used if `OUTPUT_GWS_CONFIG_DIR` is unset |

---

## GWS Credential Setup

This skill uses the `gws` CLI with the `GWS_USER_ADMIN` credential profile by default. This profile must be pre-configured and authorised for Google Drive access on the Paperclip shared drive.

**To use the default profile:**

```bash
# Verify gws is authenticated
gws drive about --params '{"fields": "user"}' --format json
```

**To override the profile for a specific agent:**

```bash
export OUTPUT_GWS_CONFIG_DIR=/path/to/agent-specific-gws-config
```

**Never set `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` directly.** The pipeline clears that variable before invoking `gws` to prevent credential confusion. Always use `OUTPUT_GWS_CONFIG_DIR` or `GWS_USER_ADMIN`.

---

## Installation

Copy the `scripts/` directory from this skill into your project's `scripts/output-pipeline/` (or any path you prefer):

```bash
cp -r skills/operations/operations-output-to-drive/scripts/ scripts/output-pipeline/
```

Set required env vars in your agent's environment or `.env`:

```bash
OUTPUT_PROJECT_NAME="Your Project Name"
GWS_USER_ADMIN=/path/to/gws-admin-config
```

---

## Commands

**Generate manifest only:**

```bash
node scripts/output-pipeline/create-manifest.mjs ISSUE-123
```

**Upload one issue:**

```bash
node scripts/output-pipeline/upload-issue.mjs ISSUE-123
node scripts/output-pipeline/upload-issue.mjs ISSUE-123 --dry-run
```

**Post-task completion hook (manifest + upload):**

```bash
node scripts/output-pipeline/post-task-hook.mjs ISSUE-123
node scripts/output-pipeline/post-task-hook.mjs ISSUE-123 --dry-run
```

The issue ID can also come from `PAPERCLIP_TASK_IDENTIFIER` or `PAPERCLIP_TASK_ID` env vars automatically.

**Hourly reconciliation:**

```bash
node scripts/output-pipeline/reconcile-hourly.mjs
node scripts/output-pipeline/reconcile-hourly.mjs --dry-run
# Optionally limit to specific issues:
node scripts/output-pipeline/reconcile-hourly.mjs ISSUE-123 ISSUE-456
```

**Daily GC:**

```bash
node scripts/output-pipeline/gc-daily.mjs
node scripts/output-pipeline/gc-daily.mjs --dry-run
```

---

## Integration with Paperclip Agent Tasks

Add the post-task hook to your settings.json hooks config so it fires automatically on task completion:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "node scripts/output-pipeline/post-task-hook.mjs"
          }
        ]
      }
    ]
  }
}
```

Or invoke it explicitly at the end of any task that produces files:

```javascript
// In your agent's task completion logic:
// node scripts/output-pipeline/post-task-hook.mjs $PAPERCLIP_TASK_IDENTIFIER
```

---

## Routine Integration

### Hourly Reconciliation

Catches uploads that were missed by the event-driven path (e.g. agent crash, hook failure).

**Paperclip routine schedule:** `0 * * * *`

```bash
node scripts/output-pipeline/reconcile-hourly.mjs
```

### Daily GC

Moves uploaded issue output folders to `.trash/<ISSUE-ID>/<timestamp>/`, then hard-deletes `.trash` snapshots older than `OUTPUT_RETENTION_DAYS` days.

**Paperclip routine schedule:** `30 2 * * *` (02:30 UTC)

```bash
node scripts/output-pipeline/gc-daily.mjs
```

---

## Drive Folder Structure

Files land at:

```
09 - Shared Resources/
  Cross-Team Projects/
    <OUTPUT_PROJECT_NAME>/
      Outputs/
        <ISSUE-ID>/
          artifact-manifest.json    ← uploaded alongside outputs
          <your output files>
```

---

## Local State Files

Each issue output directory gets two state files:

| File | Purpose |
|---|---|
| `artifact-manifest.json` | Checksums and Drive folder path for all output files |
| `.drive-upload-state.json` | Upload status per file; `readyForLocalGc: true` gates GC eligibility |

These are idempotency guards. Re-running any command is safe — already-uploaded files are skipped.

---

## Assigning This Skill to an Agent

After importing the skill into the company skills library:

```bash
# Import from the repo
POST /api/companies/{companyId}/skills/import
{ "repoUrl": "https://github.com/dgroch/skills.git", "skillName": "operations-output-to-drive" }

# Assign to an agent
POST /api/agents/{agentId}/skills/sync
{ "desiredSkills": ["operations-output-to-drive"] }
```

Or include `desiredSkills: ["operations-output-to-drive"]` when hiring a new agent.

---

## Safety Rules

- **One-way push only.** Local deletes never propagate to Drive.
- **7-day retention** before hard delete (configurable via `OUTPUT_RETENTION_DAYS`).
- GC only runs on issue dirs where `readyForLocalGc === true` in the upload state.
- Dry-run mode (`--dry-run`) is available on all scripts — always test on a new project first.
