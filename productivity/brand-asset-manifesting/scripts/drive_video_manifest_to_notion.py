#!/usr/bin/env python3
"""Manifest Google Drive/shared-drive videos into a Notion brand asset database.

Env:
  DRIVE_FOLDER_ID                         required source folder
  MANIFEST_LIMIT                          optional max videos, 0/all if omitted
  GEMINI_MODEL                            default google/gemini-3-flash-preview
  NOTION_BRAND_ASSET_DATABASE_ID          existing Notion database (recommended)
  NOTION_BRAND_ASSET_PARENT_PAGE_ID       parent page if DB should be created
  OPENROUTER_API_KEY, NOTION_API_KEY      required
"""
from __future__ import annotations

import base64, datetime as dt, json, math, mimetypes, os, re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
LIMIT = int(os.environ.get("MANIFEST_LIMIT") or "0")
GEMINI_PROVIDER = os.environ.get("GEMINI_PROVIDER", "openrouter").lower()
MODEL = os.environ.get("GEMINI_MODEL", "google/gemini-3-flash-preview" if GEMINI_PROVIDER == "openrouter" else "gemini-2.5-flash")
NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")
DB_ID = os.environ.get("NOTION_BRAND_ASSET_DATABASE_ID")
PARENT_PAGE_ID = os.environ.get("NOTION_BRAND_ASSET_PARENT_PAGE_ID")
WORKDIR = Path(os.environ.get("MANIFEST_WORKDIR", "/opt/data/brand-asset-manifests/notion-drive-assets"))

SETUP_TEXT = """
Brand asset manifesting setup required. Configure these in your private env file; never commit secrets:

Required source/destination:
  DRIVE_FOLDER_ID=<Google Drive folder ID to crawl>
  NOTION_BRAND_ASSET_DATABASE_ID=<existing Notion database ID>
    OR
  NOTION_BRAND_ASSET_PARENT_PAGE_ID=<Notion page ID where the script can create a database>
  MANIFEST_WORKDIR=/private/local/output/path

Gemini access path, choose one:
  # Option A: Gemini via OpenRouter
  GEMINI_PROVIDER=openrouter
  GEMINI_MODEL=google/gemini-3-flash-preview
  Set OPENROUTER_API_KEY in private env only.

  # Option B: Direct Google Gemini API
  GEMINI_PROVIDER=google
  GEMINI_MODEL=gemini-2.5-flash
  Set GEMINI_API_KEY or GOOGLE_API_KEY in private env only.

Notion:
  Set NOTION_API_KEY in private env only.
  Share the target Notion page/database with the Notion integration.
""".strip()
DOWNLOADS, FRAMES, OUT = WORKDIR / "downloads", WORKDIR / "frames", WORKDIR / "output"

GWS_ENV = os.environ.copy()
GWS_ENV["PATH"] = "/opt/data/npm-global/bin:/opt/data/home/.local/bin:" + GWS_ENV.get("PATH", "")
GWS_ENV["HOME"] = "/opt/data/home"


def log(msg):
    print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=GWS_ENV, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"command failed {p.returncode}: {' '.join(cmd)}\nSTDOUT={p.stdout[-1000:]}\nSTDERR={p.stderr[-2000:]}")
    return p


def gws_json(args, cwd=None):
    p = run(["gws"] + args + ["--format", "json"], cwd=cwd)
    return json.loads(p.stdout)


def notion(method, path, body=None):
    key = os.environ.get("NOTION_API_KEY")
    if not key: raise RuntimeError("NOTION_API_KEY missing")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=data, method=method,
        headers={"Authorization": "Bearer " + key, "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Notion {method} {path} failed {e.code}: {e.read().decode()[:1000]}")


def rt(text, limit=1900):
    return {"rich_text": [{"text": {"content": str(text or "")[:limit]}}]}


def title(text):
    return {"title": [{"text": {"content": str(text or "Untitled")[:200]}}]}


def sel(name):
    if not name: return None
    return {"select": {"name": str(name)[:100].replace(",", " ")}}


def ms(vals, maxn=12):
    seen, out = set(), []
    for v in vals or []:
        s = str(v).strip().replace(",", " ")[:90]
        if s and s.lower() not in seen:
            seen.add(s.lower()); out.append({"name": s})
        if len(out) >= maxn: break
    return {"multi_select": out}


