---
name: klaviyo-api
description: Provides authentication patterns, endpoint documentation, request/response formats, error handling, rate limiting, and known gotchas for all Klaviyo API domains. version: 1.0.0
source_api_revision: "2026-01-15"
openapi_spec_repo: "https://github.com/klaviyo/openapi"
author: Dan Groch
license: MIT
metadata:
  tags: [API, Klaviyo, Email, Marketing, Integration, Reference]
---

# Klaviyo API

## Overview

A reference skill for making API calls to Klaviyo's marketing platform.
Covers authentication, all major endpoint domains, error handling, rate
limiting, pagination, and known issues. Designed to be consumed by other
skills that build on Klaviyo (email campaigns, flows, analytics, etc.).

This skill targets **Klaviyo API revision `2026-01-15`**. See "Version
Management" at the end of this document for how to detect and handle
API version drift.

Use this skill whenever an agent needs to make any Klaviyo API call — creating templates, campaigns, flows, pulling metrics, managing profiles, lists, segments, or any other Klaviyo operation. Also use when debugging Klaviyo API errors, choosing between MCP and direct API access, or checking whether a Klaviyo capability is API-accessible. This is a reference skill — it teaches the agent how to talk to Klaviyo, not what to build. Consuming skills (like email-template-builder) define the "what".

## Access Methods

Klaviyo offers two ways for agents to interact with the platform.
Choose based on what's available in the agent's environment.

### Option 1: Klaviyo MCP Server (preferred when available)

Klaviyo provides an official MCP (Model Context Protocol) server that
wraps the full API. If the agent's runtime supports MCP connections,
this is the simplest path — it handles auth, pagination, and request
formatting automatically.

**Remote server (recommended):**
```json
{
  "mcpServers": {
    "klaviyo": {
      "url": "https://mcp.klaviyo.com/sse",
      "env": {
        "KLAVIYO_API_KEY": "<private-api-key>"
      }
    }
  }
}
```

**Available via Claude.ai connector:**
Settings → Connectors → Browse Connectors → Klaviyo → Connect.
Authenticates via OAuth. Available on Pro, Max, Team, Enterprise plans.

**When to use MCP:** The agent is running in an environment with MCP
support (Claude Desktop, Cursor, VS Code, Claude.ai connectors, or
any MCP-compatible runtime). MCP is preferred because it reduces the
surface area for auth/format errors.

**When NOT to use MCP:** The agent is running in a headless environment
without MCP support, or needs fine-grained control over request
construction (e.g., building hybrid templates, custom metric aggregate
queries). Fall back to direct API calls.

**MCP query parameters for control:**
- `?read_only=true` — restrict to read-only operations
- `?enable_ugc=true` — enable user-generated content tools
- `?multi_account=true` — enable multi-account support

### Option 2: Direct API (HTTP)

All endpoints live under `https://a.klaviyo.com/api/`.

**Authentication:**
```
Authorization: Klaviyo-API-Key <private-api-key>
```

**Required headers on every request:**
```
Content-Type: application/json
Accept: application/json
revision: 2026-01-15
```

The `revision` header is mandatory. Omitting it defaults to the oldest
supported revision, which may lack features or return different response
shapes. Always pin to the revision this skill targets.

**API key scopes:** Klaviyo supports granular scopes on private keys.
Each reference file documents the scopes required for its endpoints.
Common scopes: `templates:read`, `templates:write`, `campaigns:read`,
`campaigns:write`, `flows:read`, `flows:write`, `metrics:read`,
`profiles:read`, `profiles:write`, `lists:read`, `lists:write`,
`segments:read`, `segments:write`, `events:read`, `events:write`.

If a request returns `403 Forbidden`, the API key likely lacks the
required scope. The error response body will indicate which scope
is needed.

## Request Format: JSON:API

