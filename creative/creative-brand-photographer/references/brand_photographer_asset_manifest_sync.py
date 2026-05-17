#!/usr/bin/env python3
"""Sync Brand Asset Manifest entries into Creative Brand Photographer seeds.

This is the bridge between:
- productivity/brand-asset-manifesting: canonical asset discovery + Notion manifest
- devops/devops-brand-cdn: public CDN URLs for model-readable previews/seeds
- creative/creative-brand-photographer: brand seed registry in file or Notion storage

Examples:
  # From the JSON backup produced by drive_video_manifest_to_notion.py
  python references/brand_photographer_asset_manifest_sync.py \
    --brand-id fig-and-bloom \
    --manifest-json /opt/data/brand-asset-manifests/notion-drive-assets/output/drive-video-manifest.json \
    --category bouquet \
    --dry-run

  # From the Notion asset manifest database
  BRAND_PHOTOGRAPHER_STORAGE=notion \
  BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID=<brand-photographer-ds> \
  NOTION_BRAND_ASSET_DATABASE_ID=<asset-manifest-db> \
  NOTION_API_KEY=<secret> \
  python references/brand_photographer_asset_manifest_sync.py --brand-id fig-and-bloom

Optional CDN publication:
  --upload-cdn --cdn-bucket figandbloom --cdn-key-prefix seeds/fig-and-bloom

When --upload-cdn is used, the script shells out to the brand CDN upload helper
and stores the returned public URL in seed.cdn_url. If the source record already
has a Preview URL from the asset manifesting pipeline, that URL is used without
re-uploading unless --force-cdn-upload is provided.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brand_photographer_api import (  # noqa: E402
    FileBrandStore,
    NotionBrandStore,
    _active_store,
    _brands_root,
    seed_from_asset_manifest_record,
)

NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")
NOTION_API_BASE = "https://api.notion.com/v1"


def notion_request(method: str, path: str, body: dict | None = None) -> dict:
    key = os.environ.get("NOTION_API_KEY")
    if not key:
        raise RuntimeError("NOTION_API_KEY is required to read the asset manifest database")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        NOTION_API_BASE + path,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + key,
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def rich_text(prop: dict) -> str:
    typ = prop.get("type")
    if typ in {"title", "rich_text"}:
        return "".join(x.get("plain_text", "") for x in prop.get(typ, []))
    if typ == "select":
        return (prop.get("select") or {}).get("name", "")
    if typ == "url":
        return prop.get("url") or ""
    if typ == "number":
        val = prop.get("number")
        return "" if val is None else str(val)
    return ""


def multi_select(prop: dict) -> list[str]:
    return [x.get("name", "") for x in prop.get("multi_select", []) if x.get("name")]


def query_asset_manifest_db(db_id: str, limit: int = 0) -> list[dict]:
    records: list[dict] = []
    cursor = None
    while True:
        body: dict[str, Any] = {"page_size": min(100, limit or 100)}
        if cursor:
            body["start_cursor"] = cursor
        data = notion_request("POST", f"/databases/{db_id}/query", body)
        for page in data.get("results", []):
            props = page.get("properties", {})
            file_id = rich_text(props.get("Drive File ID", {}))
            name = rich_text(props.get("Asset", {})) or file_id or page.get("id", "asset")
            record = {
                "page_id": page.get("id", ""),
                "database_id": db_id,
                "preview_url": rich_text(props.get("Preview URL", {})),
                "file": {
                    "id": file_id,
                    "name": name,
                    "mimeType": rich_text(props.get("Mime Type", {})),
                    "webViewLink": rich_text(props.get("Drive Link", {})),
                },
                "analysis": {
                    "content_type": rich_text(props.get("Content Type", {})),
                    "overall_description": rich_text(props.get("Overall Description", {})),
                    "visual_tags": multi_select(props.get("Visual Tags", {})),
                    "mood_tone": multi_select(props.get("Mood Tone", {})),
                    "products_or_flowers": multi_select(props.get("Products / Flowers", {})),
                    "usable_for": multi_select(props.get("Usable For", {})),
                    "setting_location": rich_text(props.get("Setting / Location", {})),
                },
                "meta": {"dimensions": rich_text(props.get("Dimensions", {}))},
            }
            records.append(record)
            if limit and len(records) >= limit:
                return records
        if not data.get("has_more"):
            return records
        cursor = data.get("next_cursor")


def load_manifest_json(path: Path, limit: int = 0) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        records = data["records"]
        for r in records:
            if isinstance(r, dict):
                r.setdefault("db_id", data.get("db_id"))
    elif isinstance(data, dict) and isinstance(data.get("files"), list):
        records = [{"file": f} for f in data["files"]]
    else:
        raise RuntimeError(f"Unsupported manifest JSON shape: {path}")
    return [r for r in records if isinstance(r, dict)][:limit or None]


def cdn_upload_helper_path() -> Path:
    configured = os.environ.get("BRAND_CDN_UPLOAD_HELPER")
    if configured:
        return Path(configured).expanduser()
    repo_root = HERE.parents[2]
    return repo_root / "devops" / "devops-brand-cdn" / "scripts" / "upload.py"


def upload_to_cdn(bucket: str, key: str, source: str) -> str:
    helper = cdn_upload_helper_path()
    if not helper.exists():
        raise RuntimeError(f"brand CDN upload helper not found: {helper}")
    proc = subprocess.run(
        [sys.executable, str(helper), bucket, key, source],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode:
        # Do not print env/token values; helper errors are token-safe by design.
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"CDN upload failed exit={proc.returncode}")
    url = proc.stdout.strip().splitlines()[-1]
    if not url.startswith("http"):
        raise RuntimeError(f"CDN upload did not return a URL: {url[:200]}")
    return url


def maybe_upload_seed_to_cdn(seed: dict, source: str, args: argparse.Namespace) -> dict:
    if not args.upload_cdn:
        return seed
    if seed.get("cdn_url") and not args.force_cdn_upload:
        return seed
    if not source:
        raise RuntimeError(f"No local/remote source available for CDN upload: {seed.get('id')}")
    suffix = Path(seed.get("file") or source).suffix or ".jpg"
    key = "/".join(x.strip("/") for x in [args.cdn_key_prefix, f"{seed['id']}{suffix}"] if x)
    seed = dict(seed)
    seed["cdn_url"] = upload_to_cdn(args.cdn_bucket, key, source)
    seed.setdefault("asset_manifest", {})["cdn_uploaded_key"] = key
    return seed


def source_for_record(record: dict, seed: dict, brand_dir: Path) -> str:
    for key in ("local_path", "source_path", "downloaded_path"):
        val = str(record.get(key) or "").strip()
        if val and Path(val).expanduser().exists():
            return val
    file_ref = str(seed.get("file") or "")
    if file_ref and (brand_dir / file_ref).exists():
        return str(brand_dir / file_ref)
    if seed.get("cdn_url"):
        return str(seed["cdn_url"])
    file_info = record.get("file") if isinstance(record.get("file"), dict) else {}
    return str(file_info.get("thumbnailLink") or file_info.get("webContentLink") or "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--manifest-json", type=Path)
    ap.add_argument("--asset-db-id", default=os.environ.get("NOTION_BRAND_ASSET_DATABASE_ID"))
    ap.add_argument("--category", default="asset")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--upload-cdn", action="store_true")
    ap.add_argument("--force-cdn-upload", action="store_true")
    ap.add_argument("--cdn-bucket", default=os.environ.get("BRAND_CDN_UPLOAD_BUCKET", ""))
    ap.add_argument("--cdn-key-prefix", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.upload_cdn and not args.cdn_bucket:
        raise RuntimeError("--cdn-bucket or BRAND_CDN_UPLOAD_BUCKET is required with --upload-cdn")

    if args.manifest_json:
        records = load_manifest_json(args.manifest_json, args.limit)
    elif args.asset_db_id:
        records = query_asset_manifest_db(args.asset_db_id, args.limit)
    else:
        raise RuntimeError("Provide --manifest-json or --asset-db-id/NOTION_BRAND_ASSET_DATABASE_ID")

    store = _active_store()
    brand_dir = _brands_root() / args.brand_id
    synced = []
    for record in records:
        seed = seed_from_asset_manifest_record(record, brand_id=args.brand_id, category=args.category)
        source = source_for_record(record, seed, brand_dir)
        seed = maybe_upload_seed_to_cdn(seed, source, args)
        if not args.dry_run:
            if not hasattr(store, "upsert_seed"):
                raise RuntimeError(f"Active store {store.__class__.__name__} does not support seed upsert")
            store.upsert_seed(args.brand_id, seed)  # type: ignore[attr-defined]
        raw_manifest = seed.get("asset_manifest")
        manifest = raw_manifest if isinstance(raw_manifest, dict) else {}
        drive_file_id = manifest.get("drive_file_id") if isinstance(manifest, dict) else None
        synced.append({"id": seed.get("id"), "cdn_url": seed.get("cdn_url"), "drive_file_id": drive_file_id})

    print(json.dumps({
        "status": "dry-run" if args.dry_run else "synced",
        "brand_id": args.brand_id,
        "store": store.__class__.__name__,
        "count": len(synced),
        "seeds": synced,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
