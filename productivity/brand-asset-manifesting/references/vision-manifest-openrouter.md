# Vision Asset Manifesting via OpenRouter + Gemini

## Overview

Alternative to the Gemini-provider-based manifesting pipeline. Uses OpenRouter's Gemini models for vision analysis when the Gemini provider is unavailable or when OpenRouter credits are preferred.

## Model Selection

- **`google/gemini-2.0-flash-lite-001`** — fast, cheap, works for bulk analysis (~$0.001/image)
- **`google/gemini-2.5-flash`** — higher quality, more expensive
- Avoid `google/gemini-2.0-flash-exp:free` (deprecated, returns 401)
- Avoid `google/gemini-2.0-flash` (not a valid model ID on OpenRouter)

## Pattern

```python
import base64, json, urllib.request

def analyze_with_openrouter(image_paths, api_key, prompt):
    """Send images to Gemini via OpenRouter for analysis."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-domain.com",
        "X-Title": "Your App Name",
    }

    content_parts = [{"type": "text", "text": prompt}]

    for img_path in image_paths:
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        mime = "image/jpeg" if img_path.endswith(".jpg") else "image/png"
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{img_data}"}
        })

    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": 500,
    }

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers=headers,
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())

    text = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end]), None
    return None, f"Invalid JSON: {text[:200]}"
```

## Video Frame Extraction

For video assets, extract 3 frames at 25%, 50%, 75% of duration:

```python
import subprocess

def extract_video_frames(filepath, duration=None):
    """Extract 3 frames from video for analysis."""
    if duration is None:
        dur_result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", filepath],
            capture_output=True, text=True, timeout=10
        )
        duration = float(dur_result.stdout.strip()) if dur_result.stdout.strip() else 10

    frames = []
    for pct in [0.25, 0.5, 0.75]:
        ts = duration * pct
        frame_path = f"{filepath}_f{int(pct*100)}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-i", filepath, "-ss", str(ts),
             "-vframes", "1", "-q:v", "2", frame_path],
            capture_output=True, timeout=10
        )
        if os.path.exists(frame_path) and os.path.getsize(frame_path) > 100:
            frames.append(frame_path)
    return frames
```

## Performance

- ~2.3 files/minute end-to-end (download → extract → analyze → Notion → move)
- ~$0.001-0.003 per image on Gemini 2.0 Flash Lite
- 9,295 files ≈ $10-30 in API credits, ~67 hours wall time
- Can be run in background with `notify_on_complete=true`
- Progress saved to `/tmp/vision_manifest_progress.json` for resume capability

## Reusable Script

Full pipeline script at `/tmp/vision_manifest_full.py` (session-generated, not committed).
Copies should be saved to `scripts/` if needed for future reuse.
