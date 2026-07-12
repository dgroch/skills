#!/usr/bin/env python3
"""
Full Vision Manifest + Move Script for Fig & Bloom asset library.
Processes unmanifested files on Synology Photos shared drive using
Gemini 2.0 Flash Lite via OpenRouter for vision analysis.
Updates Notion manifest and moves files to organized folders.

Prerequisites:
  - source /opt/data/.env (for OPENROUTER_API_KEY, NOTION_API_KEY)
  - gws CLI configured at /tmp/gws_config
  - ffmpeg, ffprobe installed
  - /tmp/vm_drive_files.json from prior drive scan (or script will rescan)

Usage:
  set -a; source /opt/data/.env; set +a
  python3 vision_manifest_openrouter.py --execute

The explicit ``--execute`` flag is mandatory because this script creates
Notion records and moves Drive files.

Progress: /tmp/vision_manifest_progress.json (resume-capable)
Log: /tmp/vision_manifest_log.txt
"""
import argparse
import json, os, subprocess, sys, time, base64
import urllib.request
from pathlib import Path

# Load .env
_env_path = Path("/opt/data/.env")
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key not in os.environ:
                os.environ[key] = value

DRIVE_ID = "0AOMVrKhhWKIwUk9PVA"
NOTION_DB = "357fdc24425f81ed805cc4f9aff0665f"
GWS = "/opt/data/npm-global/bin/gws"
GWS_ENV = {
    **os.environ,
    "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config",
    "GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND": "file",
}
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")

PROGRESS_FILE = "/tmp/vision_manifest_progress.json"
LOG_FILE = "/tmp/vision_manifest_log.txt"
DELAY_BETWEEN_FILES = 2.5


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def gws_cmd(args, timeout=30):
    cmd = [GWS] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=GWS_ENV)
        out = result.stdout
        lines = [l for l in out.split("\n") if l.strip() and not l.startswith("Using keyring")]
        clean = "\n".join(lines).strip()
        if not clean:
            return None, result.stderr.strip() or f"Exit {result.returncode}"
        depth, start = 0, None
        for i, c in enumerate(clean):
            if c == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        return json.loads(clean[start : i + 1]), None
                    except:
                        pass
                    start = None
        return None, "Parse error"
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


def download_file(file_id, mime_type):
    """Download file from Drive to /tmp using gws drive files get."""
    is_video = "video" in mime_type
    is_image = "image" in mime_type
    if not (is_image or is_video):
        return None, "Unsupported mime type"

    filepath = f"/tmp/vm_{file_id}"
    filename = f"vm_{file_id}"

    cmd = [
        GWS,
        "drive",
        "files",
        "get",
        "--params",
        json.dumps({"fileId": file_id, "alt": "media", "supportsAllDrives": True}),
        "--output",
        filename,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, env=GWS_ENV, cwd="/tmp"
        )
        out = result.stdout
        lines = [l for l in out.split("\n") if l.strip() and not l.startswith("Using keyring")]
        clean = "\n".join(lines).strip()

        if "saved_file" in clean and os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            return filepath, None
        if "error" in clean.lower():
            return None, f"gws error: {clean[:200]}"
        return None, f"Download failed: {clean[:200]}"
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


def extract_video_frames(filepath):
    """Extract 3 frames from video for analysis."""
    frames = []
    try:
        dur_result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", filepath],
            capture_output=True,
            text=True,
            timeout=10,
        )
        duration = float(dur_result.stdout.strip()) if dur_result.stdout.strip() else 10
        duration = max(duration, 1.0)

        for pct in [0.25, 0.5, 0.75]:
            ts = duration * pct
            frame_path = f"{filepath}_f{int(pct * 100)}.jpg"
            subprocess.run(
                ["ffmpeg", "-y", "-i", filepath, "-ss", str(ts), "-vframes", "1", "-q:v", "2", frame_path],
                capture_output=True,
                timeout=10,
            )
            if os.path.exists(frame_path) and os.path.getsize(frame_path) > 100:
                frames.append(frame_path)
    except Exception as e:
        log(f"  Frame extraction error: {e}")
    return frames


