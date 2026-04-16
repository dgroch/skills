---
name: workforce-employee-offboarding
description: Offboard a departing employee at Fig & Bloom — save resignation notice,
  send formal acknowledgement, revoke platform access, and schedule Deputy archival.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Offboarding, HR, People & Culture, Workforce]
    related_skills: [workforce-employee-onboarding, reference-google-drive, gws-shared, gws-gmail, workforce-deputy-connector]
---

# Employee Offboarding

## When to use this skill
Use this skill whenever someone asks to offboard an employee, process a resignation, handle someone leaving, or any variation of "we have someone departing." Also triggers for partial offboarding steps like "remove [name] from Trello", "acknowledge [name]'s resignation", or "send [name] their resignation acknowledgement." If a Paperclip issue is assigned with offboarding context (name, resignation details), treat it as a trigger.

## Dependencies

- **`gws` CLI** — Google Workspace CLI (`@googleworkspace/cli`). Must be on
  PATH. Used for all Gmail and Google Drive operations.
- Read the `gws-shared` skill for auth, global flags, and security rules.
- Read the `gws-gmail` skill for Gmail command reference.
- Read the `workforce-deputy-connector` skill for Deputy API reference (used in the deferred archival issue).


## Inputs

Collect all of the following before starting. If any required fields are missing, ask for them.

| Field                | Required    | Format / Values                                                          |
|----------------------|-------------|--------------------------------------------------------------------------|
| Full name            | Yes         | First Last                                                               |
| Email                | Yes         | Employee's email address (usually personal — most don't have @figandbloom.com) |
| City                 | Yes         | `melbourne`, `sydney`, or `brisbane`                                     |
| Resignation date     | Yes         | YYYY-MM-DD — the date the resignation was given                          |
| Final working date   | Optional    | YYYY-MM-DD — if stated in the resignation; otherwise defaults to resignation date + 7 days |
| Resignation source   | Yes         | `email`, `slack`, or `other`                                             |
| Resignation content  | Conditional | Required if source is `slack` or `other` — paste/type the resignation text |

### Deriving the final working date

If `final_working_date` is not provided as an input:
1. Check the resignation text for any mention of a final date, last day, or end date.
2. If found, use that date.
3. If not found, default to `resignation_date + 7 days`.


## Process

Execute steps in this order. Each step should be attempted regardless of whether
a previous step failed — do not stop the entire process because one integration
is down. Track pass/fail per step.

### Step 1 — Retrieve or capture resignation notice

Branches on `resignation_source`:

#### Source: email

The resignation may have been sent to `admin@figandbloom.com.au` or `kellie@figandbloom.com`. Search **both** inboxes.

**Important:** The `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var is set globally and takes precedence over `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`. Always unset it when using a profile-based config:

1. Search Kellie's inbox (`$GWS_USER_KELLIE`):
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_KELLIE \
     gws gmail users messages list \
     --params '{"userId": "me", "q": "from:{email} (resign OR resignation OR leaving OR notice OR last day)", "maxResults": 10}'
   ```

2. Search Admin inbox (`$GWS_USER_ADMIN`):
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
     gws gmail users messages list \
     --params '{"userId": "me", "q": "from:{email} (resign OR resignation OR leaving OR notice OR last day)", "maxResults": 10}'
   ```

3. If found in one inbox, read the full thread. Record **which inbox** received it — this determines which address sends the acknowledgement in Step 4.
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_{KELLIE_OR_ADMIN} \
     gws gmail users threads get \
     --params '{"userId": "me", "id": "{thread_id}"}'
   ```

4. If found in both inboxes, prefer the most recent thread.

5. If not found in either inbox, broaden the search — remove keywords and search just by email address:
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_KELLIE \
     gws gmail users messages list \
     --params '{"userId": "me", "q": "from:{email}", "maxResults": 10}'
   ```
   Repeat for Admin inbox. If still nothing, ask the operator to provide the resignation text.

6. Store the resignation content and which inbox received it for use in Steps 3 and 4.

#### Source: slack

Use the `resignation_content` input provided by the operator. Format as:
```
[Slack message from {Full Name} on {Resignation Date}]

{content}
```

Default sending inbox: `$GWS_USER_KELLIE`

#### Source: other

Use the `resignation_content` input. Format as:
```
[Resignation received via other means on {Resignation Date}]

