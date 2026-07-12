#!/usr/bin/env python3
"""
Vision-based asset manifesting using direct Gemini API.
Analyzes images/videos from Google Drive and creates Notion manifest entries.

This is the reference implementation showing how to:
1. Download files from Drive using gws
2. Analyze them with Gemini Vision API
3. Upload thumbnails to CDN
4. Create/update Notion database entries

Usage:
    set -a; source /opt/data/profiles/director/.env; set +a
    python3 vision_manifest_gemini.py --drive-folder-id <ID> --notion-db-id <ID>

See SKILL.md for full workflow and setup instructions.
"""

import os
import sys
import json
import base64
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
CDN_UPLOAD_URL=os.environ.get("CDN_UPLOAD_URL")


def analyze_with_gemini(image_path: Path, prompt: str) -> Dict[str, Any]:
    """Analyze an image using direct Gemini API.

    Args:
        image_path: Path to image file
        prompt: Analysis prompt (should request JSON output)

    Returns:
        Parsed JSON response from Gemini
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    import requests

    # Read and encode image
    image_bytes = image_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Detect mime type
    mime_type = "image/jpeg"
    suffix = image_path.suffix.lower()
    if suffix == '.png':
        mime_type = "image/png"
    elif suffix in ('.gif', '.webp'):
        mime_type = f"image/{suffix[1:]}"

    # Build request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"

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

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()

    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text']

    # Parse JSON from response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            return json.loads(text[start:end].strip())
        raise


def upload_to_cdn(file_path: Path, filename: str) -> Optional[str]:
    """Upload a file to the CDN and return the public URL.

    Args:
        file_path: Local path to file
        filename: Desired filename on CDN

    Returns:
        Public URL or None if upload failed
    """
    if not CDN_UPLOAD_URL:
        return None
    import requests

    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                CDN_UPLOAD_URL,
                files={'file': (filename, f)},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('url')
    except Exception as e:
        print(f"CDN upload failed: {e}")
        return None


def create_notion_entry(db_id: str, properties: Dict[str, Any]) -> Optional[str]:
    """Create a new entry in Notion database.

    Args:
        db_id: Notion database ID
        properties: Property values for the new page

    Returns:
        Page ID or None if creation failed
    """
    if not NOTION_API_KEY:
        return None
    import requests

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {NOTION_API_KEY}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            json={
                "parent": {"database_id": db_id},
                "properties": properties
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['id']
    except Exception as e:
        print(f"Notion creation failed: {e}")
        return None


def download_from_drive(file_id: str, output_path: Path) -> bool:
    """Download a file from Google Drive using gws.

    Args:
        file_id: Drive file ID
        output_path: Local path to save file

    Returns:
        True if successful
    """
    env = os.environ.copy()
    env["GOOGLE_WORKSPACE_CLI_CONFIG_DIR"] = "/tmp/gws_config"
    env["KEYRING_BACKEND"] = "file"

    result = subprocess.run(
        [
            "gws", "drive", "files", "get",
            "--file-id", file_id,
            "--alt", "media",
            "--output", str(output_path),
            "--supports-all-drives"
        ],
        env=env,
        capture_output=True,
        text=True
    )

    return result.returncode == 0


# Example analysis prompt for brand assets
BRAND_ASSET_PROMPT = """Analyze this brand asset for Fig & Bloom.

Extract the following information and return as JSON:
{
  "asset_name": "descriptive name for the asset",
  "content_type": "one of: product-photo, lifestyle-photo, ugc, video, graphic",
  "visual_description": "brief description of what's in the image",
  "mood_tone": ["array", "of", "mood", "keywords"],
  "color_palette": ["array", "of", "dominant", "colors"],
  "products_shown": ["array", "of", "product", "names"],
  "usable_for": ["array", "of", "potential", "uses"],
  "orientation": "portrait, landscape, or square"
}

Be specific and descriptive. Focus on visual elements that would help someone find and use this asset."""


def cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Reference helpers for direct Gemini asset manifesting."
    )
    parser.parse_args()
    print("This is a reference implementation. See SKILL.md for full workflow.")
    print("\nTo use these functions in your own script:")
    print("  from vision_manifest_gemini import analyze_with_gemini, upload_to_cdn, create_notion_entry")


if __name__ == "__main__":
    cli()
