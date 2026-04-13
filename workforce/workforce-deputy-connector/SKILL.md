---
name: workforce-deputy-connector
description: Paperclip operations workflow for Deputy Connector. Use this skill when you need to access Deputy API data for employees, rosters, timesheets, leave, and related HR operations.
---

# Deputy API Connector

This skill provides a comprehensive, reusable connector for interacting with the Deputy API. It includes helper scripts for authentication and common API operations, as well as the full OpenAPI specifications and a Postman collection for detailed reference.

## Authentication

All Deputy API calls require authentication using a **permanent API token** and the user's **Deputy subdomain**.

- **Subdomain**: The unique URL for the user's Deputy instance (e.g., `yourcompany.au.deputy.com`).
- **API Token**: A permanent token generated from the Deputy web interface.

When a task requires interacting with Deputy, first ask the user for their subdomain and API token if they have not been provided.

## Core Concepts

### Base URL

The base URL for all API requests is constructed using the user's subdomain:

`https://{subdomain}/api/v1`

### Pagination

The Deputy API uses a `start` parameter for paginating through large result sets. The `deputy_api_client.py` script handles this automatically when using the `--all-pages` flag.

## Helper Script: `deputy_api_client.py`

A Python script is provided at `/data/.openclaw/workspace/skills/deputy-connector/scripts/deputy_api_client.py` to simplify API interactions. Always use this script to ensure consistent and reliable communication with the Deputy API.

**Usage:**

```bash
python /data/.openclaw/workspace/skills/deputy-connector/scripts/deputy_api_client.py <subdomain> <token> <endpoint> [--method METHOD] [--params JSON] [--data JSON] [--all-pages]
```

**Examples:**

**1. Get all employees (handles pagination):**

```bash
python /data/.openclaw/workspace/skills/deputy-connector/scripts/deputy_api_client.py yourcompany.au.deputy.com YOUR_TOKEN resource/Employee --all-pages
```

**2. Get a specific roster:**

```bash
python /data/.openclaw/workspace/skills/deputy-connector/scripts/deputy_api_client.py yourcompany.au.deputy.com YOUR_TOKEN supervise/roster/123
```

**3. Add a new employee:**

```bash
python /data/.openclaw/workspace/skills/deputy-connector/scripts/deputy_api_client.py yourcompany.au.deputy.com YOUR_TOKEN supervise/employee --method POST --data '{"strFirstName": "John", "strLastName": "Doe", "intCompanyId": 1}'
```

## Key API Domains

This skill covers the full Deputy API. The following table summarizes the key domains and provides pointers to the relevant API specification file.

| Domain           | Description                                                                   | API Specification          |
| ---------------- | ----------------------------------------------------------------------------- | -------------------------- |
| **Employees**    | Manage employee records, including adding, updating, and terminating.         | `deputy.json`              |
| **Rosters**      | Create, publish, and manage staff rosters.                                    | `deputy.json`              |
| **Timesheets**   | Start, stop, and retrieve timesheets for payroll processing.                  | `deputy.json`              |
| **Locations**    | Manage business locations and departments.                                    | `deputy.json`              |
| **Resource API** | A generic, resource-oriented interface for interacting with all data objects. | `deputy-resource-api.json` |

For a complete and detailed understanding of all available endpoints, parameters, and schemas, always refer to the API reference files.

## API Reference

The full API specifications are available in the `references/` directory:

- `/data/.openclaw/workspace/skills/deputy-connector/references/deputy.json`: The main OpenAPI 3.0 specification.
- `/data/.openclaw/workspace/skills/deputy-connector/references/deputy-resource-api.json`: The OpenAPI 3.0 specification for the Resource API.
- `/data/.openclaw/workspace/skills/deputy-connector/references/Deputy.postman_collection.json`: A Postman collection with example requests.

Before performing any complex operation, consult these files to understand the required request structure and expected response format.
