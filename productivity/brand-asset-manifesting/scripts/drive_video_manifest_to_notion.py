#!/usr/bin/env python3
"""Manifest Google Drive/shared-drive videos into a Notion brand asset database.

Env:
  DRIVE_FOLDER_ID                         required source folder or shared-drive root
  MANIFEST_LIMIT                          optional max assets, 0/all if omitted
  MANIFEST_RECURSIVE                      default true; crawl nested folders
  GEMINI_PROVIDER/GEMINI_MODEL            openrouter or google direct Gemini
  NOTION_BRAND_ASSET_DATABASE_ID          existing Notion database (recommended)
  NOTION_BRAND_ASSET_PARENT_PAGE_ID       parent page if DB should be created
  NOTION_API_KEY plus OPENROUTER_API_KEY or GEMINI_API_KEY required privately
"""
from __future__ import annotations

import base64, datetime as dt, json, math, mimetypes, os, re, shutil, subprocess, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
MANIFEST_INPUT_JSON = os.environ.get("MANIFEST_INPUT_JSON")
LIMIT = int(os.environ.get("MANIFEST_LIMIT") or "0")
RECURSIVE = os.environ.get("MANIFEST_RECURSIVE", "true").lower() not in {"0", "false", "no"}
RENAME_FILES = os.environ.get("MANIFEST_RENAME_FILES", "true").lower() not in {"0", "false", "no"}
SKIP_EXISTING = os.environ.get("MANIFEST_SKIP_EXISTING", "false").lower() in {"1", "true", "yes"}
PRODUCT_CLASSIFICATION_ENABLED = os.environ.get("PRODUCT_CLASSIFICATION_ENABLED", "false").lower() in {"1", "true", "yes"}
PRODUCT_MATCH_THRESHOLD = float(os.environ.get("PRODUCT_MATCH_THRESHOLD") or "0.8")
PRODUCT_CATALOG_JSON = os.environ.get("PRODUCT_CATALOG_JSON")
TAXONOMY_VERSION = os.environ.get("ASSET_TAXONOMY_VERSION", "v0-discovery")
BRAND_CDN_BASE_URL = (os.environ.get("BRAND_CDN_BASE_URL") or "").rstrip("/")
BRAND_CDN_UPLOAD_DIR = os.environ.get("BRAND_CDN_UPLOAD_DIR")
BRAND_CDN_UPLOAD_TOKEN = os.environ.get("BRAND_CDN_UPLOAD_TOKEN")
BRAND_CDN_UPLOAD_BUCKET = os.environ.get("BRAND_CDN_UPLOAD_BUCKET")
BRAND_CDN_UPLOAD_URL_TEMPLATE = os.environ.get("BRAND_CDN_UPLOAD_URL_TEMPLATE")
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
  Optional: BRAND_CDN_BASE_URL + BRAND_CDN_UPLOAD_DIR to publish thumbnails via local/static mount.
  Optional: BRAND_CDN_BASE_URL + BRAND_CDN_UPLOAD_TOKEN + BRAND_CDN_UPLOAD_BUCKET to publish via Worker HTTP upload.

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
        "Timestamp Beats": {"rich_text": {}}, "Manifest Model": {"rich_text": {}}, "Taxonomy Version": {"rich_text": {}},
        "Taxonomy Candidates": {"multi_select": {}}, "Original Filename": {"rich_text": {}}, "Renamed At": {"date": {}}, "Manifested At": {"date": {}},
        "Contains Product": {"select": {"options": [{"name":"yes"},{"name":"no"}]}}, "Product Name": {"rich_text": {}}, "Product Match Confidence": {"number": {"format":"percent"}}
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


