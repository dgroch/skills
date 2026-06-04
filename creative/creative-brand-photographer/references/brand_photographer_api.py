"""
Brand Photographer — Python API Wrapper

A brand-agnostic API for generating brand-consistent AI photography.
The agent (Brand Photographer) loads a single brand configuration at
instantiation time and all subsequent operations are scoped to that
brand. This enforces isolation: no cross-contamination of prompts,
rubrics, libraries, or critiques between brands.

Supports two image generation backends:
  - Higgsfield CLI (preferred) — `higgsfield generate create ... --wait`
  - OpenRouter (fallback/explicit override) — Nano Banana 2 / Pro via google/gemini models

Critic execution priority:
  1. Claude CLI (`claude` command) — preferred when available on PATH.
     Does not require ANTHROPIC_API_KEY to be set.
  2. Anthropic API — fallback when Claude CLI is not available.
     Requires ANTHROPIC_API_KEY.

Usage:
    from brand_photographer_api import BrandPhotographer

    # Load a configured brand (by brand_id)
    photographer = BrandPhotographer(
        brand_id="bower",
        openrouter_key="sk-or-v1-...",
        # anthropic_key only needed if claude CLI is unavailable
    )

    # Generate a single shot
    result = photographer.generate("product_hero")

    # Generate a full 9-post grid
    results = photographer.generate_grid()

    # Generate a campaign set
    results = photographer.generate_campaign(
        "mothers_day",
        flowers=["garden roses", "peonies"],
    )

    # Inspect the brand's prompt library
    library = photographer.get_library()

    # Storage backend:
    #   file (default) or Notion when BRAND_PHOTOGRAPHER_STORAGE=notion and
    #   BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID is set.

    # List all configured brands
    brands = BrandPhotographer.list_brands()
"""

import os
import json
import time
import base64
import fnmatch
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import requests
from pathlib import Path
from typing import Any, Callable, Optional

# ── Defaults ─────────────────────────────────────────────────────────────

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL_PRO = "google/gemini-3-pro-image-preview"
OPENROUTER_MODEL_NB2 = "google/gemini-3.1-flash-image-preview"

HIGGSFIELD_MODEL_DEFAULT = "nano_banana_2"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Fig & Bloom Asset Library — hosted semantic search over the Brand Asset
# Manifest (source: github.com/dgroch/my-media-library). One configurable base
# URL is used everywhere so the deployment can move without code changes; set
# BRAND_PHOTOGRAPHER_ASSET_LIBRARY_URL to point at whichever host is live.
# Whichever host is used MUST expose `GET /api/search` (see /openapi.json).
ASSET_LIBRARY_BASE_URL_DEFAULT = "https://asset-library-u70t.onrender.com"

MAX_ITERATIONS = 5
PASS_THRESHOLD = 7
POLL_INTERVAL = 5
POLL_TIMEOUT = 300

VALID_RATIOS = {"9:16", "16:9", "4:3", "3:4", "1:1", "2:3", "3:2"}
RATIO_MAP = {"4:5": "3:4", "5:4": "4:3"}

# Critic execution modes — logged at runtime
CRITIC_MODE_CLI = "cli"
CRITIC_MODE_API = "api"
FIDELITY_MODE_GUIDED = "guided"
FIDELITY_MODE_STRICT = "strict"


