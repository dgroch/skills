import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

API_PATH = Path(__file__).resolve().parents[1] / "references" / "brand_photographer_api.py"
spec = importlib.util.spec_from_file_location("brand_photographer_api", API_PATH)
assert spec is not None and spec.loader is not None
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


def rt(value):
    return {"type": "rich_text", "rich_text": [{"plain_text": value}]}


def title(value):
    return {"type": "title", "title": [{"plain_text": value}]}


def select(value):
    return {"type": "select", "select": {"name": value}}


class FakeNotion:
    def __init__(self):
        self.pages = []
        self.children = {}
        self.next_id = 1

    def add_page(self, brand_id, artifact, record_id, json_obj=None, content=""):
        page_id = f"page-{self.next_id}"
        self.next_id += 1
        page = {
            "id": page_id,
            "properties": {
                "Name": title(f"{brand_id} / {record_id}"),
                "Brand ID": rt(brand_id),
                "Artifact": select(artifact),
                "Record ID": rt(record_id),
                "JSON": rt(json.dumps(json_obj or {}, separators=(",", ":")) if json_obj is not None else ""),
                "Content": rt(content),
            },
        }
        self.pages.append(page)
        payload = json.dumps(json_obj or {}, separators=(",", ":")) if json_obj is not None else content
        self.children[page_id] = [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": payload}]}}] if payload else []
        return page

    @staticmethod
    def text_prop(page, prop):
        p = page["properties"][prop]
        typ = p["type"]
        return "".join(x.get("plain_text", "") for x in p.get(typ, [])) if typ in ("title", "rich_text") else p[typ]["name"]

    def request(self, method, path, payload=None):
        if method == "POST" and path.endswith("/query"):
            filters = payload.get("filter", {}).get("and") or [payload.get("filter", {})]
            def ok(page):
                for clause in filters:
                    prop = clause.get("property")
                    expected = None
                    if "rich_text" in clause:
                        expected = clause["rich_text"].get("equals")
                    elif "select" in clause:
                        expected = clause["select"].get("equals")
                    if expected is not None and self.text_prop(page, prop) != expected:
                        return False
                return True
            return {"results": [p for p in self.pages if ok(p)], "has_more": False}
        if method == "GET" and path.startswith("/blocks/"):
            page_id = path.split("/")[2]
            return {"results": self.children.get(page_id, []), "has_more": False}
        if method == "POST" and path == "/pages":
            page_id = f"page-{self.next_id}"
            self.next_id += 1
            props = payload["properties"]
            page = {"id": page_id, "properties": {}}
            for key, value in props.items():
                if "title" in value:
                    page["properties"][key] = {"type": "title", "title": [{"plain_text": value["title"][0]["text"]["content"]}]}
                elif "rich_text" in value:
                    page["properties"][key] = {"type": "rich_text", "rich_text": [{"plain_text": x["text"]["content"]} for x in value["rich_text"]]}
                elif "select" in value:
                    page["properties"][key] = {"type": "select", "select": value["select"]}
                elif "number" in value:
                    page["properties"][key] = {"type": "number", "number": value["number"]}
            self.pages.append(page)
            converted_children = []
            for child in payload.get("children", []):
                typ = child["type"]
                rich = child[typ]["rich_text"]
                converted_children.append({"type": typ, typ: {"rich_text": [{"plain_text": x["text"]["content"]} for x in rich]}})
            self.children[page_id] = converted_children
            return page
        if method == "PATCH" and path.startswith("/pages/"):
            page_id = path.split("/")[2]
            page = next(p for p in self.pages if p["id"] == page_id)
            for key, value in (payload or {}).get("properties", {}).items():
                if "title" in value:
                    page["properties"][key] = {"type": "title", "title": [{"plain_text": value["title"][0]["text"]["content"]}]}
                elif "rich_text" in value:
                    page["properties"][key] = {"type": "rich_text", "rich_text": [{"plain_text": x["text"]["content"]} for x in value["rich_text"]]}
                elif "select" in value:
                    page["properties"][key] = {"type": "select", "select": value["select"]}
                elif "number" in value:
                    page["properties"][key] = {"type": "number", "number": value["number"]}
            return page
        raise AssertionError(f"Unexpected request {method} {path} {payload}")


class StorageTests(unittest.TestCase):
    def test_file_store_loads_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brand = root / "demo"
            brand.mkdir()
            cfg = {
                "brand_id": "demo",
                "brand_name": "Demo",
                "references": {
                    "art_direction": "art-direction.md",
                    "colour_system": "colour-system.md",
                    "grid_spec": "grid-spec.md",
                    "prompt_library": "prompt-library.json",
                    "seeds_manifest": "seeds.json",
                },
                "critic": {"dimensions": []},
                "grid_pattern": [],
            }
            (brand / "brand.json").write_text(json.dumps(cfg))
            (brand / "prompt-library.json").write_text(json.dumps([{"shot_id": "hero", "score": 8}]))
            (brand / "seeds.json").write_text(json.dumps({"seeds": [{"id": "seed-1", "file": "seeds/a.jpg"}]}))
            store = api.FileBrandStore(root)
            self.assertEqual(store.list_brands(), ["demo"])
            self.assertEqual(store.load_library("demo")[0]["shot_id"], "hero")
            self.assertEqual(store.load_seeds("demo")[0]["id"], "seed-1")

    def test_seed_without_local_file_can_use_cdn_url(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brand = root / "demo"
            brand.mkdir()
            cfg = {
                "brand_id": "demo",
                "brand_name": "Demo",
                "references": {"seeds_manifest": "seeds.json"},
                "critic": {"dimensions": []},
                "grid_pattern": [],
            }
            (brand / "brand.json").write_text(json.dumps(cfg))
            (brand / "seeds.json").write_text(json.dumps({"seeds": [{
                "id": "seed-cdn",
                "category": "bouquet",
                "cdn_url": "https://brand-cdn.example/figandbloom/seeds/seed-cdn.jpg",
                "tags": ["hero"],
            }]}))
            store = api.FileBrandStore(root)
            seeds = store.load_seeds("demo")
            self.assertEqual(seeds[0]["id"], "seed-cdn")
            # Generation should be able to resolve a seed image reference even
            # when Notion/manifest metadata is canonical and no local file path
            # has been cached yet.
            ref = api.seed_image_ref(seeds[0], brand)
            self.assertEqual(ref, "https://brand-cdn.example/figandbloom/seeds/seed-cdn.jpg")

    def test_build_seed_from_asset_manifest_record_preserves_cdn_and_handles(self):
        record = {
            "file": {"id": "drive-1", "name": "lisbon-bouquet.jpg", "webViewLink": "https://drive/item"},
            "analysis": {
                "content_type": "product hero",
                "overall_description": "Warm lisbon bouquet on a table.",
                "visual_tags": ["Lisbon", "warm whites"],
                "mood_tone": ["soft"],
                "products_or_flowers": ["roses", "lisianthus"],
                "usable_for": ["product page", "ad creative"],
                "setting_location": "studio table",
            },
            "preview_url": "https://brand-cdn.example/asset-manifest/lisbon.jpg",
        }
        seed = api.seed_from_asset_manifest_record(record, brand_id="fig-and-bloom", category="bouquet")
        self.assertEqual(seed["id"], "asset-drive-1")
        self.assertEqual(seed["cdn_url"], "https://brand-cdn.example/asset-manifest/lisbon.jpg")
        self.assertEqual(seed["asset_manifest"]["drive_file_id"], "drive-1")
        self.assertIn("roses", seed["flowers"])
        self.assertIn("product page", seed["usable_for"])

    def test_notion_seed_rows_include_asset_manifest_and_cdn_properties(self):
        fake = FakeNotion()
        store = api.NotionBrandStore("ds-test", api_key="secret", request_fn=fake.request)
        seed = {
            "id": "asset-drive-1",
            "category": "bouquet",
            "cdn_url": "https://brand-cdn.example/asset-manifest/lisbon.jpg",
            "file": "seeds/asset-manifest/asset-drive-1.jpg",
            "asset_manifest": {"drive_file_id": "drive-1", "page_id": "notion-page-1", "database_id": "asset-db"},
        }
        store.upsert_seed("fig-and-bloom", seed)
        page = fake.pages[-1]
        self.assertEqual(FakeNotion.text_prop(page, "CDN URL"), seed["cdn_url"])
        self.assertEqual(FakeNotion.text_prop(page, "Drive File ID"), "drive-1")
        self.assertEqual(FakeNotion.text_prop(page, "Asset Manifest Page ID"), "notion-page-1")
        self.assertEqual(FakeNotion.text_prop(page, "Local File"), "seeds/asset-manifest/asset-drive-1.jpg")

    def test_notion_seed_upsert_refreshes_json_property(self):
        fake = FakeNotion()
        store = api.NotionBrandStore("ds-test", api_key="secret", request_fn=fake.request)
        store.upsert_seed("fig-and-bloom", {"id": "seed-1", "category": "bouquet", "cdn_url": "https://old.example/a.jpg"})
        store.upsert_seed("fig-and-bloom", {"id": "seed-1", "category": "bouquet", "cdn_url": "https://new.example/a.jpg"})
        seeds = store.load_seeds("fig-and-bloom")
        self.assertEqual(len(seeds), 1)
        self.assertEqual(seeds[0]["cdn_url"], "https://new.example/a.jpg")

    def test_notion_store_loads_rows_and_appends_prompt(self):
        fake = FakeNotion()
        cfg = {
            "brand_id": "demo",
            "brand_name": "Demo",
            "references": {
                "art_direction": "art-direction.md",
                "colour_system": "colour-system.md",
                "grid_spec": "grid-spec.md",
                "prompt_library": "prompt-library.json",
                "seeds_manifest": "seeds.json",
            },
            "critic": {"dimensions": []},
            "grid_pattern": [],
            "long": "x" * 3000,
        }
        fake.add_page("demo", "brand_config", "config", cfg)
        fake.add_page("demo", "art_direction", "art_direction", content="art")
        fake.add_page("demo", "seed", "seed-1", {"id": "seed-1", "file": "seeds/a.jpg"})
        store = api.NotionBrandStore("ds-test", api_key="secret", request_fn=fake.request)
        self.assertEqual(store.list_brands(), ["demo"])
        self.assertEqual(store.load_brand_config("demo")["long"], "x" * 3000)
        self.assertTrue(store.artifact_exists("demo", "prompt_library"))
        self.assertEqual(store.load_text_artifact("demo", "art_direction"), "art")
        self.assertEqual(store.load_seeds("demo")[0]["id"], "seed-1")
        store.append_library_entry("demo", {"shot_id": "hero", "prompt": "make image", "score": 9})
        prompts = store.load_library("demo")
        self.assertEqual(prompts[0]["shot_id"], "hero")
        self.assertEqual(prompts[0]["score"], 9)


if __name__ == "__main__":
    unittest.main()