def db_properties():
    return {
        "Asset": {"title": {}}, "Drive File ID": {"rich_text": {}}, "File Handle": {"rich_text": {}},
        "Drive Link": {"url": {}}, "Preview URL": {"url": {}}, "Preview": {"files": {}}, "Source Folder": {"rich_text": {}}, "Folder Path": {"rich_text": {}},
        "Mime Type": {"rich_text": {}}, "Asset Type": {"select": {"options": [{"name":"video"},{"name":"image"},{"name":"other"}]}},
        "Duration Seconds": {"number": {"format": "number"}}, "Dimensions": {"rich_text": {}},
        "Aspect Ratio": {"select": {}}, "Orientation": {"select": {}}, "Size MB": {"number": {"format":"number"}},
        "Overall Description": {"rich_text": {}}, "Content Type": {"select": {}}, "Mood Tone": {"multi_select": {}},
        "Visual Tags": {"multi_select": {}}, "People Present": {"rich_text": {}}, "Products / Flowers": {"multi_select": {}},
        "Setting / Location": {"rich_text": {}}, "Usable For": {"multi_select": {}}, "Reorg Notes": {"rich_text": {}},
        "Timestamp Beats": {"rich_text": {}}, "Manifest Model": {"rich_text": {}}, "Manifested At": {"date": {}}
    }


def ensure_schema(db):
    existing = set((db.get("properties") or {}).keys())
    additions = {k: v for k, v in db_properties().items() if k not in existing}
    # Title properties cannot be added/changed after creation. If the target DB lacks Asset, fail clearly.
    if "Asset" not in existing:
        raise RuntimeError("Target Notion database must have an 'Asset' title property, or provide a parent page so this script can create the database.")
    additions.pop("Asset", None)
    if additions:
        log(f"adding missing Notion properties: {', '.join(sorted(additions))}")
        notion("PATCH", f"/databases/{db['id']}", {"properties": additions})


def ensure_db():
    global DB_ID
    if DB_ID:
        db = notion("GET", f"/databases/{DB_ID}")
        ensure_schema(db)
        return DB_ID
    if not PARENT_PAGE_ID:
        raise RuntimeError("Set NOTION_BRAND_ASSET_DATABASE_ID or NOTION_BRAND_ASSET_PARENT_PAGE_ID")
    props = db_properties()
    db = notion("POST", "/databases", {"parent": {"page_id": PARENT_PAGE_ID}, "title": [{"text":{"content":"Brand Asset Manifest"}}], "properties": props})
    DB_ID = db["id"]
    log(f"created Notion database {DB_ID}")
    return DB_ID


def list_videos(folder_id):
    files, token = [], None
    while True:
        params = {"q": f'"{folder_id}" in parents and trashed=false and mimeType contains "video/"', "includeItemsFromAllDrives": True, "supportsAllDrives": True, "pageSize": 100, "fields": "files(id,name,mimeType,parents,driveId,size,videoMediaMetadata,webViewLink,thumbnailLink,modifiedTime),nextPageToken"}
        if token: params["pageToken"] = token
        data = gws_json(["drive", "files", "list", "--params", json.dumps(params)])
        files += data.get("files", [])
        token = data.get("nextPageToken")
        if not token: break
    return files[:LIMIT] if LIMIT else files


def clean(name): return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:150]


def download(file):
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    suffix = Path(file["name"]).suffix or mimetypes.guess_extension(file.get("mimeType", "")) or ".mp4"
    local = DOWNLOADS / f"{file['id']}_{clean(Path(file['name']).stem)}{suffix}"
    if not local.exists() or local.stat().st_size == 0:
        gws_json(["drive", "files", "get", "--params", json.dumps({"fileId": file["id"], "alt": "media"}), "--output", local.name], cwd=DOWNLOADS)
    return local


def ffprobe(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(p.stdout)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"duration": float(v.get("duration") or data.get("format", {}).get("duration") or 0), "width": int(v.get("width") or 0), "height": int(v.get("height") or 0)}


def ratio(w,h):
    if not w or not h: return "unknown"
    g = math.gcd(w,h); return f"{w//g}:{h//g}"


