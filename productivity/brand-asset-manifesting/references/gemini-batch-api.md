# Gemini Batch API for Large-Scale Vision Manifesting

## When to Use

For **1,000+ assets**, use the Gemini Batch API instead of individual `generateContent` calls:

- **50% cheaper** than standard API
- **No rate limiting** — async processing
- **Handles videos properly** — upload via File API first, reference in batch
- **24h target turnaround** (usually faster)

## Workflow

### 1. Upload Media to Gemini File API

Each file requires a resumable upload:

```python
import urllib.request
import json

def upload_to_gemini_file_api(local_path, filename, mime_type, api_key):
    """Upload file to Gemini File API, returns file URI."""

    # Start resumable upload
    metadata = {"file": {"display_name": filename}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}",
        data=json.dumps(metadata).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start"
        },
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=30)
    upload_url = resp.headers["X-Goog-Upload-URL"]

    # Upload file content
    file_size = os.path.getsize(local_path)
    with open(local_path, "rb") as f:
        data = f.read()

    req = urllib.request.Request(
        upload_url,
        data=data,
        headers={
            "Content-Length": str(file_size),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize"
        },
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=300)
    result = json.loads(resp.read())
    return result["file"]["uri"]  # e.g., "https://generativelanguage.googleapis.com/v1beta/files/abc123"
```

**MIME types:**
- Images: `image/jpeg`, `image/png`, `image/webp`, `image/heic`
- Videos: `video/mp4`, `video/quicktime`, `video/x-msvideo`

### 2. Generate JSONL Request File

One JSON object per line, each with a unique `key` and full `request` structure:

```python
import json

requests = []
for i, file_info in enumerate(media_files):
    file_uri = file_info["gemini_uri"]  # from upload step
    mime_type = file_info["mime_type"]

    prompt = """Analyze this image and extract metadata. Return JSON with:
- content_type: one of "Product Photography", "Lifestyle Photography", "Influencer UGC", "Behind the Scenes"
- mood: 3-5 mood tags (e.g., "vibrant", "natural", "minimal")
- visual_tags: 5-8 visual elements (e.g., "pink hydrangea", "marble surface", "natural light")
- products: list any Fig & Bloom products visible (bouquets named after cities like Marseille, Osaka, etc.)
- usable_for: where this could be used (e.g., "Instagram Feed", "Website Hero", "Email Campaign")

Be specific and brand-aware."""

    request = {
        "key": f"request-{i}",
        "request": {
            "contents": [{
                "parts": [
                    {"file_data": {"mime_type": mime_type, "file_uri": file_uri}},
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "mood": {"type": "array", "items": {"type": "string"}},
                        "visual_tags": {"type": "array", "items": {"type": "string"}},
                        "products": {"type": "array", "items": {"type": "string"}},
                        "usable_for": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
    }
    requests.append(request)

# Write JSONL (one object per line, no trailing newline)
with open("/tmp/batch_requests.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")
```

### 3. Upload JSONL to File API

Same resumable upload pattern as media files, but `mime_type="application/jsonl"`.

### 4. Submit Batch Job

```python
batch_request = {
    "displayName": "fig-bloom-manifest-batch",
    "model": "models/gemini-2.5-flash",
    "inputConfig": {
        "gcsSource": {
            "uri": jsonl_file_uri  # from step 3
        }
    }
}

req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/batches?key={api_key}",
    data=json.dumps(batch_request).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read())
batch_name = result["name"]  # e.g., "batches/xyz789"
```

### 5. Poll for Completion

Check every 60 seconds until `state` is `JOB_STATE_SUCCEEDED`:

```python
import time

while True:
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/{batch_name}?key={api_key}",
        method="GET"
    )
    resp = urllib.request.urlopen(req, timeout=30)
    status = json.loads(resp.read())

    state = status["state"]
    print(f"Batch state: {state}")

    if state == "JOB_STATE_SUCCEEDED":
        results_uri = status["output"]["gcsSource"]["uri"]
        break
    elif state in ["JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"]:
        raise Exception(f"Batch failed: {status.get('error', 'Unknown error')}")

    time.sleep(60)
```

### 6. Download and Parse Results

Results are a JSONL file with one response per line:

```python
req = urllib.request.Request(results_uri)
resp = urllib.request.urlopen(req, timeout=300)
results_data = resp.read().decode("utf-8")

results = {}
for line in results_data.strip().split("\n"):
    if not line.strip():
        continue
    result = json.loads(line)
    key = result["key"]

    # Check if request succeeded
    if "response" in result:
        text = result["response"]["candidates"][0]["content"]["parts"][0]["text"]
        analysis = json.loads(text)
        results[key] = {"status": "success", "analysis": analysis}
    elif "error" in result:
        results[key] = {"status": "failed", "error": result["error"]}
```

### 7. Create Notion Entries

Use the analysis results to populate the Notion database:

```python
for i, file_info in enumerate(media_files):
    key = f"request-{i}"
    result = results.get(key)

    if result and result["status"] == "success":
        analysis = result["analysis"]

        # Create Notion page with structured properties
        page_data = {
            "parent": {"database_id": notion_db_id},
            "properties": {
                "Asset": {"title": [{"text": {"content": file_info["name"]}}]},
                "Content Type": {"select": {"name": analysis["content_type"]}},
                "Visual Tags": {"multi_select": [{"name": tag} for tag in analysis["visual_tags"]]},
                "Mood": {"multi_select": [{"name": mood} for mood in analysis["mood"]]},
                "Drive File ID": {"rich_text": [{"text": {"content": file_info["id"]}}]}
            }
        }

        # POST to Notion API
        req = urllib.request.Request(
            f"https://api.notion.com/v1/pages",
            data=json.dumps(page_data).encode(),
            headers={
                "Authorization": f"Bearer {notion_api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )
        urllib.request.urlopen(req, timeout=30)
        time.sleep(0.3)  # Notion rate limit
```

## Critical Requirements

1. **File API uploads required** — Cannot use inline base64 data in batch requests
2. **JSONL format** — One JSON object per line, not a JSON array
3. **Structured output** — Use `responseMimeType: "application/json"` with `responseSchema` for reliable parsing
4. **Error handling** — Check each result for `response` vs `error` fields
5. **Rate limiting** — Batch API itself has no rate limits, but Notion API still needs 0.3s delays

## Cost Comparison

For 1,000 images:
- **Direct API**: ~$2.50 (at $2.50 per 1M tokens input, $10 per 1M tokens output)
- **Batch API**: ~$1.25 (50% discount)

For 40,000 images:
- **Direct API**: ~$100
- **Batch API**: ~$50

## Limitations

- **24h turnaround** — Not suitable for real-time workflows
- **File size limits** — Individual files must be < 2GB
- **No streaming** — Results only available after batch completes
- **JSONL size limit** — Max 2GB per JSONL file (usually fine for 40k requests)

## Debugging

**Check batch status:**
```bash
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/batches?pageSize=10"
```

**View recent batches:**
Returns list of batch jobs with `name`, `state`, `createTime`, `endTime`.

**Cancel a running batch:**
```bash
curl -X POST -H "Authorization: Bearer $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/batches/{batch_name}:cancel"
```
