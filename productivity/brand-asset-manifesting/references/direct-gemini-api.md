# Direct Gemini API Pattern (Preferred over OpenRouter)

When manifesting brand assets with vision analysis, use Google's native Gemini API directly rather than routing through OpenRouter. This avoids credit exhaustion issues and provides more reliable access.

## API Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}
```

## Vision-Capable Models

- `gemini-2.5-flash` (fastest, best for batch processing)
- `gemini-2.5-pro` (highest quality)
- `gemini-2.0-flash`
- `gemini-2.0-flash-lite-001`

## Request Structure

For image analysis with inline base64:

```json
{
  "contents": [{
    "parts": [
      {
        "text": "Your prompt here"
      },
      {
        "inline_data": {
          "mime_type": "image/jpeg",
          "data": "<base64-encoded-image>"
        }
      }
    ]
  }]
}
```

## Environment Setup

Required environment variable:
```bash
export GEMINI_API_KEY="<your-gemini-api-key>"
```

The key should be stored in the active profile's `.env` file and loaded without printing it:
```bash
set -a; source "${HERMES_HOME:-$HOME/.hermes}/.env"; set +a
```

## Example Python Implementation

```python
import base64
import os
from pathlib import Path
import requests

def analyze_image_with_gemini(image_path, prompt):
    """Analyze an image using direct Gemini API"""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    # Read and encode image
    image_bytes = Path(image_path).read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Detect mime type
    mime_type = "image/jpeg"
    if image_path.lower().endswith('.png'):
        mime_type = "image/png"
    elif image_path.lower().endswith('.gif'):
        mime_type = "image/gif"

    # Build request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_b64
                    }
                }
            ]
        }]
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']
```

## Advantages over OpenRouter

1. **No credit limits**: OpenRouter credits can exhaust mid-job, causing entire batch to fail
2. **Direct access**: No intermediary, faster response times
3. **Reliable**: No rate limiting issues during long manifest jobs
4. **Cost**: Uses your Google Cloud quota directly

## When to Use OpenRouter Instead

Only fall back to OpenRouter if:
- You don't have a GEMINI_API_KEY available
- You need to use a model that's only available through OpenRouter
- You're doing a small one-off analysis and already have OpenRouter credits

For production manifesting workloads (hundreds or thousands of assets), always prefer direct Gemini API.

## Rate Limiting

Gemini API has generous rate limits, but for large batches:
- Add 2-3 second delays between requests
- Monitor for 429 (rate limit) responses
- Implement exponential backoff on failures

The manifest script at `scripts/vision_manifest_gemini.py` implements these patterns.
