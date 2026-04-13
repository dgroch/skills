---
name: workforce-employee-onboarding
description: Onboard a new employee at Fig & Bloom — from intake through contract generation,
  platform invites, and welcome email.
version: 1.0.0
author: Dan Groch
license: MIT
metadata:
  hermes:
    tags: [Onboarding, HR, People & Culture, Workforce]
    related_skills: [reference-google-drive]
---

# Employee Onboarding

## When to use this skill

Use this skill whenever someone asks to onboard a new hire, add a new employee, set up a new team member, process a new starter, or any variation of "we have a new person joining." Also triggers for partial onboarding steps like "send the employment package to [name]" or "set up [name] in Deputy." If a Paperclip issue is assigned with onboarding context (name, email, employment type), treat it as a trigger.

This is a multi-step process with external API calls. Steps can fail independently.
Track progress, retry failures, and report a clear summary at the end.

## Inputs

Collect all of the following before starting. If any are missing, ask for them.

| Field           | Required | Format / Values                                            |
| --------------- | -------- | ---------------------------------------------------------- |
| Full name       | Yes      | First Last                                                 |
| Email           | Yes      | Personal email address                                     |
| Phone           | Yes      | Australian mobile preferred                                |
| Address         | Optional | Residential address (used in contract if known)            |
| Employment type | Yes      | `CAS` (casual), `PT` (part-time), `FT` (full-time)         |
| Job title       | Yes      | Position title (e.g. "Florist", "Senior Florist")          |
| Hours of work   | If PT    | Specific hours pattern (e.g. "20 hours per week, Mon–Wed") |
| City            | Yes      | `melbourne`, `sydney`, or `brisbane`                       |
| Pay rate        | Yes      | Hourly rate (AUD)                                          |
| Start date      | Yes      | YYYY-MM-DD                                                 |

### Auto-derived fields

The following contract fields are derived from `city` — do not ask for them:

| Contract placeholder | Melbourne                           | Sydney                                  | Brisbane                          |
| -------------------- | ----------------------------------- | --------------------------------------- | --------------------------------- |
| `{studio location}`  | 274 Wingrove St, Fairfield VIC 3078 | 62-64 Australia St, Camperdown NSW 2050 | 31 Jeays St, Bowen Hills QLD 4006 |
| `{governing law}`    | Victoria                            | New South Wales                         | Queensland                        |

## Process

Execute steps in this order. Each step should be attempted regardless of whether
a previous step failed — do not stop the entire process because one integration
is down. Track pass/fail per step.

### Step 1 — Retrieve hiring thread and CV from Gmail

Use the Gmail MCP to search for the candidate's correspondence.

1. Search Gmail for messages involving the employee's email address:
   - Query: `from:{email} OR to:{email}`
   - Sort by most recent first.
2. Identify the hiring/interview thread. Look for subject lines containing
   keywords like "application", "interview", "offer", "role", "position",
   the candidate's name, or job-related context. If multiple threads exist,
   prefer the most recent thread with the most messages.
