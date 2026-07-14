#!/usr/bin/env python3
"""Search official Pexels and Unsplash APIs for licensed lifestyle imagery.

No scraping/private endpoints. Requires PEXELS_API_KEY and/or UNSPLASH_ACCESS_KEY.
Outputs normalized JSON candidate records suitable for Fig & Bloom image QA.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

PEXELS_LICENSE = "https://www.pexels.com/license/"
UNSPLASH_LICENSE = "https://unsplash.com/license"


def load_env_files():
    """Load common Hermes env files without printing secrets.

    Existing process env wins. This keeps the script useful from cron/background
    contexts where shell-exported keys are not inherited.
    """
    for path in [
        os.path.expanduser("~/.hermes/.env"),
        "/opt/data/.env",
        "/opt/data/profiles/director/.env",
    ]:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


load_env_files()


def request_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code} for {url}: {body}") from e


def search_pexels(query, limit, orientation):
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return {"provider": "pexels", "missing_key": "PEXELS_API_KEY", "results": []}
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": min(limit, 80),
        "orientation": orientation,
    })
    data = request_json(
        f"https://api.pexels.com/v1/search?{params}",
        {"Authorization": key},
    )
    results = []
    for p in data.get("photos", [])[:limit]:
        src = p.get("src") or {}
        img = src.get("large2x") or src.get("large") or src.get("original")
        results.append({
            "provider": "pexels",
            "provider_id": str(p.get("id")),
            "photographer": p.get("photographer"),
            "source_url": p.get("url"),
            "image_url": img,
            "download_tracking_url": None,
            "licence_url": PEXELS_LICENSE,
            "width": p.get("width"),
            "height": p.get("height"),
            "orientation": "portrait" if (p.get("height") or 0) >= (p.get("width") or 0) else "landscape",
            "recommended_role": "candidate",
            "alt_text": p.get("alt") or f"Lifestyle image by {p.get('photographer') or 'Pexels photographer'}",
            "selection_notes": "Needs brand/product-truth review before use.",
            "raw": {"avg_color": p.get("avg_color")},
        })
    return {"provider": "pexels", "results": results}


def search_unsplash(query, limit, orientation):
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not key:
        return {"provider": "unsplash", "missing_key": "UNSPLASH_ACCESS_KEY", "results": []}
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": min(limit, 30),
        "orientation": orientation,
        "content_filter": "high",
    })
    data = request_json(
        f"https://api.unsplash.com/search/photos?{params}",
        {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"},
    )
    results = []
    for p in data.get("results", [])[:limit]:
        urls = p.get("urls") or {}
        links = p.get("links") or {}
        user = p.get("user") or {}
        results.append({
            "provider": "unsplash",
            "provider_id": p.get("id"),
            "photographer": user.get("name"),
            "source_url": links.get("html"),
            "image_url": urls.get("regular") or urls.get("full") or urls.get("raw"),
            "download_tracking_url": links.get("download_location"),
            "licence_url": UNSPLASH_LICENSE,
            "width": p.get("width"),
            "height": p.get("height"),
            "orientation": "portrait" if (p.get("height") or 0) >= (p.get("width") or 0) else "landscape",
            "recommended_role": "candidate",
            "alt_text": p.get("alt_description") or p.get("description") or f"Lifestyle image by {user.get('name') or 'Unsplash photographer'}",
            "selection_notes": "Needs brand/product-truth review before use. If selected, trigger download_tracking_url per Unsplash API guidelines.",
            "raw": {"color": p.get("color"), "blur_hash": p.get("blur_hash")},
        })
    return {"provider": "unsplash", "results": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--providers", default="pexels,unsplash", help="Comma-separated: pexels,unsplash")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "square"])
    ap.add_argument("--out")
    args = ap.parse_args()

    providers = [p.strip().lower() for p in args.providers.split(",") if p.strip()]
    payload = {
        "query": args.query,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "providers": [],
        "candidates": [],
    }
    for provider in providers:
        try:
            if provider == "pexels":
                res = search_pexels(args.query, args.limit, args.orientation)
            elif provider == "unsplash":
                res = search_unsplash(args.query, args.limit, args.orientation)
            else:
                res = {"provider": provider, "error": "unknown provider", "results": []}
        except Exception as e:
            # Provider failures are isolated: one blocked/down API must not
            # prevent returning candidates from the other official provider.
            res = {"provider": provider, "error": str(e)[:1000], "results": []}
        payload["providers"].append({k: v for k, v in res.items() if k != "results"})
        payload["candidates"].extend(res.get("results", []))

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)
    if not payload["candidates"]:
        missing = [p.get("missing_key") for p in payload["providers"] if p.get("missing_key")]
        if missing:
            print("Missing API keys: " + ", ".join(missing), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