{content}
```

Default sending inbox: `$GWS_USER_KELLIE`

#### Derive final working date

If `final_working_date` was not provided as an input, scan the resignation text for mentions of a final date, last day, or end date. If none found, calculate `resignation_date + 7 days`.


### Step 2 — Locate employee folder in Google Drive

Use the `gws` CLI for all Drive operations. Read `references/drive-ids.md` for IDs.

The People & Culture content lives on a separate shared drive (ID: `0AEGiBwrY8uSoUk9PVA`).

1. Search the **Employee Files** folder (ID: `1fep2a5Q0gpkfgMJnPRQ4N0WSH-twUXo0`) for a subfolder matching the employee's full name:
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
     gws drive files list \
     --params '{
       "q": "mimeType='\''application/vnd.google-apps.folder'\'' AND name='\''{Full Name}'\'' AND '\''1fep2a5Q0gpkfgMJnPRQ4N0WSH-twUXo0'\'' in parents AND trashed=false",
       "supportsAllDrives": true,
       "includeItemsFromAllDrives": true,
       "corpora": "drive",
       "driveId": "0AEGiBwrY8uSoUk9PVA"
     }'
   ```

2. If found, record the folder ID.

3. If not found, create one (the employee may predate the onboarding skill):
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
     gws drive files create \
     --json '{"name": "{Full Name}", "mimeType": "application/vnd.google-apps.folder", "parents": ["1fep2a5Q0gpkfgMJnPRQ4N0WSH-twUXo0"]}' \
     --params '{"supportsAllDrives": true, "fields": "id,name,webViewLink"}'
   ```


### Step 3 — Save resignation notice to employee folder

1. Write the resignation notice content to a local file:
   ```
   /tmp/offboarding-{name}/resignation-notice.txt
   ```

   Content format:
   ```
   RESIGNATION NOTICE RECORD
   =========================

   Employee:           {Full Name}
   Resignation Date:   {Resignation Date}
   Final Working Date: {Final Working Date}
   Source:             {email / Slack / other}
   Record Created:     {today's date}

   --- Original Resignation ---

   {full resignation text}

   --- Reference ---
   Gmail Thread ID: {thread_id} (if applicable)
   Gmail Message ID: {message_id} (if applicable)
   ```

2. Upload to Google Drive as a Google Doc (auto-converted on upload):
   ```bash
   env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
     GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
     gws drive files create \
     --upload /tmp/offboarding-{name}/resignation-notice.txt \
     --json '{"name": "Resignation Notice - {Full Name} - {Resignation Date}", "mimeType": "application/vnd.google-apps.document", "parents": ["{employee_folder_id}"]}' \
     --params '{"supportsAllDrives": true, "fields": "id,name,webViewLink"}'
   ```


### Step 4 — Send formal resignation acknowledgement email

**Critical:** Send from the **same inbox** that received the resignation email.

| Scenario                                   | Send from           | Sign-off name |
|--------------------------------------------|----------------------|---------------|
| Resignation found in Kellie's inbox        | `$GWS_USER_KELLIE`  | Kellie        |
| Resignation found in Admin's inbox         | `$GWS_USER_ADMIN`   | Dan           |
| Resignation source was `slack` or `other`  | `$GWS_USER_KELLIE`  | Kellie        |

Build the MIME message as a `.eml` file using Python's `email.mime.*` modules,
then send via the Gmail API using `--upload`:

```bash
env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_{KELLIE_OR_ADMIN} \
  gws gmail users messages send \
  --params '{"userId": "me"}' \
  --upload "/tmp/offboarding-{name}/acknowledgement.eml" \
  --upload-content-type "message/rfc822"
```

**Email template:**

```
To: {email}
Subject: Resignation Acknowledgement — Fig & Bloom

Hi {first_name},

Thank you for letting us know of your decision. We acknowledge receipt of your
resignation dated {resignation_date}.

We confirm your final working day with Fig & Bloom will be {final_working_date}.

We appreciate the contribution you've made during your time with us and wish you
all the best in your next chapter. If you have any questions about your final pay,
entitlements, or the handover process, please don't hesitate to reach out.

Warm regards,
{sender_name}
Fig & Bloom
```

Where `{sender_name}` is:
- **Kellie** — when sent from `kellie@figandbloom.com`
- **Dan** — when sent from `admin@figandbloom.com.au`

Clean up `/tmp/offboarding-{name}/` after sending.


### Step 5 — Remove from Trello boards

Check **all three** city boards — the employee may have been added to multiple.

| City      | Trello Board ID |
|-----------|-----------------|
| Melbourne | `4GWtuEoW`      |
| Sydney    | `trCaCddH`      |
| Brisbane  | `tXKKliCD`      |

1. For each board, get members:
   ```
   GET https://api.trello.com/1/boards/{board_id}/members?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}
   ```

2. Search returned members for the employee by name (case-insensitive, match on full name or display name).

3. If found, remove:
   ```
   DELETE https://api.trello.com/1/boards/{board_id}/members/{member_id}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}
   ```

4. If not found on any board, note in summary — this is not an error.


### Step 6 — Deactivate Slack access (manual)

> **Known limitation:** Slack's workspace invite/deactivation API (`admin.users.*`) is
> restricted to Enterprise Grid plans. Fig & Bloom does not use Enterprise Grid.

Flag as a manual step. Include in the summary:
- Employee's full name and email
- Instruction: "Deactivate this user's Slack account from Workspace Settings > Members"
- Note: **deactivate** (not delete) to preserve message history.


### Step 7 — Create Paperclip issue for deferred Deputy archival

The employee must remain active in Deputy while final pay is processed (14-day pay cycle). Create a Paperclip issue to archive them after sufficient time has passed.

- **Issue title:** `Archive {Full Name} in Deputy`
- **Issue body:**
  ```
  Employee:            {Full Name}
  Final Working Date:  {Final Working Date}
  Earliest Safe Date:  {Final Working Date + 30 days}

  Instructions:
  Use the Deputy API to archive this employee. Search by name, confirm identity
  by location ({city}), then call the terminate endpoint.

  Use `terminate` (not `delete`) to preserve historical timesheets and leave records.

  Refer to the `workforce-deputy-connector` skill for API details and authentication.
  ```
- The issue remains **open** until a human triggers the agent to process it after the safe date.


## Post-Process Summary

After all steps complete, produce a summary:

```
## Offboarding Summary: {Full Name}

**Departure:** {city} | Final day: {final_working_date} | Resignation date: {resignation_date}

| Step                                  | Status | Notes                              |
|---------------------------------------|--------|------------------------------------|
| Resignation notice — capture          | ✅/❌   | Source: {source}                   |
| Employee folder — locate/create       | ✅/❌   | [link]                             |
| Resignation notice — save to Drive    | ✅/❌   | [link]                             |
| Acknowledgement email — send          | ✅/❌   | Sent from {inbox} to {email}       |
| Trello — remove from boards           | ✅/❌   | Removed from {boards}              |
| Slack — deactivate                    | ⏳      | Manual — deactivate {name}         |
| Deputy — archive issue created        | ✅/❌   | Issue #{id}, safe after {date}     |

**Action required:**
- [ ] Deactivate {name}'s Slack account (Workspace Settings > Members)
- [ ] Confirm final pay and entitlements are processed
- [ ] Collect any company property (keys, equipment, etc.)
- [ ] Archive in Deputy after {archive_date} (see issue #{id})
```

Adapt the table to reflect actual outcomes — use ✅ for success, ❌ for failure
(with error detail), and ⏳ for manual steps.


## Configuration

This skill requires the following secrets/environment variables to be available
at runtime. If any are missing, note which integrations will be skipped and flag
for manual completion.

| Variable                                  | Description                                                  |
|-------------------------------------------|--------------------------------------------------------------|
| `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND`    | Must be set to `file` (global)                               |
| `GWS_USER_KELLIE`                         | Path to gws config dir for kellie@figandbloom.com            |
| `GWS_USER_ADMIN`                          | Path to gws config dir for admin@figandbloom.com.au          |
| `TRELLO_API_KEY`                          | Trello Power-Up API key                                      |
| `TRELLO_API_TOKEN`                        | Trello user token with board write access                    |

**Drive operations** use `$GWS_USER_ADMIN`. **Gmail operations** use whichever
profile matches the inbox that received the resignation (or `$GWS_USER_KELLIE`
by default for Slack/other sources).

**Note on `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`:** If this env var is set in
the agent environment, it takes precedence over `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`.
All `gws` commands in this skill use `env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`
to ensure the correct profile-based credentials are used.


## Error Handling

- **API call fails:** Log the HTTP status and error body. Do not retry more
  than twice. Mark the step as failed and continue.
- **Employee folder not found:** Create one — the employee may predate the
  onboarding skill.
- **Trello member not found:** Not an error — note in summary and continue.
- **Gmail search finds no resignation:** Ask the operator to provide the
  resignation text directly.
- **Missing input:** Stop and ask before proceeding.
- **Partial completion:** Always produce the summary table even if some steps
  failed. The human needs to know what's done and what isn't.


## Anti-Patterns

- **Don't send acknowledgement before saving resignation to Drive.** Step 3
  must complete before Step 4.
- **Don't send acknowledgement from a different inbox** than the one that
  received the resignation.
- **Don't assume the employee is only on one Trello board** — check all three.
- **Don't silently skip failed steps.** Every failure must appear in the
  summary table with a clear error description.
- **Don't pass large base64 payloads inline via `--json`.** Use `--upload`
  with a `.eml` file for Gmail sends.
- **Don't archive in Deputy immediately.** The employee must remain active
  for final pay processing. Create a Paperclip issue for deferred archival.
- **Don't use `delete` on Deputy** — use `terminate` to preserve historical
  timesheets and leave records.