def analyze_with_gemini(image_paths, mime_type, filename):
    """Send images to Gemini via OpenRouter for analysis."""
    prompt = """Analyze this brand asset for a flower business called Fig & Bloom.
Return ONLY valid JSON with these fields:
{
  "overall_description": "2-3 sentence description",
  "content_type": "Product Photography" or "Lifestyle Photography" or "UGC" or "Video Still" or "Graphic/Design" or "Brand Asset" or "Behind the Scenes" or "Unknown",
  "mood_tone": ["elegant","natural","romantic","rustic","modern","minimal","vibrant","soft","dark","bright"],
  "visual_tags": ["bouquet","roses","studio","outdoor","hands","vase","candle","gift box","plant","greenery","flat lay","texture"],
  "people_present": "none" or "one person" or "hands only" or "multiple people" or "staff in apron",
  "products_flowers": ["Pink Rose Bouquet","Marseille","Amour","candle","vase","plant","none"],
  "setting_location": "studio" or "outdoor" or "home interior" or "shop interior" or "delivery" or "event" or "unknown",
  "usable_for": ["product page","social media","email campaign","ad creative","website hero","blog"],
  "orientation": "landscape" or "portrait" or "square",
  "reorg_notes": "Brief note on where this file should be organized"
}
Return only JSON, no markdown."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://figandbloom.com.au",
        "X-Title": "Fig&Bloom Manifesting",
    }

    content_parts = [{"type": "text", "text": prompt}]
    for img_path in image_paths:
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        mime = "image/jpeg" if img_path.endswith(".jpg") else "image/png"
        content_parts.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_data}"}})

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

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end]), None
        return None, f"Invalid JSON: {text[:200]}"
    except Exception as e:
        return None, f"API error: {e}"


def get_or_create_folder(parent_name, sub_name=""):
    parent_id = find_folder(parent_name, DRIVE_ID)
    if not parent_id:
        parent_id = create_folder(parent_name, DRIVE_ID)
        if not parent_id:
            return None
    if not sub_name:
        return parent_id
    sub_id = find_folder(sub_name, parent_id)
    if not sub_id:
        sub_id = create_folder(sub_name, parent_id)
    return sub_id


def find_folder(name, parent_id):
    data, err = gws_cmd(
        [
            "drive",
            "files",
            "list",
            "--params",
            json.dumps(
                {
                    "q": f"'{parent_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                    "supportsAllDrives": True,
                    "includeItemsFromAllDrives": True,
                    "pageSize": 1,
                    "fields": "files(id,name)",
                }
            ),
        ]
    )
    if data and data.get("files"):
        return data["files"][0]["id"]
    return None


def create_folder(name, parent_id):
    body = json.dumps({"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]})
    data, err = gws_cmd(
        ["drive", "files", "create", "--json", body, "--params", json.dumps({"supportsAllDrives": True})],
        timeout=30,
    )
    return data.get("id") if data else None


def classify_file(file_info, analysis):
    ct = analysis.get("content_type", "").lower()
    setting = analysis.get("setting_location", "").lower()
    products = analysis.get("products_flowers", [])
    fname = file_info.get("name", "").lower()

    if "product" in ct or "product photography" in ct:
        parent = "Products"
        sub = products[0] if products and products[0] != "none" else "Unnamed"
    elif "lifestyle" in ct:
        parent = "Lifestyle"
        if "studio" in setting:
            sub = "Studio"
        elif "home" in setting or "interior" in setting:
            sub = "Home"
        elif "outdoor" in setting:
            sub = "Outdoor"
        else:
            sub = "Other"
    elif "ugc" in ct:
        parent = "UGC"
        sub = "TikTok" if "tiktok" in fname else "Instagram"
    elif "video" in ct or "video" in file_info.get("mimeType", ""):
        parent = "Video"
        sub = "Brand" if "brand" in ct else ("Product" if "product" in ct else "Raw")
    elif "graphic" in ct or "design" in ct:
        parent = "Graphics"
        sub = "Promotional"
    elif "brand" in ct:
        parent = "Brand Assets"
        sub = ""
    else:
        if "image" in file_info.get("mimeType", ""):
            parent, sub = "Products", "Unnamed"
        else:
            parent, sub = "Video", "Raw"
    return parent, sub


def move_file(file_id, target_folder_id):
    data, err = gws_cmd(
        [
            "drive",
            "files",
            "get",
            "--params",
            json.dumps({"fileId": file_id, "supportsAllDrives": True, "fields": "id,parents"}),
        ]
    )
    if not data:
        return False, f"Can't get parents: {err}"
    current = data.get("parents", [])
    if not current:
        return False, "No current parents"
    remove = ",".join(current)
    data, err = gws_cmd(
        [
            "drive",
            "files",
            "update",
            "--params",
            json.dumps(
                {
                    "fileId": file_id,
                    "addParents": target_folder_id,
                    "removeParents": remove,
                    "supportsAllDrives": True,
                }
            ),
            "--json",
            "{}",
        ],
        timeout=30,
    )
    if err:
        return False, err
    return True, "moved"


def create_notion_entry(file_info, analysis):
    file_id = file_info["id"]
    name = file_info.get("name", "")

    def clean_tags(tags):
        cleaned = []
        for t in tags:
            t = t.replace(",", " ").strip()[:100]
            if t:
                cleaned.append(t)
        return cleaned[:5]

    page_data = {
        "parent": {"database_id": NOTION_DB},
        "properties": {
            "Asset": {"title": [{"text": {"content": name[:100]}}]},
            "Drive File ID": {"rich_text": [{"text": {"content": file_id}}]},
            "Content Type": {"select": {"name": analysis.get("content_type", "Unknown")[:100]}},
            "Mood Tone": {"multi_select": [{"name": m[:100]} for m in clean_tags(analysis.get("mood_tone", []))]},
            "Visual Tags": {"multi_select": [{"name": t[:100]} for t in clean_tags(analysis.get("visual_tags", []))]},
            "People Present": {"rich_text": [{"text": {"content": analysis.get("people_present", "none")[:100]}}]},
            "Products / Flowers": {
                "multi_select": [{"name": p[:100]} for p in clean_tags(analysis.get("products_flowers", [])) if p != "none"]
            },
            "Setting / Location": {"rich_text": [{"text": {"content": analysis.get("setting_location", "unknown")[:100]}}]},
            "Usable For": {"multi_select": [{"name": u[:100]} for u in clean_tags(analysis.get("usable_for", []))]},
            "Overall Description": {"rich_text": [{"text": {"content": analysis.get("overall_description", "")[:2000]}}]},
            "Reorg Notes": {"rich_text": [{"text": {"content": analysis.get("reorg_notes", "")[:500]}}]},
            "Taxonomy Version": {"rich_text": [{"text": {"content": "v1-full-vision"}}]},
        },
    }

    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=json.dumps(page_data).encode(),
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, None
    except Exception as e:
        return False, str(e)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"processed": [], "failed": [], "manifest_ids": [], "start_time": None, "drive_files_cached": False}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def get_drive_files():
    log("Scanning drive...")
    all_files = []
    page_token = None
    while True:
        params = {
            "corpora": "drive",
            "driveId": DRIVE_ID,
            "includeItemsFromAllDrives": True,
            "supportsAllDrives": True,
            "q": "trashed=false and (mimeType contains 'image/' or mimeType contains 'video/')",
            "pageSize": 500,
            "fields": "files(id,name,mimeType,parents,modifiedTime,size,webViewLink),nextPageToken",
        }
        if page_token:
            params["pageToken"] = page_token
        data, err = gws_cmd(["drive", "files", "list", "--params", json.dumps(params)], timeout=60)
        if err:
            log(f"  Scan error: {err}")
            break
        files = data.get("files", [])
        all_files.extend(files)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.5)
    log(f"  Found {len(all_files)} media files")
    return all_files


def get_notion_ids():
    log("Loading Notion manifest...")
    ids = set()
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{NOTION_DB}/query",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            log(f"  Notion error: {e}")
            break
        for page in data.get("results", []):
            props = page.get("properties", {})
            for item in props.get("Drive File ID", {}).get("rich_text", []):
                fid = item.get("text", {}).get("content", "").strip()
                if fid and "/" not in fid:
                    ids.add(fid)
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        time.sleep(0.3)
    log(f"  {len(ids)} existing entries")
    return ids


def cleanup_files(file_id, base_path):
    if os.path.exists(base_path):
        try:
            os.remove(base_path)
        except:
            pass
    for f in os.listdir("/tmp"):
        if f.startswith(f"vm_{file_id}_"):
            try:
                os.remove(f"/tmp/{f}")
            except:
                pass


def main():
    log("=" * 60)
    log("VISION MANIFEST + MOVE - STARTING")
    log("=" * 60)

    progress = load_progress()
    if progress.get("start_time") is None:
        progress["start_time"] = time.time()
        save_progress(progress)

    if not progress.get("drive_files_cached"):
        all_files = get_drive_files()
        with open("/tmp/vm_drive_files.json", "w") as f:
            json.dump(all_files, f)
        progress["drive_files_cached"] = True
        save_progress(progress)
    else:
        with open("/tmp/vm_drive_files.json") as f:
            all_files = json.load(f)

    if not progress.get("manifest_ids"):
        manifest_ids = get_notion_ids()
        progress["manifest_ids"] = list(manifest_ids)
        save_progress(progress)
    else:
        manifest_ids = set(progress["manifest_ids"])

    processed = set(progress.get("processed", []))
    failed = set(progress.get("failed", []))

    to_process = [f for f in all_files if f["id"] not in manifest_ids and f["id"] not in processed and f["id"] not in failed]

    total = len(to_process)
    log(f"\nQueue: {total} files to process")
    log(f"Already manifested: {len(manifest_ids)}")
    log(f"Previously processed: {len(processed)}")
    log(f"Previously failed: {len(failed)}")

    current = 0
    for file_info in to_process:
        current += 1
        file_id = file_info["id"]
        filename = file_info.get("name", "")
        mime = file_info.get("mimeType", "")

        log(f"\n[{current}/{total}] {filename[:60]}")

        filepath, err = download_file(file_id, mime)
        if err:
            log(f"  ❌ Download: {err}")
            failed.add(file_id)
            progress["failed"].append(file_id)
            save_progress(progress)
            continue

        if "video" in mime:
            image_paths = extract_video_frames(filepath)
            if not image_paths:
                log(f"  ❌ Frame extraction failed")
                cleanup_files(file_id, filepath)
                failed.add(file_id)
                progress["failed"].append(file_id)
                save_progress(progress)
                continue
        else:
            image_paths = [filepath]

        analysis, err = analyze_with_gemini(image_paths, mime, filename)
        if err:
            log(f"  ❌ Analysis: {err}")
            cleanup_files(file_id, filepath)
            failed.add(file_id)
            progress["failed"].append(file_id)
            save_progress(progress)
            continue

        log(f"  ✅ {analysis.get('content_type', 'Unknown')} | {analysis.get('setting_location', 'unknown')}")

        ok, err = create_notion_entry(file_info, analysis)
        if err:
            log(f"  ⚠️ Notion: {err[:100]}")
        else:
            log(f"  ✅ Notion entry created")
            manifest_ids.add(file_id)

        parent, sub = classify_file(file_info, analysis)
        folder_id = get_or_create_folder(parent, sub)
        if folder_id:
            ok, err = move_file(file_id, folder_id)
            if ok:
                log(f"  ✅ Moved to {parent}/{sub}")
            else:
                log(f"  ⚠️ Move: {err}")
        else:
            log(f"  ⚠️ Can't create folder {parent}/{sub}")

        cleanup_files(file_id, filepath)
        processed.add(file_id)
        progress["processed"].append(file_id)
        save_progress(progress)

        if current % 10 == 0:
            elapsed = time.time() - progress["start_time"]
            rate = current / (elapsed / 60) if elapsed > 0 else 0
            remaining = total - current
            eta = remaining / rate if rate > 0 else 0
            log(f"\n📊 {current}/{total} ({current/total*100:.1f}%) | {rate:.1f}/min | ETA: {eta:.0f}min | Failed: {len(failed)}")

        time.sleep(DELAY_BETWEEN_FILES)

    elapsed = time.time() - progress["start_time"]
    log(f"\n{'='*60}")
    log(f"✅ DONE: {current} files in {elapsed/60:.1f}min")
    log(f"   Failed: {len(failed)}")
    log(f"   Rate: {current/(elapsed/60):.1f}/min")
    log(f"{'='*60}")


def cli():
    parser = argparse.ArgumentParser(
        description="Manifest unindexed Fig & Bloom assets and move them in Drive."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="perform live API writes and Drive moves (required)",
    )
    args = parser.parse_args()
    if not args.execute:
        parser.error("refusing live run without explicit --execute")
    if not OPENROUTER_KEY or not NOTION_TOKEN:
        parser.error("OPENROUTER_API_KEY and NOTION_API_KEY must be configured")
    main()


if __name__ == "__main__":
    cli()