Klaviyo uses the [JSON:API](https://jsonapi.org/) specification.
All request and response bodies follow this structure:

```json
{
  "data": {
    "type": "resource-type",
    "id": "resource-id",
    "attributes": { ... },
    "relationships": { ... }
  }
}
```

Key JSON:API patterns used throughout:

**Creating a resource:**
```json
POST /api/{resource}/
{
  "data": {
    "type": "{resource-type}",
    "attributes": { ... }
  }
}
```

**Updating a resource:**
```json
PATCH /api/{resource}/{id}/
{
  "data": {
    "type": "{resource-type}",
    "id": "{id}",
    "attributes": { ... }
  }
}
```

**Including related resources:**
```
GET /api/campaigns/{id}/?include=campaign-messages
```

**Sparse fieldsets (request only specific fields):**
```
GET /api/profiles/?fields[profile]=email,first_name,last_name
```

**Filtering:**
```
GET /api/campaigns/?filter=equals(messages.channel,'email')
```

Filter operators: `equals`, `contains`, `greater-than`,
`greater-or-equal`, `less-than`, `less-or-equal`, `any`.
Operator support varies by endpoint — check the reference file.

## Pagination

Klaviyo uses cursor-based pagination. Responses include a `links`
object with `self`, `next`, and `prev` URLs.

```json
{
  "data": [ ... ],
  "links": {
    "self": "https://a.klaviyo.com/api/profiles/?page[cursor]=abc123",
    "next": "https://a.klaviyo.com/api/profiles/?page[cursor]=def456",
    "prev": null
  }
}
```

To paginate: follow the `links.next` URL until it returns `null`.

**Page size:** Use `page[size]=N` (default varies, max usually 100).

**Do not** construct cursor values manually. Always use the URLs
returned in `links`.

## Rate Limiting

Klaviyo uses tiered rate limits that vary by endpoint:

| Tier   | Burst        | Steady       | Typical endpoints              |
|--------|-------------|-------------|--------------------------------|
| XXXL   | 700/s       | 3500/m      | Client-side tracking           |
| XL     | 100/s       | 700/m       | Get Profiles, Get Events       |
| L      | 75/s        | 700/m       | Create/Update Profiles         |
| M      | 10/s        | 150/m       | Get Campaigns, Get Flows       |
| S      | 3/s         | 60/m        | Create Campaign, Create Flow   |
| SMALL  | 3/s         | 60/m        | Reporting, Metric Aggregates   |

**Rate limit response:** HTTP `429 Too Many Requests`

**Headers on every response:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1620000000
Retry-After: 1
```

**Recovery strategy:**
1. On 429: read `Retry-After` header (seconds).
2. If no `Retry-After`: exponential backoff — 1s, 2s, 4s, 8s, max 30s.
3. Maximum 5 retries per request.
4. If still failing after 5 retries: log the error and report to the
   operator. Do not silently retry indefinitely.

## Error Handling

**Standard error response:**
```json
{
  "errors": [
    {
      "id": "unique-error-id",
      "status": 400,
      "code": "invalid",
      "title": "Invalid input.",
      "detail": "The 'name' attribute is required.",
      "source": {
        "pointer": "/data/attributes/name"
      }
    }
  ]
}
```

**Common status codes and actions:**

| Code | Meaning            | Action                                        |
|------|-------------------|-----------------------------------------------|
| 400  | Bad request       | Fix the request body. Check `source.pointer`.  |
| 401  | Unauthorized      | API key is missing or invalid.                 |
| 403  | Forbidden         | API key lacks required scope. Add scope.       |
| 404  | Not found         | Resource doesn't exist. Check the ID.          |
| 409  | Conflict          | Resource already exists or state conflict.     |
| 429  | Rate limited      | Back off per strategy above.                   |
| 500  | Server error      | Retry with backoff. If persistent, escalate.   |
| 503  | Service unavail.  | Retry with backoff. Klaviyo may be deploying.  |

**Known 404 bug (template clone):** When you assign a template to a
campaign message, Klaviyo clones the template and returns a new
`template_id`. Attempting to `PATCH` this cloned template immediately
may return 404. Workaround: wait 2-3 seconds after assignment before
updating the cloned template. If still 404, update the original
template instead and re-assign.

## Endpoint Reference Files

Each API domain is documented in a separate reference file. Read the
relevant file before making calls to that domain.

| Domain              | File                              | Key scopes needed         |
|--------------------|----------------------------------|--------------------------|
| Templates          | `references/templates.md`         | templates:read/write     |
| Campaigns          | `references/campaigns.md`         | campaigns:read/write     |
| Flows              | `references/flows.md`             | flows:read/write         |
| Reporting          | `references/reporting.md`         | campaigns:read, flows:read, metrics:read |
| Profiles           | `references/profiles.md`          | profiles:read/write      |
| Lists & Segments   | `references/lists-segments.md`    | lists:read/write, segments:read/write |
| Events & Metrics   | `references/events-metrics.md`    | events:read/write, metrics:read |
| Catalogs           | `references/catalogs.md`          | catalogs:read/write      |
| Tags               | `references/tags.md`              | tags:read/write          |
| Images             | `references/images.md`            | images:read/write        |

Read only the reference file(s) relevant to the current task.

## SDKs

Klaviyo maintains official SDKs that handle auth, pagination, rate
limiting, and retry logic. If the agent's environment supports
installing packages, prefer an SDK over raw HTTP.

| Language | Package              | Install                             |
|----------|---------------------|-------------------------------------|
| Python   | `klaviyo-api`        | `pip install klaviyo-api`           |
| Node.js  | `klaviyo-api`        | `npm install klaviyo-api`           |
| Ruby     | `klaviyo-api-sdk`    | `gem install klaviyo-api-sdk`       |
| PHP      | `klaviyo/api`        | `composer require klaviyo/api`      |

**Python SDK example:**
```python
from klaviyo_api import KlaviyoAPI
klaviyo = KlaviyoAPI("YOUR_API_KEY", max_delay=60, max_retries=3)

# Get all templates
templates = klaviyo.Templates.get_templates()

# Create a template
klaviyo.Templates.create_template({
    "data": {
        "type": "template",
        "attributes": {
            "name": "My Template",
            "editor_type": "CODE",
            "html": "<html>...</html>"
        }
    }
})
```

## Klaviyo Template Language

Klaviyo templates use Django-style template tags for dynamic content:

| Tag                                      | Purpose                        |
|-----------------------------------------|-------------------------------|
| `{{ first_name }}`                       | Profile property              |
| `{{ first_name\|default:'Friend' }}`     | Property with fallback        |
| `{% if ... %}...{% endif %}`             | Conditional block             |
| `{% for item in items %}...{% endfor %}` | Loop (product feeds, etc.)    |
| `{% unsubscribe %}`                      | Unsubscribe link (required)   |
| `{{ organization.url }}`                 | Company URL                   |
| `{% manage_preferences %}`               | Preference centre link        |
| `{{ email }}`                            | Recipient email               |

For product feeds:
```
{% for item in catalog %}
  {{ item.title }}
  {{ item.image_url }}
  {{ item.price }}
  {{ item.url }}
{% endfor %}
```

## Version Management

This skill targets Klaviyo API revision `2026-01-15`. Klaviyo releases
new revisions roughly quarterly. Breaking changes only occur between
revisions; within a revision, the API is stable.

### How to check for version drift

Klaviyo publishes their OpenAPI spec at:
`https://github.com/klaviyo/openapi`

The `openapi/stable.json` file contains the current stable spec. The
revision this skill targets is recorded in the YAML frontmatter above
(`source_api_revision`).

**To check if the skill is current:**

1. Fetch the latest spec: `GET https://github.com/klaviyo/openapi`
2. Compare the revision in the spec against `source_api_revision`
   in this file's frontmatter.
3. If they differ, check Klaviyo's changelog at
   `https://developers.klaviyo.com/en/docs/changelog_` for breaking
   changes relevant to the endpoints being used.

**If a newer revision exists:**
- Do NOT automatically switch revisions. The skill's reference files
  and examples are validated against the pinned revision.
- Report to the operator: "Klaviyo API revision [new] is available.
  This skill targets [current]. Review the changelog for breaking
  changes before updating."
- Continue using the pinned revision — Klaviyo supports multiple
  active revisions simultaneously.

### Versioning policy

Klaviyo's versioning policy:
- New revisions are released ~quarterly.
- Previous revisions remain supported for 2 years after release.
- After 2 years, a revision is deprecated with 1 year notice.
- Breaking changes (removed fields, renamed endpoints, changed
  response shapes) only occur in new revisions.
- Non-breaking changes (new optional fields, new endpoints) may be
  added to existing revisions.

### Available revisions (as of skill creation)

`v2026-01-15` (current) · `v2025-10-15` · `v2025-07-15` ·
`v2025-04-15` · `v2025-01-15` · `v2024-10-15` · `v2024-07-15` ·
`v2024-06-15` · `v2024-05-15` · `v2024-02-15` · older (deprecated)

## Anti-Patterns

- **Omitting the `revision` header.** This silently uses the oldest
  supported revision and may return unexpected response shapes.
  Always include `revision: 2026-01-15`.

- **Constructing pagination cursors manually.** Always use the URLs
  from `links.next`. Cursor format is opaque and can change.

- **Retrying indefinitely on 429.** Cap at 5 retries with backoff.
  Infinite retry loops risk degrading the Klaviyo account's rate
  limit allowance.

- **Ignoring the `source.pointer` in error responses.** This tells
  you exactly which field caused the error. Use it.

- **Using the wrong editor_type for templates.** `CODE` templates
  accept raw HTML. `DRAG_AND_DROP` (hybrid) templates have a
  specific JSON structure. If you're building from a component
  library, use `CODE`.

- **Updating cloned templates immediately after assignment.** The
  clone 404 bug requires a brief wait. See "Known 404 bug" above.

- **Mixing up Reporting API and Metric Aggregates.** The Reporting
  API (`campaign-values-reports`, `flow-values-reports`) matches
  Klaviyo's UI and uses send-time. Metric Aggregates uses event-time.
  See `references/reporting.md` for when to use which.

- **Hardcoding the API revision.** Put it in a config variable so
  it can be updated in one place when the skill is upgraded.