3. Read the full thread content.
4. Scan all messages in the thread for attachments. Look for CV/resume files
   (typically `.pdf`, `.docx`, or `.doc` with filenames containing "cv",
   "resume", or the candidate's name). Download any found.
5. If no CV attachment is found in the thread, broaden the search:
   - Query: `from:{email} filename:pdf OR filename:docx`
   - Check the first few results for anything that looks like a CV.
6. If still no CV is found, note this in the summary — don't block the process.

Store the thread content and any downloaded attachments for use in Step 2.

### Step 2 — Create employee folder in Google Drive

Read `references/drive-ids.md` for all folder and file IDs used in this skill.

The People & Culture content lives on a separate shared drive (ID: `0AEGiBwrY8uSoUk9PVA`),
not the Paperclip shared drive.

Any `gws drive` operation against this shared drive must include
`"supportsAllDrives": true` in `--params`. This applies to `files copy`,
`files create`, `files update`, `files delete`, and `files get`. Without this
flag, Drive operations can return `404` even when the file or folder exists.

1. Inside the **Employee Files** folder (ID: `1fep2a5Q0gpkfgMJnPRQ4N0WSH-twUXo0`),
   create a subfolder named with the employee's full name (e.g. `Sarah Chen`).
2. If a CV was retrieved from Gmail (Step 1), upload it to this folder.
3. Save the hiring email thread to this folder as a Google Doc named
   `Hiring Correspondence - [Full Name]`. Include sender, date, subject,
   and body for each message in the thread.
4. If no thread was found in Step 1, skip item 3 and note it in the summary.

Record the new folder's ID — you'll need it in later steps.

### Step 3 — Generate employment contract

Select the correct template by employment type (see `references/drive-ids.md`
for full details):

| Type | Template File ID                              |
| ---- | --------------------------------------------- |
| CAS  | `1ElSlt6L5-vAM2n9ShyVCjstr_HshCxMT43n-Bgc3iDk` |
| PT   | `18bf8BJ1E8r7BfXSVu4cgP26GaDeY9w6Jvwh4KTrWXAc` |
| FT   | `1viGOPU2BfXBQ7QXKf0MfRSD5iZmofpeaqZv6wNmBtX4` |

Use `gws drive` and `gws docs` for this step. Do not use MCP file-creation tools
to copy the contract template. Uploading or recreating the document can destroy
Google Docs-native formatting such as paragraph numbering, fonts, and layout.

1. Copy the correct Google Docs template into the employee's folder using
   `gws drive files copy` with `supportsAllDrives: true`.
   Example:

   ```bash
   gws drive files copy \
     --params '{"fileId": "{TEMPLATE_ID}", "supportsAllDrives": true}' \
     --json '{"name": "Employment Contract - {Full Name}", "parents": ["{EMPLOYEE_FOLDER_ID}"]}'
   ```

   Save the returned document ID as `$CONTRACT_DOC_ID`.

2. Fill placeholders using the Google Docs API via `gws docs documents batchUpdate`.
   Use one `replaceAllText` request per placeholder so formatting is preserved.
   Example:

   ```bash
   gws docs documents batchUpdate \
     --params '{"documentId": "$CONTRACT_DOC_ID"}' \
     --json '{"requests": [
       {"replaceAllText": {"containsText": {"text": "{employee name}", "matchCase": true}, "replaceText": "Jemma Pike"}}
     ]}'
   ```

3. All three templates use `{curly brace}` placeholders. Replace every instance
   of each placeholder listed below.

**Placeholder map — all contract types:**

| Placeholder                   | Source                                                      |
| ----------------------------- | ----------------------------------------------------------- |
| `{employee name}`             | Full name (appears in header AND Schedule)                  |
| `{employee email}`            | Email (Schedule Item 2)                                     |
| `{employee phone}`            | Phone (Schedule Item 2)                                     |
| `{employee address if known}` | Address if provided, otherwise remove line                  |
| `{job title}`                 | Job title (Schedule Item 3)                                 |
| `{commencement date}`         | Start date (header AND Schedule Item 4)                     |
| `{studio location}`           | Auto-derived from city (see Inputs table)                   |
| `{pay rate}`                  | Pay rate in AUD (Schedule — "per hour plus superannuation") |
| `{governing law}`             | Auto-derived from city (see Inputs table)                   |

**PT only — additional placeholder:**

| Placeholder       | Source                                  |
| ----------------- | --------------------------------------- |
| `{hours of work}` | Hours of work pattern (Schedule Item 8) |

4. If address was not provided, remove the full `{employee address if known}`
   line from Schedule Item 2 entirely rather than leaving a blank.

5. After placeholder replacement, clear the template's pink highlight styling so
   the final contract does not retain human-only markup:

   1. Get the document end index:

      ```bash
      gws docs documents get --params '{"documentId": "$CONTRACT_DOC_ID"}' 2>/dev/null
      ```

   2. Clear background colour across the document:

      ```bash
      gws docs documents batchUpdate \
        --params '{"documentId": "$CONTRACT_DOC_ID"}' \
        --json '{"requests": [{"updateTextStyle": {
          "range": {"startIndex": 1, "endIndex": END_INDEX},
          "textStyle": {"backgroundColor": {}},
          "fields": "backgroundColor"
        }}]}'
      ```

6. Verify that no `{` or `}` placeholder tokens remain in the document. If any
   are found that aren't in the map above, flag them in the summary with the
   surrounding context so the human can resolve them.

### Step 4 — Send platform invitations

#### 4a — Deputy (API)

Use Deputy as a two-step setup:

1. Create the employee profile and core employment details.
2. Apply the correct Deputy award-library pay rate for the employee's employment type.

`DEPUTY_SUBDOMAIN` already contains the full hostname
(for example `18b41717033219.au.deputy.com`). The correct base URL is:
`https://$DEPUTY_SUBDOMAIN/api/v1`

**Step 4a.1 — Create the employee**

```
POST https://$DEPUTY_SUBDOMAIN/api/v1/supervise/employee
Authorization: OAuth $DEPUTY_TOKEN
Content-Type: application/json

{
  "strFirstName": "{first_name}",
  "strLastName": "{last_name}",
  "strEmail": "{email}",
  "strMobile": "{phone}",
  "intCompanyId": 1,
  "fltPayRate": {pay_rate},
  "strStartDate": "{start_date}",
  "strEmploymentBasis": "{employment_type}"
}
```

Use Deputy employment basis values:

| Skill input | Deputy value |
| ----------- | ------------ |
| `CAS`       | `CAS`        |
| `PT`        | `PT`         |
| `FT`        | `FT`         |

Capture the created employee ID from the response for the award configuration step.

**Location mapping:**

| City      | Deputy Location ID |
| --------- | ------------------ |
| Melbourne | `1`                |
| Sydney    | `8`                |
| Brisbane  | `10`               |

This step is responsible for:

- Personal information such as first name, last name, email, and mobile
- Employment basis (`CAS`, `PT`, `FT`)
- Start date
- Base pay value used during creation

**Step 4a.2 — Apply the Deputy award library**

Fig & Bloom uses the Deputy award library for GRIA. After the employee is created,
apply the correct library award based on employment type:

| Skill input | Deputy award library name |
| ----------- | ------------------------- |
| `PT`        | `TP [MA000004] GRIA - Part Time - 1-July-2025` |
| `CAS`       | `TP [MA000004] GRIA - Casual- 1-July-2025` |
| `FT`        | `TP [MA000004] GRIA - Full Time - 1-July-2025` |

Use the Deputy pay-rate-library flow:

1. Query the employment contract / award library to find the matching library record ID.
2. Apply that library award to the employee.
3. If the award configuration supports overriding the ordinary base hourly rate,
   set it to the employee's agreed pay rate.
4. If a classification / level is required for the selected award, do not guess.
   Flag it for human confirmation unless it was explicitly provided in the onboarding brief.

Also set or update the employee's Payroll ID if the workflow has a confirmed value
to use. If no Payroll ID is available, leave it blank and note it in the summary.

Do not assume the create-employee API call fully configures pay details shown in the
Deputy UI. The award-library assignment is a separate step and must be handled explicitly.

If API credentials are not configured or the call fails, log the failure and
note that Deputy setup must be completed manually.

#### 4b — Trello (API)

Invite the employee to the city-specific Trello board.

```
PUT https://api.trello.com/1/boards/{board_id}/members
  ?email={email}
  &key=$TRELLO_API_KEY
  &token=$TRELLO_TOKEN
Content-Type: application/json

{
  "fullName": "{full_name}"
}
```

**Board mapping:**

| City      | Trello Board ID |
| --------- | --------------- |
| Melbourne | `4GWtuEoW`      |
| Sydney    | `trCaCddH`      |
| Brisbane  | `tXKKliCD`      |

If API credentials are not configured or the call fails, log the failure and
note that the Trello invite must be sent manually.

#### 4c — Slack

> **Known limitation:** Slack's workspace invite API (`admin.users.invite`) is
> restricted to Enterprise Grid plans. Fig & Bloom does not use Enterprise Grid.
> Legacy token endpoints were deprecated in March 2025.

**Current approach:** Flag Slack as a manual step. Include the employee's name
and email in the summary so the human can send the invite from Slack directly.

**Future options** (for Dan to evaluate):

- If Fig & Bloom upgrades to Enterprise Grid, use `admin.users.invite`.
- Build a browser automation skill using Claude in Chrome to navigate to
  Slack's invite UI and submit the form.
- Use a third-party integration (Zapier/Make) triggered by a webhook.

### Step 5 — Send employment package via email

Compose and send an email to the new employee with the following attachments.
Use Gmail (via MCP or API) to send from the appropriate Fig & Bloom address.

Before attempting to draft or send, perform a lightweight Gmail authorisation
check such as `gmail_get_profile`.

- If the check succeeds, continue with Step 5 as normal.
- If the check fails with an auth or permissions error, skip sending. Include
  the complete ready-to-send subject, body, recipient, and attachment list in
  the final summary so a human can copy-paste and send it manually.

**Subject:** `Welcome to Fig & Bloom — Your Employment Package`

**Body template:**

```
Hi {first_name},

Welcome to Fig & Bloom! We're thrilled to have you joining the team.

Please find your employment package attached. This includes:

- Your employment contract — please review, sign, and return
- Payroll information form — please complete and return
- Fair Work Information Statement
- Employee handbook
- Health & safety handbook

If you have any questions, don't hesitate to reach out.

We look forward to working with you.

Warm regards,
Fig & Bloom
```

**Attachments — source file IDs (People & Culture shared drive):**

| Document                        | File ID                                        |
| ------------------------------- | ---------------------------------------------- |
| Employment contract             | The copy created in Step 3 (employee's folder) |
| Payroll Information Form        | `1TchMO5lP1Yv0HnYjKQRN6gq3Ba1KkGh4`            |
| Fair Work Information Statement | `11txwv4dHDHslHkRzh0DoO0ny-OGpsLwR`            |
| Employee Handbook               | `17UpA0Msl7G_0YRkYBldil4gKDs4kZmPl`            |
| Health & Safety Handbook        | `17VF3zyohOAN80d9aSMG0KvX_Oo2GhVl_`            |

See `references/drive-ids.md` for the full file inventory.

To attach Drive files to the email:

1. Download each PDF from Google Drive using the file IDs above.
2. Export the employment contract from Google Docs as PDF.
3. Attach all to the outgoing Gmail message.

If any attachment cannot be found or downloaded, send the email with whatever
attachments are available and note the missing items in the summary.

### Step 6 — Save documents to Google Drive

Ensure the employee's folder (from Step 2) contains:

- CV (if found in Step 1)
- Hiring correspondence (saved in Step 2)
- Employment contract (already there from Step 3)
- A record of the welcome email sent (save as PDF or note the Gmail message ID)

This step is mostly a verification pass — confirm the folder has what it should.

## Post-Process Summary

After all steps complete, produce a summary like this:

```
## Onboarding Summary: {Full Name}

**Employment:** {type} | {city} | ${rate}/hr | Starting {date}

| Step                        | Status | Notes                          |
|-----------------------------|--------|--------------------------------|
| Gmail — thread & CV         | ✅      | Thread found, CV attached      |
| Google Drive folder         | ✅      | [link]                        |
| Employment contract         | ✅      | [link]                        |
| Deputy profile              | ✅      | Employee ID: {id}             |
| Trello board invite         | ✅      | {city} board                  |
| Slack invite                | ⏳      | Manual — send to {email}      |
| Employment package email    | ✅      | Sent {timestamp}              |
| Drive folder verification   | ✅      |                               |

**Action required:**
- [ ] Send Slack workspace invite to {email}
- [ ] Confirm contract is signed and returned
```

Adapt the table to reflect actual outcomes — use ✅ for success, ❌ for failure
(with error detail), and ⏳ for manual steps.

## Configuration

This skill requires the following secrets/environment variables to be available
to the agent at runtime. If any are missing, the agent should note which
integrations will be skipped and flag for manual completion.

| Variable           | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `DEPUTY_TOKEN`     | OAuth token for Deputy V1 API                                            |
| `DEPUTY_SUBDOMAIN` | Full Deputy hostname used in URL: `https://$DEPUTY_SUBDOMAIN/api/v1`     |
| `TRELLO_API_KEY`   | Trello Power-Up API key                                                  |
| `TRELLO_TOKEN`     | Trello user token with board write access                                |

Google Drive and Gmail access is provided via MCP connectors (Google Drive MCP,
Gmail MCP) — these do not require separate API keys.

## Error Handling

- **API call fails:** Log the HTTP status and error body. Do not retry more
  than twice. Mark the step as failed and continue.
- **Template not found:** Search Drive for partial matches. If still not found,
  list available files in the Employment Contracts folder so the human can
  identify the right one.
- **Missing input:** If a required input is missing, stop and ask before
  proceeding.
- **No Gmail results:** If no hiring thread or CV is found in Gmail, note it
  in the summary and continue. These are nice-to-have, not blockers.
- **Partial completion:** Always produce the summary table even if some steps
  failed. The human needs to know what's done and what isn't.

## Anti-Patterns

- **Don't send the email before the contract is generated.** The contract is
  an attachment — wait for Step 3 to complete before Step 5.
- **Don't assume folder IDs.** Always search for folders by name within the
  shared drive. Folder IDs can change if someone moves things around.
- **Don't silently skip failed steps.** Every failure must appear in the
  summary table with a clear error description.
- **Don't hardcode Deputy location IDs without verification.** The IDs in
  this skill (1, 8, 10) are confirmed as of April 2026. If a call returns
  a location error, query the Deputy API for the current location list
  before assuming the IDs are wrong.