def _load_env(path: str = "/opt/data/.env") -> None:
    """Load simple KEY=VALUE lines without overriding process env."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _storage_mode() -> str:
    configured = os.environ.get("BRAND_PHOTOGRAPHER_STORAGE", "").strip().lower()
    if configured:
        return configured
    if _notion_data_source_id():
        return "notion"
    return "file"


def _notion_data_source_id() -> str:
    return (
        os.environ.get("BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID")
        or os.environ.get("BRAND_PHOTOGRAPHER_NOTION_DS")
        or os.environ.get("BP_NOTION_DATA_SOURCE_ID")
        or ""
    ).strip()


class BrandStore:
    """Storage boundary for brand artifacts."""

    def list_brands(self) -> list[str]:
        raise NotImplementedError

    def load_brand_config(self, brand_id: str) -> dict:
        raise NotImplementedError

    def artifact_exists(self, brand_id: str, artifact: str) -> bool:
        raise NotImplementedError

    def load_text_artifact(self, brand_id: str, artifact: str) -> str:
        raise NotImplementedError

    def load_library(self, brand_id: str) -> list[dict]:
        raise NotImplementedError

    def append_library_entry(self, brand_id: str, entry: dict) -> None:
        raise NotImplementedError

    def load_seeds(self, brand_id: str) -> list[dict]:
        raise NotImplementedError


    def upsert_seed(self, brand_id: str, seed: dict) -> None:
        raise NotImplementedError

class FileBrandStore(BrandStore):
    def __init__(self, root: Path):
        self.root = root

    def brand_dir(self, brand_id: str) -> Path:
        return self.root / brand_id

    def list_brands(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(
            d.name for d in self.root.iterdir()
            if d.is_dir() and (d / "brand.json").exists()
        )

    def load_brand_config(self, brand_id: str) -> dict:
        path = self.brand_dir(brand_id) / "brand.json"
        if not path.exists():
            raise BrandNotConfiguredError(f"No brand configured at {path}")
        return json.loads(path.read_text())

    def artifact_path(self, brand_id: str, artifact: str, config: Optional[dict] = None) -> Path:
        if artifact == "brand_config":
            return self.brand_dir(brand_id) / "brand.json"
        cfg = config or self.load_brand_config(brand_id)
        references = cfg.get("references", {})
        ref_map = {
            "art_direction": "art_direction",
            "colour_system": "colour_system",
            "grid_spec": "grid_spec",
            "prompt_library": "prompt_library",
            "seeds_manifest": "seeds_manifest",
        }
        filename = references.get(ref_map.get(artifact, artifact), artifact)
        return self.brand_dir(brand_id) / filename

    def artifact_exists(self, brand_id: str, artifact: str) -> bool:
        return self.artifact_path(brand_id, artifact).exists()

    def load_text_artifact(self, brand_id: str, artifact: str) -> str:
        path = self.artifact_path(brand_id, artifact)
        return path.read_text() if path.exists() else ""

    def load_library(self, brand_id: str) -> list[dict]:
        path = self.artifact_path(brand_id, "prompt_library")
        if path.exists():
            return json.loads(path.read_text())
        return []

    def append_library_entry(self, brand_id: str, entry: dict) -> None:
        path = self.artifact_path(brand_id, "prompt_library")
        path.parent.mkdir(parents=True, exist_ok=True)
        library = self.load_library(brand_id)
        library.append(entry)
        path.write_text(json.dumps(library, indent=2))

    def load_seeds(self, brand_id: str) -> list[dict]:
        path = self.artifact_path(brand_id, "seeds_manifest")
        if not path.exists():
            return []
        manifest = json.loads(path.read_text())
        raw = manifest.get("seeds", [])
        return raw if isinstance(raw, list) else []

    def upsert_seed(self, brand_id: str, seed: dict) -> None:
        path = self.artifact_path(brand_id, "seeds_manifest")
        manifest = {"version": "1.0", "seeds": []}
        if path.exists():
            try:
                loaded = json.loads(path.read_text())
                if isinstance(loaded, dict):
                    manifest.update(loaded)
            except json.JSONDecodeError:
                pass
        seeds = manifest.get("seeds", [])
        if not isinstance(seeds, list):
            seeds = []
        sid = str(seed.get("id") or "").strip()
        if not sid:
            raise ValueError("seed id is required")
        replaced = False
        updated = []
        for item in seeds:
            if isinstance(item, dict) and item.get("id") == sid:
                updated.append(seed)
                replaced = True
            else:
                updated.append(item)
        if not replaced:
            updated.append(seed)
        manifest["seeds"] = updated
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def _clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            out.append(text)
    return out


def _slugify_seed(text: str, max_len: int = 64) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")
    return (slug or "asset")[:max_len].strip("-") or "asset"


def seed_image_ref(seed: dict, brand_dir: Path) -> str:
    """Return the best image reference for a seed: local file first, then CDN/manifest URLs."""
    file_ref = str(seed.get("file") or seed.get("local_file") or "").strip()
    if file_ref:
        local = Path(file_ref)
        if not local.is_absolute():
            local = brand_dir / file_ref
        if local.exists():
            return str(local)
    for key in ("cdn_url", "public_url", "preview_url", "source_url"):
        url = str(seed.get(key) or "").strip()
        if url.startswith(("http://", "https://", "data:image")):
            return url
    manifest = seed.get("asset_manifest") if isinstance(seed.get("asset_manifest"), dict) else {}
    for key in ("cdn_url", "preview_url", "drive_link"):
        url = str(manifest.get(key) or "").strip()
        if url.startswith(("http://", "https://")):
            return url
    return str((brand_dir / file_ref) if file_ref else "")


def seed_from_asset_manifest_record(record: dict, brand_id: str, category: str = "asset") -> dict:
    """Convert a brand-asset-manifesting backup/record into a Brand Photographer seed."""
    file_info = record.get("file") if isinstance(record.get("file"), dict) else record
    analysis = record.get("analysis") if isinstance(record.get("analysis"), dict) else {}
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    drive_id = str(file_info.get("id") or record.get("drive_file_id") or record.get("Drive File ID") or "").strip()
    name = str(file_info.get("name") or record.get("name") or record.get("Asset") or drive_id or "asset").strip()
    seed_id = f"asset-{drive_id}" if drive_id else f"asset-{_slugify_seed(name)}"
    cdn_url = str(record.get("preview_url") or record.get("cdn_url") or record.get("Preview URL") or "").strip()
    drive_link = str(file_info.get("webViewLink") or record.get("drive_link") or record.get("Drive Link") or "").strip()
    tags = _clean_list(analysis.get("visual_tags")) + _clean_list(analysis.get("mood_tone"))
    usable_for = _clean_list(analysis.get("usable_for"))
    flowers = _clean_list(analysis.get("products_or_flowers"))
    description = str(analysis.get("overall_description") or record.get("description") or "").strip()
    seed = {
        "id": seed_id,
        "category": category or str(analysis.get("content_type") or "asset"),
        "file": f"seeds/asset-manifest/{seed_id}{Path(name).suffix or '.jpg'}",
        "cdn_url": cdn_url,
        "tags": tags,
        "flowers": flowers,
        "usable_for": usable_for,
        "description": description,
        "source": "brand_asset_manifest",
        "asset_manifest": {
            "brand_id": brand_id,
            "drive_file_id": drive_id,
            "drive_link": drive_link,
            "preview_url": cdn_url,
            "page_id": str(record.get("page_id") or record.get("notion_page_id") or ""),
            "database_id": str(record.get("database_id") or record.get("db_id") or ""),
            "mime_type": str(file_info.get("mimeType") or record.get("mime_type") or ""),
            "dimensions": f"{meta.get('width','')}x{meta.get('height','')}" if meta else str(record.get("Dimensions") or ""),
        },
    }
    # Drop empty scalar/list fields while preserving nested manifest handles.
    return {k: v for k, v in seed.items() if v not in ("", [], None)}


def seed_from_search_result(asset: dict, brand_id: str = "", category: str = "asset") -> dict:
    """Convert an Asset Library `/api/search` result into an ephemeral seed dict.

    Search results carry `{id, title, url, description, mediaType, driveLink}`.
    The returned seed is generation-ready (`cdn_url` resolves to the Brand CDN
    preview) but is NOT a registered seed — promote it via
    `brand_photographer_asset_manifest_sync.py` to persist it as a seed row.
    """
    page_id = str(asset.get("id") or "").strip()
    title = str(asset.get("title") or page_id or "asset").strip()
    cdn_url = str(asset.get("url") or "").strip()
    seed_id = f"search-{page_id}" if page_id else f"search-{_slugify_seed(title)}"
    manifest = {k: v for k, v in {
        "brand_id": brand_id,
        "page_id": page_id,
        "preview_url": cdn_url,
        "drive_link": str(asset.get("driveLink") or "").strip(),
    }.items() if v}
    seed = {
        "id": seed_id,
        "category": category or "asset",
        "cdn_url": cdn_url,
        "description": str(asset.get("description") or "").strip(),
        "source": "asset_library_search",
        "asset_manifest": manifest,
    }
    return {k: v for k, v in seed.items() if v not in ("", [], None, {})}


def _asset_library_base_url(base_url: Optional[str] = None) -> str:
    """Resolve the Asset Library base URL (arg > env > default), no trailing slash."""
    resolved = (
        base_url
        or os.environ.get("BRAND_PHOTOGRAPHER_ASSET_LIBRARY_URL")
        or ASSET_LIBRARY_BASE_URL_DEFAULT
    ).strip()
    return resolved.rstrip("/")


def search_asset_library(
    query: str,
    cursor: str = "0",
    base_url: Optional[str] = None,
    timeout: int = 60,
) -> dict:
    """Semantic search over the Fig & Bloom Brand Asset Manifest.

    Calls `GET {base}/api/search?q=<query>&cursor=<cursor>` on the hosted Asset
    Library (github.com/dgroch/my-media-library) and returns the parsed JSON:
    `{"results": Asset[], "nextCursor": str | None}`. Each Asset carries
    `id` (Notion Manifest page ID), `title`, `url` (Brand CDN preview),
    `description`, `mediaType`, and `driveLink`.

    On any transport/parse error this returns an empty result set with an
    `error` key rather than raising, so callers can degrade gracefully.
    """
    _load_env()
    base = _asset_library_base_url(base_url)
    params = urllib.parse.urlencode({"q": query, "cursor": str(cursor)})
    url = f"{base}/api/search?{params}"
    try:
        res = requests.get(url, timeout=timeout)
        res.raise_for_status()
        data = res.json()
    except Exception as exc:
        return {"results": [], "nextCursor": None, "base_url": base, "error": str(exc)}
    results = data.get("results", []) if isinstance(data, dict) else []
    return {
        "results": results if isinstance(results, list) else [],
        "nextCursor": data.get("nextCursor") if isinstance(data, dict) else None,
        "base_url": base,
    }


class NotionBrandStore(BrandStore):
    """Notion-backed brand artifact store.

    Uses a single Notion data source with these properties:
    - Name (title)
    - Brand ID (rich_text)
    - Artifact (select): brand_config, art_direction, colour_system, grid_spec, prompt, seed
    - Record ID (rich_text): stable row key, e.g. config, product_hero, bouquet-001
    - JSON (rich_text): compact JSON for structured records
    - Content (rich_text): markdown/plain text for long-form brand reference docs
    - Category (select), File (rich_text), Score (number) are optional convenience fields
    """

    def __init__(
        self,
        data_source_id: str,
        api_key: Optional[str] = None,
        request_fn: Optional[Callable[[str, str, Optional[dict]], dict]] = None,
    ):
        self.data_source_id = data_source_id
        self.api_key = api_key or os.environ.get("NOTION_API_KEY", "")
        if not self.data_source_id:
            raise ValueError("BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID is required for Notion storage")
        if not self.api_key and request_fn is None:
            raise ValueError("NOTION_API_KEY is required for Notion storage")
        self._request_fn = request_fn

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        if self._request_fn:
            return self._request_fn(method, path, payload)
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            f"{NOTION_API_BASE}{path}",
            data=data,
            headers=self._headers(),
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = resp.read().decode()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            raise RuntimeError(f"Notion {method} {path} failed HTTP {exc.code}: {body[:1200]}") from exc

    def _query(self, payload: dict) -> list[dict]:
        results: list[dict] = []
        cursor = None
        while True:
            body = dict(payload)
            if cursor:
                body["start_cursor"] = cursor
            data = self._request("POST", f"/data_sources/{self.data_source_id}/query", body)
            results.extend(data.get("results", []))
            if not data.get("has_more"):
                return results
            cursor = data.get("next_cursor")

    @staticmethod
    def _text_prop(page: dict, name: str) -> str:
        prop = page.get("properties", {}).get(name, {})
        typ = prop.get("type")
        if typ == "title":
            return "".join(x.get("plain_text", "") for x in prop.get("title", []))
        if typ == "rich_text":
            return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))
        if typ == "select":
            return (prop.get("select") or {}).get("name", "")
        if typ == "number":
            val = prop.get("number")
            return "" if val is None else str(val)
        return ""

    @staticmethod
    def _rt(value: str) -> dict:
        # Notion rich_text property chunks max at 2000 chars. Keep this as an
        # index/preview only; complete JSON/content is stored in page children.
        return {"rich_text": [{"type": "text", "text": {"content": value[:1900]}}]} if value else {"rich_text": []}

    @staticmethod
    def _title(value: str) -> dict:
        return {"title": [{"type": "text", "text": {"content": value[:2000]}}]}

    @staticmethod
    def _select(value: str) -> dict:
        return {"select": {"name": value}} if value else {"select": None}

    @staticmethod
    def _number(value: Any) -> dict:
        return {"number": value if isinstance(value, (int, float)) else None}

    def _filter(self, brand_id: str, artifact: Optional[str] = None, record_id: Optional[str] = None) -> dict:
        clauses = [{"property": "Brand ID", "rich_text": {"equals": brand_id}}]
        if artifact:
            clauses.append({"property": "Artifact", "select": {"equals": artifact}})
        if record_id:
            clauses.append({"property": "Record ID", "rich_text": {"equals": record_id}})
        return {"filter": {"and": clauses}}

    def _pages(self, brand_id: str, artifact: Optional[str] = None, record_id: Optional[str] = None) -> list[dict]:
        return self._query(self._filter(brand_id, artifact, record_id))

    def _read_blocks_text(self, page_id: str) -> str:
        chunks: list[str] = []
        cursor = None
        while True:
            suffix = f"?start_cursor={urllib.parse.quote(cursor)}" if cursor else ""
            data = self._request("GET", f"/blocks/{page_id}/children{suffix}", None)
            for block in data.get("results", []):
                typ = block.get("type")
                rich = block.get(typ, {}).get("rich_text", []) if typ else []
                chunks.append("".join(x.get("plain_text", "") for x in rich))
            if not data.get("has_more"):
                return "".join(chunks)
            cursor = data.get("next_cursor")

    def _json_from_page(self, page: dict) -> dict:
        # Prefer the JSON property when it contains parseable JSON. This lets
        # upserts refresh compact records without attempting to rewrite Notion
        # child blocks. Fall back to page children for long initial-import rows
        # whose JSON property was only an index/preview.
        prop_raw = self._text_prop(page, "JSON")
        if prop_raw:
            try:
                return json.loads(prop_raw)
            except json.JSONDecodeError:
                pass
        raw = ""
        page_id = page.get("id")
        if page_id:
            try:
                raw = self._read_blocks_text(page_id)
            except Exception:
                raw = ""
        if not raw:
            return {}
        return json.loads(raw)

    @staticmethod
    def _children_for(payload: str, language: str = "plain text") -> list[dict]:
        if not payload:
            return []
        children = []
        for i in range(0, len(payload), 1900):
            chunk = payload[i:i + 1900]
            if language == "json":
                children.append({
                    "object": "block",
                    "type": "code",
                    "code": {"language": "json", "rich_text": [{"type": "text", "text": {"content": chunk}}]},
                })
            else:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]},
                })
        return children

    def _create_page(self, brand_id: str, artifact: str, record_id: str, name: str, json_obj: Optional[dict] = None, content: str = "", extra: Optional[dict] = None) -> dict:
        json_payload = json.dumps(json_obj or {}, separators=(",", ":")) if json_obj is not None else ""
        props = {
            "Name": self._title(name),
            "Brand ID": self._rt(brand_id),
            "Artifact": self._select(artifact),
            "Record ID": self._rt(record_id),
            "JSON": self._rt(json_payload),
            "Content": self._rt(content),
        }
        if extra:
            props.update(extra)
        children = self._children_for(json_payload, "json") if json_payload else self._children_for(content)
        payload = {"parent": {"data_source_id": self.data_source_id}, "properties": props}
        if children:
            payload["children"] = children
        return self._request("POST", "/pages", payload)

    def list_brands(self) -> list[str]:
        pages = self._query({"filter": {"property": "Artifact", "select": {"equals": "brand_config"}}})
        return sorted({self._text_prop(p, "Brand ID") for p in pages if self._text_prop(p, "Brand ID")})

    def load_brand_config(self, brand_id: str) -> dict:
        pages = self._pages(brand_id, "brand_config", "config")
        if not pages:
            raise BrandNotConfiguredError(f"No Notion brand_config row for brand_id={brand_id}")
        return self._json_from_page(pages[0])

    def artifact_exists(self, brand_id: str, artifact: str) -> bool:
        if artifact in ("prompt_library", "seeds_manifest"):
            # Empty prompt libraries and seed manifests are valid; their rows are
            # optional because prompt/seed entries are represented individually.
            return bool(self._pages(brand_id, "brand_config", "config"))
        return bool(self._pages(brand_id, artifact, artifact))

    def load_text_artifact(self, brand_id: str, artifact: str) -> str:
        pages = self._pages(brand_id, artifact, artifact)
        if not pages:
            return ""
        page_id = pages[0].get("id")
        if page_id:
            try:
                text = self._read_blocks_text(page_id)
                if text:
                    return text
            except Exception:
                pass
        return self._text_prop(pages[0], "Content")

    def load_library(self, brand_id: str) -> list[dict]:
        entries = []
        for page in self._pages(brand_id, "prompt"):
            record = self._json_from_page(page)
            if record:
                entries.append(record)
        return entries

    def append_library_entry(self, brand_id: str, entry: dict) -> None:
        shot_id = str(entry.get("shot_id") or "prompt")
        score = entry.get("score")
        self._create_page(
            brand_id,
            "prompt",
            f"{shot_id}:{int(time.time())}",
            f"{brand_id} / {shot_id}",
            json_obj=entry,
            extra={
                "Score": self._number(score),
            },
        )

    def load_seeds(self, brand_id: str) -> list[dict]:
        seeds = []
        for page in self._pages(brand_id, "seed"):
            record = self._json_from_page(page)
            if record:
                seeds.append(record)
        return seeds

    def upsert_seed(self, brand_id: str, seed: dict) -> None:
        sid = str(seed.get("id") or "").strip()
        if not sid:
            raise ValueError("seed id is required")
        manifest = seed.get("asset_manifest") if isinstance(seed.get("asset_manifest"), dict) else {}
        json_payload = json.dumps(seed, separators=(",", ":"), ensure_ascii=False)
        extra = {
            "JSON": self._rt(json_payload),
            "Category": self._select(str(seed.get("category") or "")),
            "File": self._rt(str(seed.get("file") or seed.get("local_file") or "")),
            "Local File": self._rt(str(seed.get("file") or seed.get("local_file") or "")),
            "CDN URL": self._rt(str(seed.get("cdn_url") or seed.get("public_url") or manifest.get("cdn_url") or manifest.get("preview_url") or "")),
            "Preview URL": self._rt(str(seed.get("preview_url") or manifest.get("preview_url") or seed.get("cdn_url") or "")),
            "Drive File ID": self._rt(str(manifest.get("drive_file_id") or seed.get("drive_file_id") or "")),
            "Asset Manifest Page ID": self._rt(str(manifest.get("page_id") or seed.get("asset_manifest_page_id") or "")),
            "Asset Manifest DB ID": self._rt(str(manifest.get("database_id") or seed.get("asset_manifest_database_id") or "")),
        }
        pages = self._pages(brand_id, "seed", sid)
        if pages:
            # Update indexed properties plus the compact JSON property. Notion
            # blocks are append-only via the public API, so load prefers the
            # refreshed JSON property for upserted compact seed rows.
            self._request("PATCH", f"/pages/{pages[0]['id']}", {"properties": extra})
            return
        self._create_page(
            brand_id,
            "seed",
            sid,
            f"{brand_id} / {sid}",
            json_obj=seed,
            extra=extra,
        )


def _active_store() -> BrandStore:
    _load_env()
    root = _brands_root()
    if _storage_mode() == "notion":
        return NotionBrandStore(_notion_data_source_id())
    return FileBrandStore(root)


def _brands_root() -> Path:
    """Root directory holding per-brand configuration.

    Returns a persistent path outside the ephemeral __runtime__ directory so
    that seeds.json, seed images, prompt-library, and outputs survive across
    heartbeat sessions.

    Path structure inside __runtime__:
        .../skills/{companyId}/__runtime__/{skill}/references/brand_photographer_api.py

    Persistent store lives two levels above __runtime__:
        .../skills/{companyId}/data/creative-brand-photographer/brands/

    On first access, any brand directory present in the bundled brands/ tree
    is bootstrapped into the persistent store (copy-once, never overwrite).
    """
    skill_root = Path(__file__).resolve().parent.parent  # __runtime__/{skill}/
    skills_base = skill_root.parent.parent               # .../skills/{companyId}/
    persistent = skills_base / "data" / "creative-brand-photographer" / "brands"
    persistent.mkdir(parents=True, exist_ok=True)

    # Bootstrap: copy any brand dirs that exist in the bundled source but
    # have not yet been initialised in the persistent store.  Never overwrites.
    bundled = skill_root / "brands"
    if bundled.exists():
        for brand_dir in bundled.iterdir():
            if brand_dir.is_dir() and not (persistent / brand_dir.name).exists():
                shutil.copytree(str(brand_dir), str(persistent / brand_dir.name))

    return persistent


def _claude_cli_available() -> bool:
    """Return True if the `claude` CLI is present on PATH."""
    return shutil.which("claude") is not None


def _higgsfield_cli_path() -> Optional[str]:
    """Return the installed Higgsfield CLI path, preferring PATH."""
    found = shutil.which("higgsfield")
    if found:
        return found
    bundled = Path("/paperclip/.local/bin/higgsfield")
    if bundled.exists() and os.access(bundled, os.X_OK):
        return str(bundled)
    return None


def _higgsfield_cli_available() -> bool:
    """Return True if the `higgsfield` CLI is installed for this runtime."""
    return _higgsfield_cli_path() is not None


def _higgsfield_account_status() -> tuple[bool, str]:
    """Return whether the Higgsfield CLI is authenticated, plus safe status text."""
    cli = _higgsfield_cli_path()
    if not cli:
        return False, "`higgsfield` CLI is not installed or is not on PATH or /paperclip/.local/bin"
    try:
        result = subprocess.run(
            [cli, "account", "status"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return False, "`higgsfield account status` timed out"
    except Exception as exc:
        return False, f"`higgsfield account status` failed: {exc}"
    output = (result.stdout or result.stderr or "").strip()
    if result.returncode != 0:
        msg = output[:500] or f"exit code {result.returncode}"
        return False, f"`higgsfield account status` failed: {msg}"
    return True, output[:500]


class BrandNotConfiguredError(Exception):
    """Raised when the requested brand_id has no configuration."""


class BrandPhotographer:
    """Multi-brand photographer API.

    Each instance is bound to exactly one brand_id. All library writes,
    critiques, and prompt revisions use that brand's assets only.

    Critic execution: Claude CLI is used when available (preferred). Falls back
    to direct Anthropic API calls when CLI is unavailable. ANTHROPIC_API_KEY is
    only required for the API fallback path.

    Args:
        brand_id: Identifier of the brand directory under brands/.
        backend: "higgsfield" (preferred) or "openrouter".
        openrouter_key: OpenRouter API key.
        model: Override the brand's configured image model.
        anthropic_key: Anthropic API key for API-mode critic fallback.
            Optional when `claude` CLI is available on PATH.
        max_iterations: Override brand's quality-gate iteration cap.
        pass_threshold: Override brand's pass threshold (1-10).
        verbose: Print progress messages.
    """

    def __init__(
        self,
        brand_id: str,
        backend: Optional[str] = None,
        openrouter_key: str = "",
        model: str = "",
        hf_key: str = "",
        hf_secret: str = "",
        anthropic_key: str = "",
        max_iterations: Optional[int] = None,
        pass_threshold: Optional[int] = None,
        verbose: bool = True,
    ):
        self.brand_id = brand_id
        self.verbose = verbose

        # ── Load brand configuration ─────────────────────────────────
        self.store = _active_store()
        self.brand_dir = _brands_root() / brand_id  # still used for seed image files + outputs
        try:
            self.config = self.store.load_brand_config(brand_id)
        except BrandNotConfiguredError as exc:
            raise BrandNotConfiguredError(
                f"{exc}. Available brands: {self.list_brands()}. "
                "Complete the onboarding flow to add a new brand."
            ) from exc
        self._validate_config()

        # Brand-scoped paths — NEVER reach across brands. In Notion mode,
        # structured artifacts are read/written through self.store; seed image
        # files and generated outputs remain local for model compatibility.
        self.output_dir = self.brand_dir / "outputs"
        self.library_path = self.brand_dir / self.config["references"].get("prompt_library", "prompt-library.json")
        self.seeds_manifest_path = self.brand_dir / self.config["references"].get("seeds_manifest", "seeds.json")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.seeds = self._load_seeds_manifest()

        # Asset Library programmatic search — used as a seed-discovery fallback
        # when no registered seed satisfies a brief (the "search the hosted API"
        # branch of the mode-selection logic). Resolution order:
        # env BRAND_PHOTOGRAPHER_ASSET_SEARCH > brand config asset_search.enabled
        # > default on for Fig & Bloom, off otherwise.
        asset_cfg = self.config.get("asset_search", {})
        asset_cfg = asset_cfg if isinstance(asset_cfg, dict) else {}
        env_flag = os.environ.get("BRAND_PHOTOGRAPHER_ASSET_SEARCH", "").strip().lower()
        if env_flag in ("1", "true", "yes", "on"):
            self.asset_search_enabled = True
        elif env_flag in ("0", "false", "no", "off"):
            self.asset_search_enabled = False
        elif "enabled" in asset_cfg:
            self.asset_search_enabled = bool(asset_cfg.get("enabled"))
        else:
            self.asset_search_enabled = (brand_id == "fig-and-bloom")

        # Backend resolution (constructor arg > env > Higgsfield CLI when
        # available > brand config > OpenRouter fallback). Older brand configs
        # may still say "openrouter"; CLI availability intentionally promotes
        # the new preferred path unless a caller explicitly overrides it.
        brand_backend = self.config.get("image_backend", {})
        env_backend = os.environ.get("BRAND_PHOTOGRAPHER_IMAGE_BACKEND", "").strip()
        configured_backend = str(brand_backend.get("default") or "openrouter").strip()
        if backend:
            self.backend = backend
        elif env_backend:
            self.backend = env_backend
        elif _higgsfield_cli_available():
            self.backend = "higgsfield"
        else:
            self.backend = configured_backend
        if self.backend in ("higgsfield_cli", "higgsfield-cli"):
            self.backend = "higgsfield"
        self.model = model or (
            brand_backend.get("higgsfield_model")
            if self.backend == "higgsfield"
            else brand_backend.get("model")
        ) or (HIGGSFIELD_MODEL_DEFAULT if self.backend == "higgsfield" else OPENROUTER_MODEL_NB2)

        # Quality gate
        gate = self.config.get("quality_gate", {})
        self.max_iterations = max_iterations if max_iterations is not None else gate.get("max_iterations", MAX_ITERATIONS)
        self.pass_threshold = pass_threshold if pass_threshold is not None else gate.get("pass_threshold", PASS_THRESHOLD)

        # Critic setup
        critic = self.config.get("critic", {})
        self.critic_model = critic.get("model", DEFAULT_CLAUDE_MODEL)
        self.critic_system = self._build_critic_system()

        # ── Critic execution mode ──────────────────────────────────────
        # Prefer Claude CLI; fall back to API only when CLI is absent.
        self._cli_available = _claude_cli_available()
        if self._cli_available:
            self.critic_mode = CRITIC_MODE_CLI
            self._log("[critic] Claude CLI found on PATH — using CLI mode")
            # API key not required but accepted if provided (used only if CLI fails)
            self.anthropic_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
        else:
            self.critic_mode = CRITIC_MODE_API
            self._log("[critic] Claude CLI not found — falling back to API mode")
            self.anthropic_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
            if not self.anthropic_key:
                raise ValueError(
                    "Anthropic API key required when Claude CLI is unavailable. "
                    "Either install the Claude CLI or set ANTHROPIC_API_KEY."
                )

        self.anthropic_headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
        } if self.anthropic_key else {}

        # Backend-specific credentials
        if self.backend == "openrouter":
            self.openrouter_key = openrouter_key or os.environ.get("OPENROUTER_API_KEY", "")
            if not self.openrouter_key:
                raise ValueError("OpenRouter API key required: set OPENROUTER_API_KEY or pass openrouter_key")
            self.openrouter_headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
            }
        elif self.backend == "higgsfield":
            ok, status = _higgsfield_account_status()
            if not ok:
                raise ValueError(
                    "Higgsfield CLI is the preferred Brand Photographer generation path, "
                    f"but it is not ready: {status}. Install the CLI or ask the owner to run "
                    "`higgsfield auth login` (or `hf auth login` when the CLI prints that hint); "
                    "use backend='openrouter' only as an explicit fallback."
                )
            self._log("[generation] Higgsfield CLI authenticated — using CLI generation path")
        else:
            raise ValueError(f"Unknown backend: {self.backend}. Use 'openrouter' or 'higgsfield'.")

        self._log(f"Brand Photographer configured for '{self.config['brand_name']}' (brand_id={brand_id})")

    # ── Brand discovery ──────────────────────────────────────────────────

    @classmethod
    def list_brands(cls) -> list[str]:
        """Return all configured brand_ids from the active storage backend."""
        return _active_store().list_brands()

    @classmethod
    def load_brand_config(cls, brand_id: str) -> dict:
        """Return the raw brand configuration dict for a brand_id."""
        return _active_store().load_brand_config(brand_id)

    def _load_seeds_manifest(self) -> list[dict]:
        """Load and normalize seeds from the active storage backend."""
        try:
            raw_seeds = self.store.load_seeds(self.brand_id)
        except Exception as exc:
            self._log(f"[seed] Could not load seeds from {self.store.__class__.__name__}: {exc}")
            return []
        if not isinstance(raw_seeds, list):
            return []

        normalized = []
        for seed in raw_seeds:
            if not isinstance(seed, dict):
                continue
            sid = seed.get("id")
            image_ref = seed_image_ref(seed, self.brand_dir)
            if not sid or not image_ref:
                continue
            normalized.append(seed)
        return normalized

    # ── Validation & critic construction ─────────────────────────────────

    def _validate_config(self):
        required_top = ["brand_id", "brand_name", "references", "critic", "grid_pattern"]
        for key in required_top:
            if key not in self.config:
                raise ValueError(f"Brand config missing required key: {key}")
        if self.config["brand_id"] != self.brand_id:
            raise ValueError(
                f"brand_id mismatch: directory '{self.brand_id}' vs config '{self.config['brand_id']}'"
            )
        # Required reference artifacts must exist in the active store.
        required_refs = ("art_direction", "colour_system", "grid_spec", "prompt_library", "seeds_manifest")
        for label in required_refs:
            if label in self.config.get("references", {}) and not self.store.artifact_exists(self.brand_id, label):
                raise FileNotFoundError(
                    f"Brand '{self.brand_id}' references missing artifact: {label} in {self.store.__class__.__name__}"
                )

    def _build_critic_system(self) -> str:
        """Build the critic system prompt from brand config + reference docs."""
        brand_name = self.config["brand_name"]
        description = self.config.get("description", "")
        dims = self.config["critic"]["dimensions"]

        rubric_lines = []
        dimension_names = []
        for d in dims:
            name = d["name"].upper()
            dimension_names.append(d["name"])
            rubric_lines.append(f"- {name}: {d['description']}")
        rubric = "\n".join(rubric_lines)

        dims_schema = ",\n    ".join(
            f'"{n}": {{"score": <1-10>, "note": "<15 words max>"}}'
            for n in dimension_names
        )

        return f"""You are a brand photography critic for "{brand_name}" — {description} Evaluate AI-generated images against {brand_name}'s art direction rubric and suggest specific prompt improvements.