def frames(path, file_id, duration):
    outdir = FRAMES / file_id; outdir.mkdir(parents=True, exist_ok=True)
    safe_end = max(0, duration - 1.0) if duration > 2 else max(0, duration * .75)
    n = min(8, max(4, int(duration // 3) + 2)) if duration else 4
    times = sorted(set(round(safe_end * i / max(1, n-1), 2) for i in range(n)))
    result = []
    for t in times:
        out = outdir / f"t{str(t).replace('.','_')}.jpg"
        if not out.exists() or out.stat().st_size == 0:
            ok = False
            for tt in [t, max(0,t-.5), max(0,t-1), 0]:
                if out.exists() and out.stat().st_size == 0: out.unlink()
                p = run(["ffmpeg", "-y", "-ss", str(tt), "-i", str(path), "-frames:v", "1", "-vf", "scale='min(640,iw)':-2", "-q:v", "4", str(out)], check=False)
                if p.returncode == 0 and out.exists() and out.stat().st_size > 0:
                    t, ok = tt, True; break
            if not ok: continue
        result.append({"time": t, "path": out})
    return result


def data_url(path): return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def gemini_prompt(file, meta):
    return f"""Create a brand asset manifest entry for this video. Original filename: {file['name']}. Drive file ID: {file['id']}. Duration {meta['duration']:.2f}s, dimensions {meta['width']}x{meta['height']}, aspect {ratio(meta['width'], meta['height'])}. Analyse the video as a whole from sampled timestamp frames. Return ONLY JSON: {{"overall_description":"2-4 sentences", "content_type":"short category", "mood_tone":["tags"], "visual_tags":["tags"], "people_present":"none/one/multiple/unclear plus brief notes", "products_or_flowers":["items"], "setting_location":"brief", "usable_for":["future AI/content uses"], "reorg_notes":"how to file/group this", "beats":[{{"start_s":0,"end_s":1.5,"shot_description":"visual action", "shot_type":"wide/medium/close-up/detail/movement/text-overlay", "ai_usefulness":"why useful"}}]}}"""


def parse_json_text(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S|re.I)
    return json.loads(text)


def gemini(file, meta, frs):
    prompt = gemini_prompt(file, meta)
    if GEMINI_PROVIDER == "google":
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENAI_API_KEY")
        if not key: raise RuntimeError("Direct Gemini selected but GEMINI_API_KEY/GOOGLE_API_KEY is missing.\n" + SETUP_TEXT)
        parts = [{"text": prompt}]
        for f in frs:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(Path(f["path"]).read_bytes()).decode()}})
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2200, "responseMimeType": "application/json"}}
        req = urllib.request.Request(url, method="POST", headers={"Content-Type":"application/json", "x-goog-api-key": key}, data=json.dumps(payload).encode())
        with urllib.request.urlopen(req, timeout=120) as r: data = json.loads(r.read().decode())
        return parse_json_text(data["candidates"][0]["content"]["parts"][0]["text"])

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key: raise RuntimeError("OpenRouter Gemini selected but OPENROUTER_API_KEY is missing.\n" + SETUP_TEXT)
    content = [{"type":"text", "text": prompt}] + [{"type":"image_url", "image_url":{"url": data_url(f["path"])}} for f in frs]
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", method="POST",
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json","HTTP-Referer":"https://hermes-agent.local","X-Title":"Brand Asset Manifest"},
        data=json.dumps({"model": MODEL, "messages":[{"role":"user","content":content}], "temperature":0.2, "response_format":{"type":"json_object"}, "max_tokens":2200}).encode())
    with urllib.request.urlopen(req, timeout=120) as r: data = json.loads(r.read().decode())
    return parse_json_text(data["choices"][0]["message"]["content"])


def query_existing(db_id):
    existing, cursor = {}, None
    while True:
        body = {"page_size": 100}
        if cursor: body["start_cursor"] = cursor
        res = notion("POST", f"/databases/{db_id}/query", body)
        for page in res.get("results", []):
            prop = page.get("properties", {}).get("Drive File ID", {}).get("rich_text", [])
            if prop:
                existing[prop[0].get("plain_text", "")] = page["id"]
        if not res.get("has_more"): break
        cursor = res.get("next_cursor")
    return existing


def beat_text(beats):
    lines=[]
    for b in beats or []:
        lines.append(f"{b.get('start_s',0)}-{b.get('end_s',b.get('start_s',0))}s: {b.get('shot_description','')} [{b.get('shot_type','')}; use: {b.get('ai_usefulness','')}]")
    return "\n".join(lines)[:1900]