def list_children(folder_id):
    files, token = [], None
    while True:
        params = {"q": f'"{folder_id}" in parents and trashed=false', "includeItemsFromAllDrives": True, "supportsAllDrives": True, "pageSize": 100, "fields": "files(id,name,mimeType,parents,driveId,size,videoMediaMetadata,webViewLink,thumbnailLink,modifiedTime),nextPageToken"}
        if token: params["pageToken"] = token
        data = gws_json(["drive", "files", "list", "--params", json.dumps(params)])
        files += data.get("files", [])
        token = data.get("nextPageToken")
        if not token: break
    return files


def list_assets(folder_id):
    assets, seen_folders, queue = [], set(), [(folder_id, folder_id)]
    while queue:
        current, path = queue.pop(0)
        if current in seen_folders: continue
        seen_folders.add(current)
        for f in list_children(current):
            mt = f.get("mimeType", "")
            f["folderPath"] = path
            if mt == "application/vnd.google-apps.folder" and RECURSIVE:
                queue.append((f["id"], path + "/" + f.get("name", f["id"])))
            elif mt.startswith("video/") or mt.startswith("image/"):
                assets.append(f)
                if LIMIT and len(assets) >= LIMIT:
                    return assets
    return assets


def load_input_assets(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        assets = data
    elif isinstance(data, dict) and isinstance(data.get("files"), list):
        assets = data["files"]
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        assets = [r.get("file") for r in data["records"] if isinstance(r.get("file"), dict)]
    else:
        raise RuntimeError(f"MANIFEST_INPUT_JSON must contain a list or a dict with files/records: {path}")
    normalized = []
    for f in assets:
        if not isinstance(f, dict) or not f.get("id"):
            continue
        mt = f.get("mimeType", "")
        if mt.startswith("video/") or mt.startswith("image/"):
            f.setdefault("folderPath", f.get("folderPath") or f.get("sourceFolder") or DRIVE_FOLDER_ID or "manifest-input")
            normalized.append(f)
            if LIMIT and len(normalized) >= LIMIT:
                break
    return normalized


def asset_type(file):
    mt = file.get("mimeType", "")
    if mt.startswith("video/"): return "video"
    if mt.startswith("image/"): return "image"
    return "other"


def clean(name): return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:150]


def slugify(text, max_len=52):
    text = (text or "asset").lower()
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text or "asset")[:max_len].strip("-") or "asset"


def intuitive_basename(file, analysis, kind):
    # Use the model's concise category/tags, but keep it short and Drive-friendly.
    parts = []
    for key in ("content_type", "setting_location"):
        val = str(analysis.get(key) or "").strip()
        if val: parts.append(val)
    for key in ("products_or_flowers", "visual_tags", "usable_for"):
        vals = analysis.get(key) or []
        if isinstance(vals, str): vals = [vals]
        for v in vals[:3]:
            if v and len(parts) < 5: parts.append(str(v))
    base = slugify(" ".join(parts), 64)
    if base == "asset": base = slugify(Path(file.get("name", kind)).stem, 64)
    return f"{base}-{file['id'][:6]}"


def rename_drive_file(file, analysis, kind):
    if not RENAME_FILES: return file.get("name"), None
    old = file.get("name") or "asset"
    ext = Path(old).suffix or mimetypes.guess_extension(file.get("mimeType", "")) or (".mp4" if kind == "video" else ".jpg")
    new_name = intuitive_basename(file, analysis, kind) + ext.lower()
    if new_name == old: return old, None
    params = {"fileId": file["id"], "supportsAllDrives": True, "fields": "id,name,webViewLink"}
    updated = gws_json(["drive", "files", "update", "--params", json.dumps(params), "--json", json.dumps({"name": new_name})])
    file["name"] = updated.get("name", new_name)
    file["webViewLink"] = updated.get("webViewLink", file.get("webViewLink"))
    return old, file["name"]


