#!/usr/bin/env python3
"""Migrate Creative Brand Photographer file artifacts into the Notion backend.

Requires:
  NOTION_API_KEY
  BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID

The Notion data source should follow references/notion-backend.md. The script is
idempotent for initial migration: existing rows with the same Brand ID + Artifact
+ Record ID are skipped unless --force is provided. --force creates a fresh row
rather than deleting old page content, so use it only for deliberate snapshots.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from brand_photographer_api import FileBrandStore, NotionBrandStore, _brands_root, _load_env, _notion_data_source_id  # noqa: E402


ARTIFACT_FILES = {
    "art_direction": "art_direction",
    "colour_system": "colour_system",
    "grid_spec": "grid_spec",
}


def existing(store: NotionBrandStore, brand_id: str, artifact: str, record_id: str) -> bool:
    return bool(store._pages(brand_id, artifact, record_id))


def create_if_missing(
    store: NotionBrandStore,
    brand_id: str,
    artifact: str,
    record_id: str,
    name: str,
    *,
    json_obj: dict[str, Any] | None = None,
    content: str = "",
    force: bool = False,
) -> str:
    if not force and existing(store, brand_id, artifact, record_id):
        return "skipped"
    store._create_page(brand_id, artifact, record_id, name, json_obj=json_obj, content=content)
    return "created"


def migrate_brand(file_store: FileBrandStore, notion_store: NotionBrandStore, brand_id: str, force: bool = False) -> dict[str, int]:
    counts = {"created": 0, "skipped": 0}
    config = file_store.load_brand_config(brand_id)

    status = create_if_missing(
        notion_store,
        brand_id,
        "brand_config",
        "config",
        f"{brand_id} / brand config",
        json_obj=config,
        force=force,
    )
    counts[status] += 1

    refs = config.get("references", {})
    for artifact, ref_key in ARTIFACT_FILES.items():
        filename = refs.get(ref_key)
        if not filename:
            continue
        path = file_store.brand_dir(brand_id) / filename
        if not path.exists():
            continue
        status = create_if_missing(
            notion_store,
            brand_id,
            artifact,
            artifact,
            f"{brand_id} / {artifact}",
            content=path.read_text(),
            force=force,
        )
        counts[status] += 1

    for entry in file_store.load_library(brand_id):
        shot_id = str(entry.get("shot_id") or "prompt")
        record_id = f"prompt:{shot_id}"
        status = create_if_missing(
            notion_store,
            brand_id,
            "prompt",
            record_id,
            f"{brand_id} / prompt / {shot_id}",
            json_obj=entry,
            force=force,
        )
        counts[status] += 1

    for seed in file_store.load_seeds(brand_id):
        seed_id = str(seed.get("id") or seed.get("file") or "seed")
        status = create_if_missing(
            notion_store,
            brand_id,
            "seed",
            seed_id,
            f"{brand_id} / seed / {seed_id}",
            json_obj=seed,
            force=force,
        )
        counts[status] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brands-root", default=str(_brands_root()), help="Existing file-backed brands root")
    parser.add_argument("--brand-id", action="append", help="Brand to migrate; repeatable. Defaults to all file-backed brands")
    parser.add_argument("--data-source-id", default="", help="Override BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID")
    parser.add_argument("--force", action="store_true", help="Create new rows even when matching rows already exist")
    args = parser.parse_args()

    _load_env()
    ds_id = args.data_source_id or _notion_data_source_id()
    if not ds_id:
        raise SystemExit("Set BRAND_PHOTOGRAPHER_NOTION_DATA_SOURCE_ID or pass --data-source-id")
    if not os.environ.get("NOTION_API_KEY"):
        raise SystemExit("Set NOTION_API_KEY")

    file_store = FileBrandStore(Path(args.brands_root))
    notion_store = NotionBrandStore(ds_id)
    brands = args.brand_id or file_store.list_brands()
    summary = {}
    for brand_id in brands:
        summary[brand_id] = migrate_brand(file_store, notion_store, brand_id, force=args.force)
    print(json.dumps({"data_source_id": ds_id, "brands": summary}, indent=2))


if __name__ == "__main__":
    main()
