# Recursive Drive Scanning and De-duplication

## Why Root-Level Scans Are Misleading

Synology Photos shared drives contain **40,000+ media files across 5,000+ folders** when recursively scanned. A root-level scan only shows ~1,000 files and gives a false sense of scope.

**Always use recursive BFS scanning** to get the true count before planning manifest jobs.

## Recursive Scan Pattern (BFS Folder Queue)

```python
import json
import subprocess
import time

def scan_drive_recursive(drive_id, gws_path="/opt/data/npm-global/bin/gws"):
    """BFS scan of entire drive, returns list of media files."""

    folders_to_scan = ['root']
    all_media = []
    scanned_count = 0

    # Media file extensions
    media_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.heic', '.heif', '.tiff'}

    while folders_to_scan:
        folder = folders_to_scan.pop(0)
        scanned_count += 1

        # Progress logging every 10 folders
        if scanned_count % 10 == 0:
            print(f"Scanned {scanned_count} folders, found {len(all_media)} media files so far...")

        # Build query
        if folder == 'root':
            q = 'trashed=false'
        else:
            q = f"trashed=false and '{folder}' in parents"

        # Paginate through results
        page_token = None
        while True:
            params = {
                'q': q,
                'corpora': 'drive',
                'driveId': drive_id,
                'supportsAllDrives': True,
                'includeItemsFromAllDrives': True,
                'pageSize': 1000
            }
            if page_token:
                params['pageToken'] = page_token

            # Run gws command
            result = subprocess.run(
                [gws_path, 'drive', 'files', 'list', '--params', json.dumps(params), '--format', 'json'],
                capture_output=True,
                text=True,
                cwd='/tmp',
                env={
                    **os.environ,
                    'GOOGLE_WORKSPACE_CLI_CONFIG_DIR': '/tmp/gws_config',
                    'KEYRING_BACKEND': 'file'
                }
            )

            if result.returncode != 0:
                print(f"GWS error: {result.stderr}")
                break

            try:
                data = json.loads(result.stdout)
            except:
                break

            files = data.get('files', [])

            for f in files:
                name = f.get('name', '').lower()
                mime = f.get('mimeType', '')

                # Check if folder
                if mime == 'application/vnd.google-apps.folder':
                    folders_to_scan.append(f['id'])

                # Check if media
                elif any(name.endswith(ext) for ext in media_exts):
                    all_media.append(f)

            page_token = data.get('nextPageToken')
            if not page_token:
                break

    print(f"Scan complete: {scanned_count} folders, {len(all_media)} total media files")
    return all_media
```

**Expected runtime:** 45-60 minutes for a drive with 5,000+ folders and 40,000+ files.

## De-duplication Against Notion

**Always check what's already manifested before processing.** This can reduce the batch size dramatically (e.g., 44k files → 37k after dedup against 7k existing entries).

### Query All Notion Entries

```python
import urllib.request
import json
import time

def get_manifested_files(notion_db_id, notion_api_key):
    """Query Notion DB for all manifested files, returns set of filenames."""

    manifested = set()
    start_cursor = None

    while True:
        payload = {
            "filter": {
                "property": "Asset",
                "title": {"is_not_empty": True}
            }
        }
        if start_cursor:
            payload["start_cursor"] = start_cursor

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{notion_db_id}/query",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {notion_api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read())
        except Exception as e:
            print(f"Notion query error: {e}")
            break

        # Extract filenames from Asset title field
        for page in result.get("results", []):
            props = page.get("properties", {})
            asset_prop = props.get("Asset", {})
            title_list = asset_prop.get("title", [])
            if title_list:
                filename = title_list[0].get("plain_text", "")
                if filename:
                    manifested.add(filename)

        # Check for more pages
        if not result.get("has_more"):
            break

        start_cursor = result.get("next_cursor")
        time.sleep(0.3)  # Notion rate limit

    print(f"Found {len(manifested)} already-manifested files in Notion")
    return manifested
```

### Filter Drive Files

```python
# Get all media files from drive (recursive scan)
all_media = scan_drive_recursive(drive_id="0AOMVrKhhWKIwUk9PVA")

# Get already-manifested files from Notion
manifested = get_manifested_files(notion_db_id="357fdc24...", notion_api_key=NOTION_API_KEY)

# De-duplicate
to_process = [f for f in all_media if f["name"] not in manifested]

print(f"De-duplication: {len(all_media)} total - {len(manifested)} manifested = {len(to_process)} to process")
```

## Performance Characteristics

**Recursive scan:**
- 5,000 folders × 2 API calls per folder (list + check for subfolders) = 10,000 API calls
- At 100ms per call = ~17 minutes
- Add 30 minutes for pagination on large folders
- **Total: 45-60 minutes**

**Notion query:**
- 7,000 entries ÷ 100 per page = 70 pages
- At 0.3s per page = 21 seconds
- **Total: ~30 seconds**

**De-duplication:**
- In-memory set lookup: O(n) where n = number of files
- For 44k files: **< 1 second**

## Common Pitfalls

1. **Assuming root scan is complete** — Root-level scans show ~1,000 files but the drive has 40,000+. Always use recursive BFS.

2. **Querying Notion with wrong property name** — The title field is `"Asset"`, not `"Asset Name"` or `"Name"`. Query the DB schema first to confirm.

3. **Not paginating Notion results** — Notion returns max 100 results per page. Always check `has_more` and use `next_cursor`.

4. **Case-sensitive filename matching** — Drive filenames may have different casing than Notion entries. Consider normalizing to lowercase before comparison:
   ```python
   manifested = {name.lower() for name in get_manifested_files(...)}
   to_process = [f for f in all_media if f["name"].lower() not in manifested]
   ```

5. **Ignoring Drive File ID** — If you have Drive File IDs in Notion, use those for dedup instead of filenames (more reliable):
   ```python
   # Query Notion for Drive File IDs
   manifested_ids = {page["properties"]["Drive File ID"]["rich_text"][0]["text"]["content"]
                     for page in notion_results}
   to_process = [f for f in all_media if f["id"] not in manifested_ids]
   ```

6. **Scanning too frequently** — A full recursive scan takes 45-60 minutes. Cache the scan results to `/tmp/drive_scan.json` and reuse for multiple batch jobs.

## Caching Strategy

Save scan results to avoid re-scanning:

```python
import json

# Save scan results
with open("/tmp/drive_scan.json", "w") as f:
    json.dump(all_media, f, indent=2)

# Load cached results (if < 24 hours old)
import os
import time

scan_file = "/tmp/drive_scan.json"
if os.path.exists(scan_file):
    age_hours = (time.time() - os.path.getmtime(scan_file)) / 3600
    if age_hours < 24:
        with open(scan_file) as f:
            all_media = json.load(f)
        print(f"Using cached scan ({len(all_media)} files, {age_hours:.1f}h old)")
    else:
        all_media = scan_drive_recursive(drive_id)
else:
    all_media = scan_drive_recursive(drive_id)
```