def sync_page(db_id, existing, file, meta, analysis):
    w,h=meta['width'],meta['height']; orient = 'portrait' if h>w else 'landscape' if w>h else 'square' if w and h else 'unknown'
    preview_url = os.environ.get("BRAND_CDN_PREVIEW_URL") or file.get("thumbnailLink")
    props = {
        "Asset": title(file["name"]), "Drive File ID": rt(file["id"]), "File Handle": rt(f"drive:{file['id']} | {file['name']}"),
        "Drive Link": {"url": file.get("webViewLink", f"https://drive.google.com/file/d/{file['id']}/view")},
        "Preview URL": {"url": preview_url} if preview_url else {"url": None},
        "Preview": {"files": [{"name": "preview", "external": {"url": preview_url}}]} if preview_url else {"files": []},
        "Source Folder": rt(DRIVE_FOLDER_ID), "Folder Path": rt(DRIVE_FOLDER_ID), "Mime Type": rt(file.get("mimeType","")), "Asset Type": sel("video"),
        "Duration Seconds": {"number": round(meta["duration"],2)}, "Dimensions": rt(f"{w}x{h}"), "Aspect Ratio": sel(ratio(w,h)), "Orientation": sel(orient),
        "Size MB": {"number": round(int(file.get("size") or 0)/1048576, 2)},
        "Overall Description": rt(analysis.get("overall_description","")), "Content Type": sel(analysis.get("content_type","")),
        "Mood Tone": ms(analysis.get("mood_tone")), "Visual Tags": ms(analysis.get("visual_tags")), "People Present": rt(analysis.get("people_present","")),
        "Products / Flowers": ms(analysis.get("products_or_flowers")), "Setting / Location": rt(analysis.get("setting_location","")),
        "Usable For": ms(analysis.get("usable_for")), "Reorg Notes": rt(analysis.get("reorg_notes","")),
        "Timestamp Beats": rt(beat_text(analysis.get("beats"))), "Manifest Model": rt(MODEL), "Manifested At": {"date":{"start": dt.datetime.now(dt.timezone.utc).isoformat()}},
    }
    page_id = existing.get(file["id"])
    if page_id:
        notion("PATCH", f"/pages/{page_id}", {"properties": props}); return "updated"
    notion("POST", "/pages", {"parent": {"database_id": db_id}, "properties": props}); return "created"


def main():
    missing = []
    if not DRIVE_FOLDER_ID: missing.append("DRIVE_FOLDER_ID")
    if not (DB_ID or PARENT_PAGE_ID): missing.append("NOTION_BRAND_ASSET_DATABASE_ID or NOTION_BRAND_ASSET_PARENT_PAGE_ID")
    if not os.environ.get("NOTION_API_KEY"): missing.append("NOTION_API_KEY")
    if GEMINI_PROVIDER == "google" and not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENAI_API_KEY")):
        missing.append("GEMINI_API_KEY/GOOGLE_API_KEY")
    if GEMINI_PROVIDER != "google" and not os.environ.get("OPENROUTER_API_KEY"):
        missing.append("OPENROUTER_API_KEY")
    if missing:
        raise RuntimeError("Missing setup: " + ", ".join(missing) + "\n\n" + SETUP_TEXT)
    for d in (DOWNLOADS, FRAMES, OUT): d.mkdir(parents=True, exist_ok=True)
    db_id = ensure_db(); existing = query_existing(db_id)
    videos = list_videos(DRIVE_FOLDER_ID); log(f"found {len(videos)} videos to consider; existing Notion IDs {len(existing)}")
    records=[]; created=updated=failed=0
    for i, file in enumerate(videos,1):
        try:
            if file["id"] in existing:
                log(f"{i}/{len(videos)} refresh {file['name']}")
            else:
                log(f"{i}/{len(videos)} create {file['name']}")
            local=download(file); meta=ffprobe(local); frs=frames(local,file["id"],meta["duration"]); analysis=gemini(file,meta,frs)
            status=sync_page(db_id, existing, file, meta, analysis)
            created += status=="created"; updated += status=="updated"; existing[file["id"]]="synced"
            records.append({"file":file,"meta":meta,"analysis":analysis,"status":status})
        except Exception as e:
            failed += 1; log(f"FAILED {file.get('id')} {file.get('name')}: {e}"); records.append({"file":file,"error":repr(e)})
        time.sleep(0.35)
    out = OUT / f"drive-video-manifest-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps({"db_id":db_id,"folder_id":DRIVE_FOLDER_ID,"model":MODEL,"created":created,"updated":updated,"failed":failed,"records":records}, indent=2, ensure_ascii=False))
    print(json.dumps({"status":"complete","db_id":db_id,"videos":len(videos),"created":created,"updated":updated,"failed":failed,"backup":str(out)}, indent=2))

if __name__ == "__main__": main()