{brand_name.upper()} ART DIRECTION RUBRIC:
{rubric}

Respond ONLY with valid JSON (no markdown, no backticks, no preamble):
{{
  "overall_score": <1-10>,
  "dimensions": {{
    {dims_schema}
  }},
  "verdict": "PASS or ITERATE",
  "prompt_revisions": "<If ITERATE: exact words to add/remove/change in the prompt. If PASS: empty string>"
}}"""

    # ── Public API ───────────────────────────────────────────────────────

    def generate(
        self,
        shot_id: str,
        prompt: str = "",
        ratio: str = "3:4",
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
        seed_constraints: Optional[dict] = None,
    ) -> dict:
        """Generate a single image through the quality gate loop."""
        if fidelity_mode not in (FIDELITY_MODE_GUIDED, FIDELITY_MODE_STRICT):
            raise ValueError("fidelity_mode must be 'guided' or 'strict'")

        library_entry = self._lookup_library_entry(shot_id)
        if not prompt:
            prompt = library_entry.get("prompt", "")
            if not prompt:
                raise ValueError(
                    f"No prompt for shot_id '{shot_id}' in {self.brand_id}'s library. "
                    "Provide a prompt or add one via the onboarding/expansion flow."
                )
        if seed_constraints is None and isinstance(library_entry.get("seed_constraints"), dict):
            seed_constraints = library_entry["seed_constraints"]
        if fidelity_mode == FIDELITY_MODE_GUIDED and isinstance(library_entry.get("fidelity_mode"), str):
            fidelity_mode = library_entry["fidelity_mode"]

        return self._run_quality_gate(
            shot_id,
            prompt,
            ratio,
            fidelity_mode=fidelity_mode,
            seed_constraints=seed_constraints,
        )

    def generate_grid(
        self,
        product: str = "",
        season: str = "",
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
        seed_constraints: Optional[dict] = None,
    ) -> list[dict]:
        """Generate a full grid following the brand's grid_pattern."""
        grid_pattern = self.config["grid_pattern"]
        slot_to_shot = self.config.get("slot_to_shot", {})

        results = []
        for slot in grid_pattern:
            shot_id = slot_to_shot.get(slot["slot"], slot["slot"])
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                self._log(f"  Skipping {slot['slot']} — no prompt for {shot_id}")
                continue

            if product:
                prompt = self._apply_product_swap(prompt, product)
            if season:
                prompt = self._apply_season_modifier(prompt, season)

            self._log(f"\n  Grid slot: {slot['slot']} ({slot['type']})")
            result = self._run_quality_gate(
                shot_id,
                prompt,
                slot["ratio"],
                fidelity_mode=fidelity_mode,
                seed_constraints=seed_constraints,
            )
            result["grid_slot"] = slot["slot"]
            result["content_type"] = slot["type"]
            results.append(result)

        return results

    def generate_campaign(
        self,
        campaign_name: str,
        emotion: str = "",
        flowers: Optional[list[str]] = None,
        products: Optional[list[str]] = None,
        shot_count: int = 5,
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
        seed_constraints: Optional[dict] = None,
    ) -> list[dict]:
        """Generate a campaign asset set using the brand's default shot plan."""
        campaign_plan = self.config.get("campaign_plan") or [
            ("product_hero", "3:4"),
            ("product_closeup", "1:1"),
            ("kitchen_table", "3:4"),
            ("doorstep_arrival", "3:4"),
            ("product_detail", "1:1"),
        ]
        plan = [(s, r) for s, r in campaign_plan][:shot_count]

        results = []
        for shot_id, ratio in plan:
            prompt = self._lookup_prompt(shot_id)
            if not prompt:
                continue

            swap = flowers or products
            if swap:
                prompt = self._apply_subject_swap(prompt, swap)
            if emotion:
                prompt = self._apply_revisions(
                    prompt,
                    f"Thread the emotional tone of '{emotion}' through the mood description.",
                )

            self._log(f"\n  Campaign shot: {shot_id}")
            result = self._run_quality_gate(
                shot_id,
                prompt,
                ratio,
                fidelity_mode=fidelity_mode,
                seed_constraints=seed_constraints,
            )
            result["campaign"] = campaign_name
            results.append(result)

        return results

    def get_library(self) -> list[dict]:
        return self.store.load_library(self.brand_id)

    def get_shot_ids(self) -> list[str]:
        return [item["shot_id"] for item in self.get_library()]

    def brand_summary(self) -> dict:
        """Return a summary of the loaded brand configuration — for agent inspection."""
        return {
            "brand_id": self.brand_id,
            "brand_name": self.config["brand_name"],
            "description": self.config.get("description", ""),
            "product_category": self.config.get("product_category", ""),
            "backend": self.backend,
            "model": self.model,
            "critic_mode": self.critic_mode,
            "critic_dimensions": [d["name"] for d in self.config["critic"]["dimensions"]],
            "pass_threshold": self.pass_threshold,
            "max_iterations": self.max_iterations,
            "library_size": len(self.get_library()),
        }

    # ── Asset discovery ──────────────────────────────────────────────────

    def discover_seed_candidates(
        self,
        query: str,
        cursor: str = "0",
        media_type: str = "image",
        limit: int = 12,
    ) -> dict:
        """Search the hosted Asset Library for Manifest-backed seed candidates.

        This is the preferred discovery path before asking for new seed photos
        or falling back to generic text-to-image: it returns real Brand Asset
        Manifest records (shop exteriors/interiors, product truth, packaging,
        lifestyle, UGC) that can be promoted into Brand Photographer seed rows.

        Filters to `media_type` (default "image") so image-generation references
        don't pick up video/B-roll cards. Returns
        `{"query", "results", "nextCursor", "base_url"}`; selected results
        should be promoted via brand_photographer_asset_manifest_sync.py before
        use as Mode B/C seeds.
        """
        data = search_asset_library(query, cursor=cursor)
        results = data.get("results", []) or []
        if media_type:
            results = [
                r for r in results
                if str(r.get("mediaType", "")).lower() == media_type.lower()
            ]
        out = {
            "query": query,
            "results": results[:limit],
            "nextCursor": data.get("nextCursor"),
            "base_url": data.get("base_url"),
        }
        if data.get("error"):
            out["error"] = data["error"]
        return out

    # ── Generation backends ──────────────────────────────────────────────

    def _generate_image(self, prompt: str, ratio: str, seed_images: Optional[list[str]] = None) -> Optional[str]:
        if self.backend == "openrouter":
            return self._generate_openrouter(prompt, ratio, seed_images=seed_images)
        return self._generate_higgsfield(prompt, ratio, seed_images=seed_images)

    def _generate_openrouter(
        self,
        prompt: str,
        ratio: str,
        seed_images: Optional[list[str]] = None,
    ) -> Optional[str]:
        ar = RATIO_MAP.get(ratio, ratio)
        try:
            content = [{"type": "text", "text": prompt}]
            for image_ref in seed_images or []:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_ref},
                })

            res = requests.post(
                OPENROUTER_URL,
                headers=self.openrouter_headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": content}],
                    "modalities": ["image", "text"],
                    "image_config": {"aspect_ratio": ar},
                },
                timeout=120,
            )
            res.raise_for_status()
            data = res.json()
            message = data["choices"][0]["message"]

            images = message.get("images", []) or []
            if images:
                url = images[0].get("image_url", {}).get("url", "")
                if url.startswith("data:image"):
                    path = self._save_base64_image(url)
                    return path if path else url
                elif url.startswith("http"):
                    return url

            content = message.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "image_url":
                        url = part["image_url"]["url"]
                        if url.startswith("data:image"):
                            path = self._save_base64_image(url)
                            return path if path else url
                        return url
                return None
            elif isinstance(content, str) and "data:image" in content:
                path = self._save_base64_image(content)
                return path if path else content
            else:
                self._log(f"    Unexpected response format: {str(content)[:100]}")
                return None

        except Exception as e:
            self._log(f"    OpenRouter error: {e}")
            return None

    def _generate_higgsfield(
        self,
        prompt: str,
        ratio: str,
        seed_images: Optional[list[str]] = None,
    ) -> Optional[str]:
        ar = RATIO_MAP.get(ratio, ratio)
        if ar not in VALID_RATIOS:
            ar = "3:4"

        cmd = [
            _higgsfield_cli_path() or "higgsfield",
            "generate",
            "create",
            self.model,
            "--prompt",
            prompt,
            "--aspect_ratio",
            ar,
            "--wait",
            "--wait-timeout",
            os.environ.get("BRAND_PHOTOGRAPHER_HIGGSFIELD_WAIT_TIMEOUT", "20m"),
        ]

        temp_paths: list[str] = []
        for image_ref in seed_images or []:
            local_path = self._image_ref_to_local_path(image_ref)
            if not local_path:
                self._log(f"    [seed] Could not resolve seed image for Higgsfield CLI: {str(image_ref)[:120]}")
                continue
            if image_ref.startswith(("http", "data:image")):
                temp_paths.append(local_path)
            cmd.extend(["--image", local_path])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 25)
            if result.returncode != 0:
                safe_err = (result.stderr or result.stdout or "").strip()[:800]
                self._log(f"    Higgsfield CLI error: {safe_err}")
                return None
            output = (result.stdout or result.stderr or "").strip()
            try:
                data = json.loads(output)
                for key in ("url", "image_url", "result_url", "output_url"):
                    if isinstance(data, dict) and isinstance(data.get(key), str) and data[key].startswith("http"):
                        return data[key]
                if isinstance(data, dict):
                    images = data.get("images") or data.get("outputs") or []
                    for item in images:
                        if isinstance(item, dict):
                            url = item.get("url") or item.get("image_url")
                            if isinstance(url, str) and url.startswith("http"):
                                return url
                        elif isinstance(item, str) and item.startswith("http"):
                            return item
            except json.JSONDecodeError:
                pass
            urls = re.findall(r"https?://\S+", output)
            if urls:
                return urls[-1].rstrip(").,]")
            self._log(f"    Higgsfield CLI returned no URL: {output[:500]}")
            return None
        except subprocess.TimeoutExpired:
            self._log("    Higgsfield CLI timed out")
            return None
        except Exception as e:
            self._log(f"    Higgsfield CLI error: {e}")
            return None
        finally:
            for path in temp_paths:
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass

    # ── Quality gate ─────────────────────────────────────────────────────

    def _get_backdrop_negation(self) -> str:
        """Return the backdrop negation string from brand config, or '' if not configured."""
        vocab = self.config.get("prompt_construction", {}).get("colour_vocabulary", {})
        return vocab.get("backdrop_correct", "")

    def _inject_backdrop_negation(self, prompt: str) -> str:
        """Ensure the brand's backdrop negation language is present in the prompt.

        Reads 'backdrop_correct' from prompt_construction.colour_vocabulary in brand.json
        and appends it if the negation language is not already in the prompt. This prevents
        backdrop colour drift (e.g. terracotta backdrops) in Mode B composite shots without
        requiring the brief author to remember to include it.
        """
        negation = self._get_backdrop_negation()
        if not negation:
            return prompt
        if "not terracotta" in prompt.lower():
            return prompt
        return f"{prompt.rstrip()} {negation}"

    def _run_quality_gate(
        self,
        shot_id: str,
        prompt: str,
        ratio: str,
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
        seed_constraints: Optional[dict] = None,
    ) -> dict:
        best_result = None
        normalized_constraints = self._normalize_seed_constraints(seed_constraints)
        seed_images, seed_context = self._select_seed_images(shot_id, prompt, normalized_constraints)

        # Mode B composite: auto-inject backdrop negation from brand config so
        # it is never omitted from the prompt regardless of how the brief was written.
        if seed_images:
            injected = self._inject_backdrop_negation(prompt)
            if injected != prompt:
                self._log("  [backdrop] Backdrop negation auto-injected from brand config")
                prompt = injected

        for iteration in range(1, self.max_iterations + 1):
            self._log(f"  Iteration {iteration}/{self.max_iterations}")

            image_ref = self._generate_image(prompt, ratio, seed_images=seed_images)
            if not image_ref:
                self._log("    Generation failed")
                continue

            self._log("    Image ready")

            critique = self._critique(
                image_ref,
                shot_id,
                prompt,
                seed_context=seed_context,
                fidelity_mode=fidelity_mode,
            )
            if not critique:
                best_result = {
                    "shot_id": shot_id, "prompt": prompt, "image_url": image_ref,
                    "score": None, "iteration": iteration,
                    "fidelity_mode": fidelity_mode,
                    "seed_constraints": normalized_constraints,
                    "selected_seeds": seed_context,
                }
                continue

            score = critique.get("overall_score", 0)
            verdict = critique.get("verdict", "ITERATE")
            self._log(f"    Score: {score}/10 — {verdict}")

            result = {
                "shot_id": shot_id, "prompt": prompt, "image_url": image_ref,
                "score": score, "iteration": iteration, "critique": critique,
                "fidelity_mode": fidelity_mode,
                "seed_constraints": normalized_constraints,
                "selected_seeds": seed_context,
            }

            if not best_result or (score and (not best_result.get("score") or score > best_result["score"])):
                best_result = result

            strict_fail = fidelity_mode == FIDELITY_MODE_STRICT and self._is_strict_fidelity_fail(critique)
            if strict_fail:
                self._log("    Strict fidelity mismatch detected — forcing iterate")

            if (score >= self.pass_threshold or verdict == "PASS") and not strict_fail:
                self._log("    PASSED")
                self._save_to_library(result)
                return result

            revisions = critique.get("prompt_revisions", "")
            if strict_fail and not revisions:
                revisions = (
                    "Match bouquet fidelity to selected seed exactly: same flower species set, "
                    "same composition hierarchy, and same colour distribution."
                )
            if revisions and iteration < self.max_iterations:
                prompt = self._apply_revisions(prompt, revisions)
                self._log("    Prompt revised")

        if best_result:
            self._save_to_library(best_result)
        return best_result or {
            "shot_id": shot_id, "prompt": prompt, "image_url": "", "score": 0, "iteration": 0,
        }

    def _normalize_seed_constraints(self, seed_constraints: Optional[dict]) -> dict:
        if not isinstance(seed_constraints, dict):
            return {}
        normalized = {}
        for key in (
            "required_seed_ids",
            "bouquet_seed_ids",
            "model_seed_ids",
            "must_include_flowers",
            "forbidden_substitutions",
            "composition_rules",
            "colour_targets",
        ):
            val = seed_constraints.get(key)
            if isinstance(val, list):
                normalized[key] = [str(v).strip() for v in val if str(v).strip()]
            elif isinstance(val, str) and val.strip():
                normalized[key] = [val.strip()]
        return normalized

    def _lookup_library_entry(self, shot_id: str) -> dict:
        matches = [item for item in self.get_library() if item.get("shot_id") == shot_id]
        if not matches:
            return {}
        return max(matches, key=lambda x: x.get("score", 0) or 0)

    def _library_seed_candidates(self, prompt: str, shot_id: str, limit: int = 2) -> list[dict]:
        """Query the hosted Asset Library for image seeds when no local seed matches."""
        query = (prompt or shot_id or "").strip()
        if not query:
            return []
        try:
            found = self.discover_seed_candidates(query, media_type="image", limit=max(limit, 6))
        except Exception as exc:
            self._log(f"  [asset-search] library query failed: {exc}")
            return []
        if found.get("error"):
            self._log(f"  [asset-search] library unavailable: {found['error']}")
            return []
        seeds: list[dict] = []
        for asset in found.get("results", []):
            seed = seed_from_search_result(asset, brand_id=self.brand_id)
            if seed.get("cdn_url"):
                seeds.append(seed)
            if len(seeds) >= limit:
                break
        if seeds:
            self._log(f"  [asset-search] {len(seeds)} library candidate(s) for '{query[:60]}'")
        return seeds

    def _select_seed_images(
        self,
        shot_id: str,
        prompt: str,
        seed_constraints: dict,
    ) -> tuple[list[str], dict]:
        """Return seed image refs for generation + metadata for critique context."""
        required_ids = set(seed_constraints.get("required_seed_ids", []))
        bouquet_ids = set(seed_constraints.get("bouquet_seed_ids", []))
        model_ids = set(seed_constraints.get("model_seed_ids", []))
        must_include_flowers = {
            x.lower() for x in seed_constraints.get("must_include_flowers", [])
        }

        # Prefer explicit ids first.
        explicit = []
        for seed in self.seeds:
            sid = seed.get("id", "")
            if sid in required_ids or sid in bouquet_ids or sid in model_ids:
                explicit.append(seed)

        if explicit:
            selected = explicit[:3]
        else:
            scored = []
            prompt_l = prompt.lower()
            shot_l = shot_id.lower()
            for seed in self.seeds:
                score = 0
                tags = [t.lower() for t in seed.get("tags", []) if isinstance(t, str)]
                flowers = [f.lower() for f in seed.get("flowers", []) if isinstance(f, str)]
                category = str(seed.get("category", "")).lower()
                if category == "bouquet":
                    score += 2
                if shot_l in " ".join(tags):
                    score += 2
                if must_include_flowers and set(flowers) & must_include_flowers:
                    score += 4
                for token in flowers:
                    if token and token in prompt_l:
                        score += 1
                scored.append((score, seed))
            scored.sort(key=lambda x: x[0], reverse=True)
            selected = [s for score, s in scored if score > 0][:3]

        # Prefer at least one bouquet seed; if available, keep one model that pairs.
        bouquets = [s for s in selected if str(s.get("category", "")).lower() == "bouquet"]
        models = [s for s in selected if str(s.get("category", "")).lower() == "model"]
        final_seeds = []
        if bouquets:
            final_seeds.append(bouquets[0])
            if models:
                b_id = bouquets[0].get("id", "")
                paired = None
                for model_seed in models:
                    patterns = model_seed.get("pairs_with", [])
                    if isinstance(patterns, list) and any(fnmatch.fnmatch(b_id, p) for p in patterns if isinstance(p, str)):
                        paired = model_seed
                        break
                final_seeds.append(paired or models[0])
        else:
            final_seeds = selected[:2]

        # Programmatic fallback: when no registered seed satisfies the brief,
        # query the hosted Asset Library for Manifest-backed image candidates
        # (the "search the hosted semantic API" branch of mode selection).
        # Skipped when the caller pinned explicit seed ids — those must resolve
        # to registered seeds, not arbitrary search hits.
        explicit_requested = bool(required_ids or bouquet_ids or model_ids)
        if not final_seeds and self.asset_search_enabled and not explicit_requested:
            final_seeds = self._library_seed_candidates(prompt, shot_id)

        image_refs = []
        context = {"seed_ids": [], "flowers": [], "colour_story": [], "notes": []}
        for seed in final_seeds:
            image_ref = seed_image_ref(seed, self.brand_dir)
            if not image_ref:
                continue
            if self.backend == "openrouter":
                image_ref = self._image_ref_to_data_url(image_ref) or ""
            if not image_ref:
                continue
            image_refs.append(image_ref)
            context["seed_ids"].append(seed.get("id"))
            if seed.get("cdn_url"):
                context.setdefault("cdn_urls", []).append(seed.get("cdn_url"))
            manifest = seed.get("asset_manifest") if isinstance(seed.get("asset_manifest"), dict) else {}
            if manifest.get("drive_file_id"):
                context.setdefault("asset_manifest_drive_file_ids", []).append(manifest.get("drive_file_id"))
            context["flowers"].extend(seed.get("flowers", []) if isinstance(seed.get("flowers"), list) else [])
            colour_story = seed.get("colour_story")
            if isinstance(colour_story, str) and colour_story:
                context["colour_story"].append(colour_story)
            if isinstance(seed.get("description"), str) and seed["description"]:
                context["notes"].append(seed["description"])

        context["flowers"] = sorted({f for f in context["flowers"] if isinstance(f, str)})
        context["colour_story"] = sorted({c for c in context["colour_story"] if isinstance(c, str)})
        context["notes"] = context["notes"][:3]
        return image_refs, context

    # ── Critic — CLI path ────────────────────────────────────────────────

    def _image_ref_to_local_path(self, image_ref: str) -> Optional[str]:
        """Return a local file path for an image ref, downloading if necessary.

        Returns None if the image cannot be resolved to a local file.
        """
        if not image_ref:
            return None

        # Already a local file
        if not image_ref.startswith("http") and not image_ref.startswith("data:"):
            p = Path(image_ref)
            return str(p) if p.exists() else None

        # HTTP URL — download to temp file
        if image_ref.startswith("http"):
            try:
                resp = requests.get(image_ref, timeout=30)
                resp.raise_for_status()
                ext = "jpg"
                ct = resp.headers.get("content-type", "")
                if "png" in ct:
                    ext = "png"
                elif "webp" in ct:
                    ext = "webp"
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                tmp.write(resp.content)
                tmp.close()
                return tmp.name
            except Exception as e:
                self._log(f"    [critic/cli] Failed to download image: {e}")
                return None

        # Base64 data URL — decode to temp file
        if image_ref.startswith("data:image"):
            try:
                header, b64_data = image_ref.split(",", 1)
                ext = "png"
                if "jpeg" in header or "jpg" in header:
                    ext = "jpg"
                elif "webp" in header:
                    ext = "webp"
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                tmp.write(base64.b64decode(b64_data))
                tmp.close()
                return tmp.name
            except Exception as e:
                self._log(f"    [critic/cli] Failed to decode base64 image: {e}")
                return None

        return None

    def _build_critic_user_text(
        self,
        shot_name: str,
        prompt: str,
        seed_context: Optional[dict],
        fidelity_mode: str,
    ) -> str:
        text = (
            f'Shot type: "{shot_name}". Prompt:\n{prompt}\n\n'
            f"Score against the {self.config['brand_name']} rubric."
        )
        if seed_context and seed_context.get("seed_ids"):
            text += (
                "\n\nSeed context for fidelity grading:"
                f"\n- fidelity_mode: {fidelity_mode}"
                f"\n- seed_ids: {', '.join(seed_context.get('seed_ids', []))}"
            )
            flowers = seed_context.get("flowers", [])
            if flowers:
                text += f"\n- expected_flowers: {', '.join(flowers)}"
            colour_story = seed_context.get("colour_story", [])
            if colour_story:
                text += f"\n- expected_colour_story: {', '.join(colour_story)}"
            notes = seed_context.get("notes", [])
            if notes:
                text += f"\n- seed_notes: {' | '.join(notes)}"
            if fidelity_mode == FIDELITY_MODE_STRICT:
                text += (
                    "\n- strict_rule: Any major bouquet species mismatch or composition mismatch must be FAIL."
                )
        return text

    def _critique_via_cli(
        self,
        image_ref: str,
        shot_name: str,
        prompt: str,
        seed_context: Optional[dict] = None,
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
    ) -> Optional[dict]:
        """Run critique using the Claude CLI (`claude --print`)."""
        local_path = self._image_ref_to_local_path(image_ref)
        if not local_path:
            self._log("    [critic/cli] Could not resolve image to local path — skipping CLI critique")
            return None

        user_text = self._build_critic_user_text(shot_name, prompt, seed_context, fidelity_mode)

        cmd = [
            "claude",
            "--print",
            "--system-prompt", self.critic_system,
            "--image", local_path,
            user_text,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # Clean up temp file if we created one
            if image_ref.startswith("http") or image_ref.startswith("data:"):
                try:
                    Path(local_path).unlink(missing_ok=True)
                except Exception:
                    pass

            if result.returncode != 0:
                self._log(f"    [critic/cli] CLI exited with code {result.returncode}: {result.stderr[:200]}")
                return None

            text = result.stdout.strip()
            if not text:
                self._log("    [critic/cli] Empty response from CLI")
                return None

            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)

        except subprocess.TimeoutExpired:
            self._log("    [critic/cli] CLI timed out")
            return None
        except json.JSONDecodeError as e:
            self._log(f"    [critic/cli] JSON parse error: {e}")
            return None
        except Exception as e:
            self._log(f"    [critic/cli] Error: {e}")
            return None

    def _critique_via_api(
        self,
        image_ref: str,
        shot_name: str,
        prompt: str,
        seed_context: Optional[dict] = None,
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
    ) -> Optional[dict]:
        """Run critique using the Anthropic API directly."""
        if not self.anthropic_key:
            self._log("    [critic/api] No API key available for fallback")
            return None
        try:
            if image_ref.startswith("data:image") or image_ref.startswith("http"):
                image_content = {
                    "type": "image",
                    "source": {"type": "url", "url": image_ref},
                }
            else:
                img_bytes = Path(image_ref).read_bytes()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                ext = Path(image_ref).suffix.lstrip(".")
                media_type = f"image/{ext}" if ext in ("png", "jpeg", "jpg", "webp", "gif") else "image/png"
                image_content = {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64},
                }

            res = requests.post(
                ANTHROPIC_URL,
                headers=self.anthropic_headers,
                json={
                    "model": self.critic_model,
                    "max_tokens": 1000,
                    "system": self.critic_system,
                    "messages": [{"role": "user", "content": [
                        image_content,
                        {"type": "text", "text": self._build_critic_user_text(
                            shot_name,
                            prompt,
                            seed_context,
                            fidelity_mode,
                        )},
                    ]}],
                },
                timeout=90,
            )
            res.raise_for_status()
            text = "".join(b.get("text", "") for b in res.json().get("content", []))
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            self._log(f"    [critic/api] Error: {e}")
            return None

    # ── Critic — dispatch ────────────────────────────────────────────────

    def _critique(
        self,
        image_ref: str,
        shot_name: str,
        prompt: str,
        seed_context: Optional[dict] = None,
        fidelity_mode: str = FIDELITY_MODE_GUIDED,
    ) -> Optional[dict]:
        """Critique an image. Tries CLI first; falls back to API on failure."""
        if self._cli_available:
            self._log(f"    [critic] Using CLI path")
            result = self._critique_via_cli(
                image_ref,
                shot_name,
                prompt,
                seed_context=seed_context,
                fidelity_mode=fidelity_mode,
            )
            if result is not None:
                return result
            # CLI attempted but failed — fall back with warning
            self._log("    [critic] CLI critique failed — falling back to API")
            return self._critique_via_api(
                image_ref,
                shot_name,
                prompt,
                seed_context=seed_context,
                fidelity_mode=fidelity_mode,
            )
        else:
            self._log(f"    [critic] Using API path (CLI not available)")
            return self._critique_via_api(
                image_ref,
                shot_name,
                prompt,
                seed_context=seed_context,
                fidelity_mode=fidelity_mode,
            )

    def _is_strict_fidelity_fail(self, critique: dict) -> bool:
        dims = critique.get("dimensions", {})
        fidelity_dim = dims.get("bouquet_fidelity", {}) if isinstance(dims, dict) else {}
        score = fidelity_dim.get("score", None)
        note = str(fidelity_dim.get("note", "")).lower()
        if isinstance(score, (int, float)) and score <= 4:
            return True
        mismatch_tokens = ("mismatch", "wrong", "missing", "substitut", "different species")
        return any(tok in note for tok in mismatch_tokens)

    # ── Prompt revision helpers ──────────────────────────────────────────

    def _apply_revisions_via_cli(self, prompt: str, revisions: str) -> Optional[str]:
        """Apply prompt revisions using the Claude CLI."""
        system = (
            "You are a prompt engineer. Apply the requested revisions to the image "
            "generation prompt. Return ONLY the revised prompt text — no explanation, "
            "no markdown, no backticks."
        )
        user_text = (
            f"CURRENT PROMPT:\n{prompt}\n\nREVISIONS TO APPLY:\n{revisions}\n\n"
            "Return the revised prompt."
        )
        cmd = ["claude", "--print", "--system-prompt", system, user_text]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                self._log(f"    [revise/cli] CLI exited with code {result.returncode}: {result.stderr[:200]}")
                return None
            text = result.stdout.strip()
            return text if text else None
        except subprocess.TimeoutExpired:
            self._log("    [revise/cli] CLI timed out")
            return None
        except Exception as e:
            self._log(f"    [revise/cli] Error: {e}")
            return None

    def _apply_revisions_via_api(self, prompt: str, revisions: str) -> Optional[str]:
        """Apply prompt revisions using the Anthropic API."""
        if not self.anthropic_key:
            return None
        try:
            res = requests.post(
                ANTHROPIC_URL,
                headers=self.anthropic_headers,
                json={
                    "model": self.critic_model,
                    "max_tokens": 2000,
                    "system": "You are a prompt engineer. Apply the requested revisions to the image generation prompt. Return ONLY the revised prompt text — no explanation, no markdown, no backticks.",
                    "messages": [{"role": "user", "content": (
                        f"CURRENT PROMPT:\n{prompt}\n\nREVISIONS TO APPLY:\n{revisions}\n\nReturn the revised prompt."
                    )}],
                },
                timeout=30,
            )
            res.raise_for_status()
            return "".join(b.get("text", "") for b in res.json().get("content", [])).strip()
        except Exception:
            return None

    def _apply_revisions(self, prompt: str, revisions: str) -> str:
        """Apply revisions to a prompt. Tries CLI first; falls back to API."""
        if self._cli_available:
            self._log("    [revise] Using CLI path")
            revised = self._apply_revisions_via_cli(prompt, revisions)
            if revised:
                return revised
            self._log("    [revise] CLI failed — falling back to API")
            revised = self._apply_revisions_via_api(prompt, revisions)
            return revised if revised else prompt
        else:
            self._log("    [revise] Using API path (CLI not available)")
            revised = self._apply_revisions_via_api(prompt, revisions)
            return revised if revised else prompt

    def _apply_subject_swap(self, prompt: str, subjects: list[str]) -> str:
        joined = ", ".join(subjects)
        return self._apply_revisions(
            prompt,
            f"Replace the primary subject description with: {joined}. Keep everything else unchanged.",
        )

    def _apply_product_swap(self, prompt: str, product: str) -> str:
        return self._apply_revisions(
            prompt,
            f"Replace the primary product/arrangement description with: {product}. Keep everything else unchanged.",
        )

    def _apply_season_modifier(self, prompt: str, season: str) -> str:
        return self._apply_revisions(
            prompt,
            f"Adjust the prompt to feel like {season}. Modify light quality, foliage, and mood accordingly while keeping the same composition and framing.",
        )

    # ── Library ──────────────────────────────────────────────────────────

    def _lookup_prompt(self, shot_id: str) -> str:
        return self._lookup_library_entry(shot_id).get("prompt", "")

    def _save_to_library(self, result: dict):
        self.store.append_library_entry(self.brand_id, {
            "shot_id": result["shot_id"],
            "shot_name": result.get("shot_name", result["shot_id"]),
            "prompt": result["prompt"],
            "image_url": result.get("image_url", ""),
            "score": result.get("score"),
            "iteration": result.get("iteration"),
            "critique": result.get("critique"),
            "campaign": result.get("campaign"),
            "grid_slot": result.get("grid_slot"),
            "fidelity_mode": result.get("fidelity_mode"),
            "seed_constraints": result.get("seed_constraints"),
            "selected_seeds": result.get("selected_seeds"),
            "brand_id": self.brand_id,
            "backend": self.backend,
            "model": self.model,
        })

    def _image_ref_to_data_url(self, image_ref: str) -> Optional[str]:
        """Convert a local path/URL/data URL image reference into a data URL."""
        if not image_ref:
            return None
        if image_ref.startswith("data:image"):
            return image_ref
        if image_ref.startswith("http"):
            try:
                resp = requests.get(image_ref, timeout=30)
                resp.raise_for_status()
                ct = resp.headers.get("content-type", "image/png")
                b64 = base64.b64encode(resp.content).decode("utf-8")
                return f"data:{ct};base64,{b64}"
            except Exception as e:
                self._log(f"    [seed] Failed to download seed image: {e}")
                return None
        try:
            path = Path(image_ref)
            if not path.exists():
                return None
            ext = path.suffix.lower().lstrip(".")
            media_type = f"image/{ext}" if ext in ("png", "jpeg", "jpg", "webp", "gif") else "image/png"
            b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
            return f"data:{media_type};base64,{b64}"
        except Exception as e:
            self._log(f"    [seed] Failed to encode local seed image: {e}")
            return None

    def _save_base64_image(self, data_url: str) -> Optional[str]:
        try:
            header, b64_data = data_url.split(",", 1)
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"
            img_bytes = base64.b64decode(b64_data)
            filename = f"{self.brand_id}_{int(time.time())}.{ext}"
            path = self.output_dir / filename
            path.write_bytes(img_bytes)
            self._log(f"    Saved: {path}")
            return str(path)
        except Exception as e:
            self._log(f"    Save error: {e}")
            return None

    def _log(self, msg: str):
        if self.verbose:
            print(msg)
