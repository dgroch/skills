#!/usr/bin/env python3
"""
Batch organize files on Google Shared Drive into classification folders.

Uses atomic parent swaps (addParents + removeParents in single PATCH request)
to comply with shared drive restrictions. Resumable via progress file.

Usage:
    # 1. First, scan the drive to build inventory:
    gws drive files list --params '{"pageSize":1000,"fields":"nextPageToken,files(id,name,mimeType,parents)","supportsAllDrives":true,"includeItemsFromAllDrives":true,"corpora":"drive","driveId":"<DRIVE_ID>"}' --page-all --page-limit 50 --page-delay 300 > /tmp/drive_scan.txt

    # 2. Run this script (update SCAN_FILE and DRIVE_ID below):
    python3 organize_assets.py

Rate limiting: 2.5s between moves (~24/min) to avoid quota errors.
Progress: saved to /tmp/organize_progress_v2.json — re-run to resume.
"""

import json
import os
import subprocess
import sys
import time
from collections import defaultdict

# === CONFIG — update these for your drive ===
DRIVE_ID = "0AOMVrKhhWKIwUk9PVA"  # Synology Photos
PROGRESS_FILE = "/tmp/organize_progress_v2.json"
SCAN_FILE = "/tmp/drive_scan_full.txt"
LOG_FILE = "/tmp/organize_log.txt"
GWS = "/opt/data/npm-global/bin/gws"

DELAY_BETWEEN_MOVES = 2.5
DELAY_BETWEEN_FOLDERS = 0.5

# Folder name → target category
FOLDER_CLASSIFICATION = {
    "Products": "Products",
    "PhotoLibrary": "Products",
    "Generated Lifestyle Images": "Lifestyle",
    "Generated Lifestyle Video": "Video",
    "Banner Ads": "Graphics",
    "Backgrounds": "Graphics",
    "Ai Backdrops": "Graphics",
    "Illustrations": "Graphics",
    "Advertising": "Graphics",
    "NLC | Best Sellers - Google PMAX": "Graphics",
    "NLC | Review Meta Ads": "Graphics",
    "NLC | WOW Giveaway Statics": "Graphics",
    "UGC Images": "UGC",
    "UGC Videos": "UGC",
    "Tagbox": "UGC",
    "Logos": "Brand Assets",
}

SKIP_FOLDERS = {
    "Photos", "Content by Monthly Theme", "Social Media",
    "Behind the Scenes", "Events", "Right Hook Digital",
    "AI Talent", "Music", "Website",
}

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg"}


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def gws_cmd(args, timeout=30):
    """Run gws CLI command, return (parsed_json, error_string)."""
    env = {
        **os.environ,
        "PATH": "/opt/data/npm-global/bin:" + os.environ.get("PATH", ""),
        "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config",
        "GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND": "file",
    }
    try:
        result = subprocess.run(
            [GWS] + args, capture_output=True, text=True, timeout=timeout, env=env
        )
        output = result.stdout.strip()
        lines = [l for l in output.split("\n") if l.strip() and not l.startswith("Using keyring")]
        clean = "\n".join(lines).strip()
        if not clean:
            return None, result.stderr.strip() or f"Exit {result.returncode}"
        try:
            return json.loads(clean), None
        except json.JSONDecodeError:
            for line in reversed(clean.split("\n")):
                if line.strip().startswith("{"):
                    try:
                        return json.loads(line.strip()), None
                    except json.JSONDecodeError:
                        continue
            return None, f"JSON parse error: {clean[:200]}"
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


def create_folder(name, parent_id):
    """Create a folder on the shared drive. Returns folder ID or None."""
    data, err = gws_cmd([
        "drive", "files", "create",
        "--json", json.dumps({
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }),
        "--params", json.dumps({"fields": "id,name", "supportsAllDrives": True}),
    ])
    if err:
        log(f"  ❌ Create folder '{name}': {err}")
        return None
    fid = data.get("id")
    if fid:
        log(f"  📁 Created '{name}' ({fid})")
    return fid