def sync_thumbnail_to_cdn(file, frs, analysis, kind):
    # Publish a generated thumbnail/contact frame to a public CDN path when configured.
    # Supported modes:
    # 1) BRAND_CDN_UPLOAD_DIR: copy to a local/static directory served at BRAND_CDN_BASE_URL.
    # 2) BRAND_CDN_UPLOAD_TOKEN + BRAND_CDN_UPLOAD_BUCKET: POST bytes to a Worker upload endpoint.
    if not (BRAND_CDN_BASE_URL and frs):
        return file.get("thumbnailLink")
    src = Path(frs[0]["path"])
    if not src.exists(): return file.get("thumbnailLink")
    date_path = dt.datetime.now(dt.timezone.utc).strftime("%Y/%m")
    rel = Path("asset-manifest") / date_path / f"{intuitive_basename(file, analysis, kind)}.jpg"
    rel_url = urllib.parse.quote(str(rel).replace(os.sep, "/"), safe="/")

    if BRAND_CDN_UPLOAD_DIR:
        dest = Path(BRAND_CDN_UPLOAD_DIR) / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return BRAND_CDN_BASE_URL + "/" + rel_url

    if BRAND_CDN_UPLOAD_TOKEN and BRAND_CDN_UPLOAD_BUCKET:
        template = BRAND_CDN_UPLOAD_URL_TEMPLATE or (BRAND_CDN_BASE_URL + "/upload/{bucket}/{key}")
        key = str(rel).replace(os.sep, "/")
        url = template.format(
            base=BRAND_CDN_BASE_URL,
            bucket=urllib.parse.quote(BRAND_CDN_UPLOAD_BUCKET, safe=""),
            key=urllib.parse.quote(key, safe="/"),
            key_encoded=urllib.parse.quote(key, safe=""),
        )
        data = src.read_bytes()
        req = urllib.request.Request(url, data=data, method="POST", headers={
            "Authorization": "Bearer " + BRAND_CDN_UPLOAD_TOKEN,
            "Content-Type": "image/jpeg",
            "User-Agent": "HermesAgent/brand-asset-manifesting",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
            try:
                payload = json.loads(body)
                if payload.get("url"):
                    return payload["url"]
            except json.JSONDecodeError:
                pass
            return BRAND_CDN_BASE_URL + "/" + urllib.parse.quote(BRAND_CDN_UPLOAD_BUCKET, safe="") + "/" + rel_url
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            log(f"CDN upload failed {e.code}; using Drive thumbnail fallback: {body}")
            return file.get("thumbnailLink")

    return file.get("thumbnailLink")


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


def frames(path, file_id, duration, mime_type="video/mp4"):
    outdir = FRAMES / file_id; outdir.mkdir(parents=True, exist_ok=True)
    if mime_type.startswith("image/"):
        out = outdir / "image_preview.jpg"
        if not out.exists() or out.stat().st_size == 0:
            run(["ffmpeg", "-y", "-i", str(path), "-frames:v", "1", "-vf", "scale='min(640,iw)':-2", "-q:v", "4", str(out)], check=False)
        return [{"time": 0, "path": out}] if out.exists() and out.stat().st_size > 0 else []
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


def gemini_prompt(file, meta, kind, product_catalog=None):
    product_instruction = ""
    if PRODUCT_CLASSIFICATION_ENABLED:
        candidates = product_catalog or []
        catalog_text = json.dumps([p.get("product_name") for p in candidates[:80]], ensure_ascii=False)
        product_instruction = f"""
Also classify whether this asset clearly features a specific Fig & Bloom product from this candidate catalogue: {catalog_text}
Only choose an exact product_name from the candidate catalogue. If no exact product match is visually clear, use null. Return confidence as 0-1. Use confidence >= {PRODUCT_MATCH_THRESHOLD:.2f} only when the match is visually strong, not just because words appear in the filename.
Include this JSON field: "product_classification": {{"contains_product": true/false, "product_name": "exact catalogue name or null", "confidence": 0.0}}.
""".strip()
    if kind == "image":
        return f"""Create a brand asset manifest entry for this image. Original filename: {file['name']}. Drive file ID: {file['id']}. Dimensions {meta['width']}x{meta['height']}, aspect {ratio(meta['width'], meta['height'])}. {product_instruction} Return ONLY JSON: {{"overall_description":"2-4 sentences", "content_type":"short category", "mood_tone":["tags"], "visual_tags":["tags"], "people_present":"none/one/multiple/unclear plus brief notes", "products_or_flowers":["items"], "setting_location":"brief", "usable_for":["future AI/content uses"], "reorg_notes":"how to file/group this", "product_classification":{{"contains_product":false,"product_name":null,"confidence":0.0}}, "beats":[{{"start_s":0,"end_s":0,"shot_description":"visual composition and subject", "shot_type":"wide/medium/close-up/detail/product/lifestyle", "ai_usefulness":"why useful"}}]}}"""
    return f"""Create a brand asset manifest entry for this video. Original filename: {file['name']}. Drive file ID: {file['id']}. Duration {meta['duration']:.2f}s, dimensions {meta['width']}x{meta['height']}, aspect {ratio(meta['width'], meta['height'])}. Analyse the video as a whole from sampled timestamp frames. {product_instruction} Return ONLY JSON: {{"overall_description":"2-4 sentences", "content_type":"short category", "mood_tone":["tags"], "visual_tags":["tags"], "people_present":"none/one/multiple/unclear plus brief notes", "products_or_flowers":["items"], "setting_location":"brief", "usable_for":["future AI/content uses"], "reorg_notes":"how to file/group this", "product_classification":{{"contains_product":false,"product_name":null,"confidence":0.0}}, "beats":[{{"start_s":0,"end_s":1.5,"shot_description":"visual action", "shot_type":"wide/medium/close-up/detail/movement/text-overlay", "ai_usefulness":"why useful"}}]}}"""


def parse_json_text(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S|re.I)
    data = json.loads(text)
    # Some vision responses wrap the object in a one-item list. Normalise so
    # downstream Notion sync can always use analysis.get(...).
    if isinstance(data, list):
        data = data[0] if data and isinstance(data[0], dict) else {"overall_description": str(data)[:500], "beats": []}
    return data


def as_list(value):
    if value is None: return []
    if isinstance(value, list): return value
    return [value]


def load_product_catalog():
    if not PRODUCT_CATALOG_JSON:
        return []
    path = Path(PRODUCT_CATALOG_JSON)
    if not path.exists():
        log(f"product catalog not found: {path}")
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data.get("products", data) if isinstance(data, dict) else data
    products = []
    for item in raw or []:
        if isinstance(item, str):
            name, aliases = item, []
        elif isinstance(item, dict):
            name, aliases = item.get("product_name") or item.get("name") or item.get("title"), item.get("aliases") or []
        else:
            continue
        name = str(name or "").strip()
        if name:
            products.append({"product_name": name[:120], "aliases": [str(a)[:120] for a in aliases[:6] if str(a).strip()]})
    return products


def product_tokens(text):
    stop = {"the","and","for","with","from","fig","bloom","figandbloom","photo","photos","image","video","final","copy","px","jpg","png","mov","mp4","day","2026","2025","2024"}
    return {t for t in re.findall(r"[a-z0-9]+", str(text).lower()) if len(t) > 2 and t not in stop}


def product_candidates(file, catalog, maxn=80):
    if not catalog:
        return []
    hay = " ".join([file.get("name", ""), file.get("folderPath", "")])
    ht = product_tokens(hay)
    scored = []
    for p in catalog:
        text = " ".join([p["product_name"]] + p.get("aliases", []))
        pt = product_tokens(text)
        score = len(ht & pt)
        if score:
            scored.append((score, p))
    if not scored:
        return catalog[:maxn]
    scored.sort(key=lambda x: (-x[0], x[1]["product_name"].lower()))
    return [p for _, p in scored[:maxn]]


def normalise_product_classification(analysis):
    pc = analysis.get("product_classification") or {}
    if not isinstance(pc, dict):
        pc = {}
    try:
        conf = float(pc.get("confidence") or 0)
    except Exception:
        conf = 0.0
    if conf > 1:
        conf = conf / 100.0
    conf = max(0.0, min(1.0, conf))
    raw_name = str(pc.get("product_name") or "").strip()
    raw_contains = pc.get("contains_product")
    if isinstance(raw_contains, str):
        raw_contains = raw_contains.strip().lower() in {"1", "true", "yes"}
    contains = bool(raw_contains) and conf >= PRODUCT_MATCH_THRESHOLD and raw_name.lower() not in {"", "null", "none", "unknown"}
    return {"contains_product": contains, "product_name": raw_name if contains else "", "confidence": conf}


def gemini(file, meta, frs, kind, product_catalog=None):
    prompt = gemini_prompt(file, meta, kind, product_catalog=product_candidates(file, product_catalog or []))
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


def sync_page(db_id, existing, file, meta, analysis, preview_url=None, original_name=None, renamed_name=None):
    kind = asset_type(file)
    w,h=meta['width'],meta['height']; orient = 'portrait' if h>w else 'landscape' if w>h else 'square' if w and h else 'unknown'
    preview_url = preview_url or file.get("thumbnailLink")
    product_match = normalise_product_classification(analysis) if PRODUCT_CLASSIFICATION_ENABLED else {"contains_product": False, "product_name": "", "confidence": 0.0}
    props = {
        "Asset": title(file["name"]), "Drive File ID": rt(file["id"]), "File Handle": rt(f"drive:{file['id']} | {file['name']}"),
        "Drive Link": {"url": file.get("webViewLink", f"https://drive.google.com/file/d/{file['id']}/view")},
        "Preview URL": {"url": preview_url} if preview_url else {"url": None},
        "Preview": {"files": [{"name": "preview", "external": {"url": preview_url}}]} if preview_url else {"files": []},
        "Source Folder": rt(DRIVE_FOLDER_ID), "Folder Path": rt(file.get("folderPath", DRIVE_FOLDER_ID)), "Mime Type": rt(file.get("mimeType","")), "Asset Type": sel(kind),
        "Duration Seconds": {"number": round(meta["duration"],2)}, "Dimensions": rt(f"{w}x{h}"), "Aspect Ratio": sel(ratio(w,h)), "Orientation": sel(orient),
        "Size MB": {"number": round(int(file.get("size") or 0)/1048576, 2)},
        "Overall Description": rt(analysis.get("overall_description","")), "Content Type": sel(analysis.get("content_type","")),
        "Mood Tone": ms(analysis.get("mood_tone")), "Visual Tags": ms(analysis.get("visual_tags")), "People Present": rt(analysis.get("people_present","")),
        "Products / Flowers": ms(analysis.get("products_or_flowers")), "Setting / Location": rt(analysis.get("setting_location","")),
        "Usable For": ms(analysis.get("usable_for")), "Reorg Notes": rt(analysis.get("reorg_notes","")),
        "Timestamp Beats": rt(beat_text(analysis.get("beats"))), "Manifest Model": rt(MODEL), "Taxonomy Version": rt(TAXONOMY_VERSION),
        "Taxonomy Candidates": ms(as_list(analysis.get("visual_tags")) + as_list(analysis.get("usable_for")) + as_list(analysis.get("products_or_flowers")), maxn=16),
        "Original Filename": rt(original_name or file.get("name", "")), "Renamed At": {"date":{"start": dt.datetime.now(dt.timezone.utc).isoformat()}} if renamed_name else {"date": None},
        "Manifested At": {"date":{"start": dt.datetime.now(dt.timezone.utc).isoformat()}},
        "Contains Product": sel("yes" if product_match["contains_product"] else "no"), "Product Name": rt(product_match["product_name"]),
        "Product Match Confidence": {"number": product_match["confidence"]},
    }
    page_id = existing.get(file["id"])
    if page_id:
        notion("PATCH", f"/pages/{page_id}", {"properties": props}); return "updated"
    notion("POST", "/pages", {"parent": {"database_id": db_id}, "properties": props}); return "created"


def taxonomy_report(records, out_dir):
    from collections import Counter
    counters = {"content_type": Counter(), "visual_tags": Counter(), "usable_for": Counter(), "products_or_flowers": Counter(), "mood_tone": Counter()}
    for r in records:
        a = r.get("analysis") or {}
        for key, c in counters.items():
            vals = a.get(key) or []
            if isinstance(vals, str): vals = [vals]
            for v in vals:
                v = str(v).strip().lower()
                if v: c[v] += 1
    report = {"taxonomy_version": TAXONOMY_VERSION, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "top_terms": {k: c.most_common(40) for k,c in counters.items()}, "recommendations": []}
    for key, terms in report["top_terms"].items():
        rare = [t for t,n in terms if n == 1][:10]
        if rare:
            report["recommendations"].append(f"Review one-off {key} values for synonyms/merge candidates: {', '.join(rare[:6])}")
    path = out_dir / f"taxonomy-review-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return str(path)


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
    product_catalog = load_product_catalog() if PRODUCT_CLASSIFICATION_ENABLED else []
    if PRODUCT_CLASSIFICATION_ENABLED:
        log(f"product classification enabled; catalog candidates loaded {len(product_catalog)}; threshold {PRODUCT_MATCH_THRESHOLD:.2f}")
    assets = load_input_assets(MANIFEST_INPUT_JSON) if MANIFEST_INPUT_JSON else list_assets(DRIVE_FOLDER_ID)
    if SKIP_EXISTING:
        before = len(assets)
        assets = [f for f in assets if f.get("id") not in existing]
        log(f"skipped {before - len(assets)} existing Notion assets via MANIFEST_SKIP_EXISTING")
    log(f"found {len(assets)} assets to consider; existing Notion IDs {len(existing)}")
    records=[]; created=updated=failed=0
    for i, file in enumerate(assets,1):
        try:
            if file["id"] in existing:
                log(f"{i}/{len(assets)} refresh {file['name']}")
            else:
                log(f"{i}/{len(assets)} create {file['name']}")
            local=download(file); meta=ffprobe(local); kind=asset_type(file); frs=frames(local,file["id"],meta["duration"],file.get("mimeType","")); analysis=gemini(file,meta,frs,kind,product_catalog=product_catalog)
            original_name, renamed_name = rename_drive_file(file, analysis, kind)
            preview_url = sync_thumbnail_to_cdn(file, frs, analysis, kind)
            status=sync_page(db_id, existing, file, meta, analysis, preview_url=preview_url, original_name=original_name, renamed_name=renamed_name)
            created += status=="created"; updated += status=="updated"; existing[file["id"]]="synced"
            records.append({"file":file,"meta":meta,"analysis":analysis,"status":status,"original_name":original_name,"renamed_name":renamed_name,"preview_url":preview_url})
        except Exception as e:
            failed += 1; log(f"FAILED {file.get('id')} {file.get('name')}: {e}"); records.append({"file":file,"error":repr(e)})
        time.sleep(0.35)
    out = OUT / f"drive-video-manifest-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    taxonomy_path = taxonomy_report(records, OUT)
    out.write_text(json.dumps({"db_id":db_id,"folder_id":DRIVE_FOLDER_ID,"model":MODEL,"taxonomy_version":TAXONOMY_VERSION,"taxonomy_report":taxonomy_path,"created":created,"updated":updated,"failed":failed,"records":records}, indent=2, ensure_ascii=False))
    print(json.dumps({"status":"complete","db_id":db_id,"assets":len(assets),"created":created,"updated":updated,"failed":failed,"backup":str(out),"taxonomy_report":taxonomy_path}, indent=2))

if __name__ == "__main__": main()
