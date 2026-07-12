# Gemini Batch vs Direct API Decision Guide

**Last updated:** May 2026

## When Batch API Fails (Current State)

As of May 2026, Gemini Batch API has persistent operational issues:

1. **Wrong endpoint** — Documentation shows `POST /v1beta/batches` but this returns 404
2. **Unclear payload structure** — The correct batch submission format is not documented
3. **File API rate limiting** — Even with 60s delays, uploading multiple chunks hits 429 errors
4. **Zero successful batches in testing** — Despite uploading 15+ GB of JSONL chunks, no batches were created

## Direct API Works at Scale

**Use direct `generateContent` calls even for 10,000+ files.**

### Performance Characteristics

- **Throughput:** ~1 file per 8-12 seconds (including analysis + 1s delay)
- **Error rate:** 20-30% of requests fail with 503 "high demand"
- **Total time for 10,000 files:** ~24-30 hours
- **Reliability:** Very high when retry logic is implemented

### Error Handling Pattern

```python
def analyze_file_with_retry(mime_type, local_path, max_attempts=3):
    """Analyze file with exponential backoff for 429/503 errors."""
    file_size = Path(local_path).stat().st_size
    if file_size > 15 * 1024 * 1024:
        return None  # Skip large files for inline processing

    with open(local_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()

    is_video = mime_type.startswith('video/')
    prompt = f"Analyze this {'video' if is_video else 'image'} and extract metadata..."

    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": mime_type, "data": b64}},
            {"text": prompt}
        ]}],
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"

    for attempt in range(max_attempts):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = 30 * (attempt + 1)  # 30s, 60s, 90s
                log(f"  Rate limited ({e.code}), waiting {wait}s...")
                time.sleep(wait)
                continue
            log(f"  API error {e.code}: {e.read().decode()[:200]}")
            return None
        except Exception as e:
            log(f"  API error: {e}")
            return None

    return None  # All retries exhausted
```

### Progress Tracking

Track completed and failed file IDs separately:

```python
progress = {
    "completed": ["file_id_1", "file_id_2", ...],
    "failed": ["file_id_3", "file_id_4", ...]
}

# Save after each file
with open(PROGRESS_FILE, 'w') as f:
    json.dump(progress, f, indent=2)
```

This allows resuming after crashes without reprocessing.

## Decision Matrix

| Files | Strategy | Expected Time | Notes |
|-------|----------|---------------|-------|
| < 100 | Direct API | 15-20 min | Simple, reliable |
| 100-1,000 | Direct API | 2-3 hours | 20-30% retry rate expected |
| 1,000-10,000 | Direct API | 24-30 hours | Still more reliable than batch |
| > 10,000 | Direct API | 30+ hours | Split into chunks if needed |

**Never use Batch API until endpoint issues are resolved.**

## Common Failures Observed

### 1. Batch Endpoint 404

```
POST https://generativelanguage.googleapis.com/v1beta/batches
Response: 404 Not Found
```

**Cause:** Endpoint doesn't exist or requires different URL structure.

**Workaround:** Use direct API.

### 2. File API Upload 429

```
Uploading chunk 16/19...
Upload init failed: HTTP Error 429: Too Many Requests
```

**Cause:** Uploading multiple large JSONL files (>1GB each) triggers rate limits even with 60s delays.

**Workaround:** Don't use File API. Inline base64 for files <15MB.

### 3. Gemini 503 "High Demand"

```
API error 503: {
  "error": {
    "code": 503,
    "message": "This model is currently experiencing high demand...",
    "status": "UNAVAILABLE"
  }
}
```

**Cause:** Gemini API is rate-limited, not just temporarily overloaded.

**Workaround:** Exponential backoff (30s, 60s, 90s) with 3 retry attempts.

### 4. Video Processing Failures

```
API error 400: {
  "error": {
    "code": 400,
    "message": "The video is corrupted or has wrong video metadata. 0 Frames found.",
    "status": "INVALID_ARGUMENT"
  }
}
```

**Cause:** Some video files have metadata issues or unsupported codecs.

**Workaround:** Log as failed, skip. Don't retry corrupted files.

## Lessons Learned

1. **Batch API documentation is outdated** — The documented endpoint and payload format don't work
2. **File API has strict rate limits** — Uploading >10 large files in quick succession triggers 429s
3. **Direct API is more reliable** — Even with 30% error rate, it completes the job
4. **503 errors are persistent** — Not temporary spikes; expect them on every run
5. **Progress tracking is essential** — 24-hour jobs will crash; resume capability is mandatory
6. **Inline base64 works for <15MB** — No need for File API overhead for most images
7. **Videos often fail** — Many video files have codec/metadata issues; log and skip