def move_file_atomic(file_id, old_parent, new_parent):
    """Atomic parent swap: remove old parent, add new parent in single PATCH."""
    data, err = gws_cmd([
        "drive", "files", "update",
        "--params", json.dumps({
            "fileId": file_id,
            "addParents": new_parent,
            "removeParents": old_parent,
            "supportsAllDrives": True,
            "fields": "id,name,parents",
        }),
    ])
    if err:
        return False, err
    return True, None


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"moved": {}, "created_folders": {}, "failed": {}, "stats": {"moved": 0, "failed": 0, "skipped": 0}}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def scan_drive():
    """Read scan file, return (files_list, folders_dict)."""
    all_items = []
    if not os.path.exists(SCAN_FILE):
        log(f"❌ Scan file not found: {SCAN_FILE}")
        return [], {}
    with open(SCAN_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Using"):
                continue
            try:
                page = json.loads(line)
                all_items.extend(page.get("files", []))
            except json.JSONDecodeError:
                pass

    folders = {}
    files = []
    for item in all_items:
        if item.get("mimeType") == "application/vnd.google-apps.folder":
            folders[item["id"]] = item
        else:
            files.append(item)
    log(f"📊 Loaded {len(files)} files and {len(folders)} folders")
    return files, folders


def get_root_folder(file_item, folders_map):
    """Walk parent chain to find root-level folder name."""
    parents = file_item.get("parents", [])
    if not parents:
        return None
    current = parents[0]
    visited = set()
    while current and current != DRIVE_ID and current not in visited:
        visited.add(current)
        if current in folders_map:
            folder = folders_map[current]
            fp = folder.get("parents", [])
            if fp and fp[0] == DRIVE_ID:
                return folder["name"]
            current = fp[0] if fp else None
        else:
            return None
    return None


def classify_files(files, folders_map):
    classification = defaultdict(list)
    for f in files:
        name = f.get("name", "").lower()
        ext = os.path.splitext(name)[1].lower()
        mime = f.get("mimeType", "")
        root_name = get_root_folder(f, folders_map)
        if not root_name or root_name in SKIP_FOLDERS or root_name not in FOLDER_CLASSIFICATION:
            continue
        cat = FOLDER_CLASSIFICATION[root_name]
        if ext in VIDEO_EXTENSIONS or "video" in mime:
            cat = "Video"
        classification[cat].append(f)
    return classification


def main():
    log("=" * 60)
    log("Asset Organization — Starting")
    log("=" * 60)

    progress = load_progress()
    already_moved = set(progress["moved"].keys())
    log(f"📋 Previously moved: {len(already_moved)} files")

    files, folders_map = scan_drive()
    if not files:
        log("❌ No files found")
        sys.exit(1)

    # Reuse existing target folders at drive root
    for fid, folder in folders_map.items():
        if folder["name"] in FOLDER_CLASSIFICATION.values():
            parents = folder.get("parents", [])
            if parents and parents[0] == DRIVE_ID:
                progress["created_folders"][folder["name"]] = fid

    # Classify and filter already-moved
    classification = classify_files(files, folders_map)
    for cat in list(classification.keys()):
        classification[cat] = [f for f in classification[cat] if f["id"] not in already_moved]

    log(f"\n📊 Classification:")
    total = 0
    for cat in ["Products", "Lifestyle", "Video", "Graphics", "UGC", "Brand Assets"]:
        c = len(classification.get(cat, []))
        total += c
        log(f"  {cat}: {c}")
    log(f"  Total to move: {total}")

    if total == 0:
        log("✅ Nothing to move!")
        return

    # Create missing target folders
    for cat in ["Products", "Lifestyle", "Video", "Graphics", "UGC", "Brand Assets"]:
        if cat in progress["created_folders"] or not classification.get(cat):
            continue
        fid = create_folder(cat, DRIVE_ID)
        if fid:
            progress["created_folders"][cat] = fid
            save_progress(progress)
            time.sleep(DELAY_BETWEEN_FOLDERS)

    log(f"\n📁 Target folders:")
    for cat, fid in sorted(progress["created_folders"].items()):
        log(f"  {cat}: {fid}")

    # Move files (smallest categories first for quick wins)
    log(f"\n🚀 Moving {total} files...")
    moved = 0
    failed = 0
    start = time.time()

    for cat in ["Brand Assets", "Lifestyle", "UGC", "Graphics", "Video", "Products"]:
        cat_files = classification.get(cat, [])
        if not cat_files:
            continue
        target = progress["created_folders"].get(cat)
        if not target:
            log(f"⚠️ No target for {cat}")
            continue

        log(f"\n📂 {cat}: {len(cat_files)} files")
        for f in cat_files:
            old_parents = f.get("parents", [])
            if not old_parents:
                progress["stats"]["skipped"] += 1
                continue
            old_parent = old_parents[0]
            if old_parent == target:
                progress["moved"][f["id"]] = cat
                progress["stats"]["skipped"] += 1
                continue

            ok, err = move_file_atomic(f["id"], old_parent, target)
            if ok:
                progress["moved"][f["id"]] = cat
                progress["stats"]["moved"] += 1
                moved += 1
                if moved % 50 == 0:
                    elapsed = time.time() - start
                    rate = moved / (elapsed / 60) if elapsed > 0 else 0
                    remaining = (total - moved) / rate if rate > 0 else 0
                    log(f"  ✅ {moved}/{total} ({rate:.1f}/min, ~{remaining:.0f}min left)")
                save_progress(progress)
                time.sleep(DELAY_BETWEEN_MOVES)
            else:
                progress["failed"][f["id"]] = err
                progress["stats"]["failed"] += 1
                failed += 1
                log(f"  ❌ '{f['name']}': {err}")
                if failed > 50:
                    log(f"🛑 {failed} failures, stopping")
                    save_progress(progress)
                    sys.exit(1)
                time.sleep(1)

    elapsed = time.time() - start
    rate = moved / (elapsed / 60) if elapsed > 0 else 0
    log(f"\n{'=' * 60}")
    log(f"✅ Done! Moved {moved} in {elapsed/60:.1f}min ({rate:.1f}/min)")
    log(f"   Failed: {failed} | Total all-time: {progress['stats']['moved']}")
    log(f"{'=' * 60}")
    save_progress(progress)


if __name__ == "__main__":
    main()
