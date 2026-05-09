#!/usr/bin/env python3
"""Create a polished 4:5 Instagram cover from a Reel URL.

Dependencies: uvx, yt-dlp via uvx, ffmpeg/ffprobe, OPENROUTER_API_KEY.
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_MODEL = os.environ.get("REEL_COVER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FIG_BLOOM_RUBRIC = """
Apply Fig & Bloom direction: premium florist/fashion editorial, vivid true-to-life florals,
warm clean light, calm negative space, refined styling, no generic stock-photo energy,
no cold/blue cast, no desaturated flowers, no awkward motion/blur/text overlays.
""".strip()


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(
            f"command failed {p.returncode}: {' '.join(cmd)}\nSTDOUT={p.stdout[-2000:]}\nSTDERR={p.stderr[-4000:]}"
        )
    return p


def need(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Required command not found on PATH: {cmd}")


def ffprobe_json(path: Path) -> dict[str, Any]:
    p = run([
        "ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)
    ], timeout=120)
    return json.loads(p.stdout)


def video_dims(path: Path) -> tuple[int, int, float]:
    data = ffprobe_json(path)
    stream = next(s for s in data.get("streams", []) if s.get("codec_type") == "video")
    w, h = int(stream["width"]), int(stream["height"])
    duration = float(data.get("format", {}).get("duration") or stream.get("duration") or 0)
    return w, h, duration


def download_reel(url: str, outdir: Path, cookies: str | None = None) -> Path:
    cmd = ["uvx", "yt-dlp", "--no-playlist", "--restrict-filenames", "-o", "source.%(ext)s"]
    if cookies:
        if cookies in {"chrome", "firefox", "safari", "edge", "brave"}:
            cmd += ["--cookies-from-browser", cookies]
        else:
            cmd += ["--cookies", cookies]
    cmd.append(url)
    run(cmd, cwd=outdir, timeout=600)
    candidates = sorted(outdir.glob("source.*"), key=lambda p: p.stat().st_size, reverse=True)
    if not candidates:
        raise RuntimeError("yt-dlp completed but no source video was found")
    # Prefer merged mp4 when available.
    for p in candidates:
        if p.suffix.lower() == ".mp4":
            return p
    return candidates[0]


def extract_frames(video: Path, outdir: Path, fps: float) -> list[Path]:
    frames = outdir / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps},scale=360:-1", str(frames / "frame_%03d.jpg")], timeout=600)
    files = sorted(frames.glob("frame_*.jpg"))
    if not files:
        raise RuntimeError("No frames extracted")
    return files


def label_frames(frames: list[Path], outdir: Path) -> list[Path]:
    labelled = outdir / "frames_labeled"
    labelled.mkdir(parents=True, exist_ok=True)
    labelled_files: list[Path] = []
    for f in frames:
        label = f.stem.split("_")[-1]
        dest = labelled / f.name
        vf = (
            "drawbox=x=8:y=8:w=92:h=36:color=black@0.65:t=fill,"
            f"drawtext=text='{label}':x=18:y=13:fontsize=24:fontcolor=white"
        )
        run(["ffmpeg", "-y", "-i", str(f), "-vf", vf, str(dest)], timeout=60)
        labelled_files.append(dest)
    return labelled_files


def make_sheet(images_glob: str, dest: Path, cols: int = 5, rows: int | None = None, scale_w: int = 240) -> Path:
    if rows is None:
        n = len(glob.glob(images_glob))
        rows = max(1, math.ceil(n / cols))
    vf = f"scale={scale_w}:-1,tile={cols}x{rows}:padding=4:margin=4:color=white"
    run(["ffmpeg", "-y", "-pattern_type", "glob", "-i", images_glob, "-vf", vf, "-frames:v", "1", str(dest)], timeout=120)
    return dest


def openrouter_vision(image: Path, prompt: str, *, model: str = DEFAULT_MODEL, timeout: int = 180) -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is required for Gemini/vision selection")
    b64 = base64.b64encode(image.read_bytes()).decode()
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
        ]}],
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hermes.local",
            "X-Title": "Hermes Instagram Reel Cover",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"]


def parse_jsonish(text: str) -> dict[str, Any]:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if m:
        text = m.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def choose_frame(sheet: Path, brand: str, model: str) -> dict[str, Any]:
    rubric = FIG_BLOOM_RUBRIC if brand.lower() in {"fig-and-bloom", "fig_bloom", "fig & bloom", "figandbloom"} else ""
    prompt = f"""
This contact sheet has visible numeric labels on each frame. Pick the single best numbered frame for a 4:5 Instagram feed cover for a premium florist/fashion editorial grid.
Prefer: clean completed floral arrangement, sharpness, elegant hands or styling, warm attractive colour, calm negative space, no awkward motion, no blur, no text overlays.
{rubric}
Return strict JSON only: {{"best_label":"019", "timestamp_seconds":18, "why":"...", "crop_notes":"...", "runners_up":[...]}}.
""".strip()
    return parse_jsonish(openrouter_vision(sheet, prompt, model=model))


def generate_crop_candidates(video: Path, timestamp: float, outdir: Path, target_w: int, target_h: int) -> list[dict[str, Any]]:
    w, h, _ = video_dims(video)
    cand_dir = outdir / "cover_candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []

    # Generate both full-width and tighter editorial crops. Full-width 9:16→4:5
    # crops are safe, but often leave too much wall/floor or distracting side props.
    # Tighter crops let the vision critic pick a clearer hero subject.
    seen: set[tuple[int, int, int, int]] = set()
    for width_factor in (1.0, 0.9, 0.8):
        crop_w = min(w, int(round(w * width_factor)))
        crop_h = min(h, int(round(crop_w * 5 / 4)))
        if crop_h > h:
            crop_h = h
            crop_w = int(round(crop_h * 4 / 5))
        max_x = max(0, w - crop_w)
        max_y = max(0, h - crop_h)
        xs = sorted({0, max_x, max(0, max_x // 2)}) if max_x else [0]
        ys = sorted({0, max_y, max(0, int(max_y * 0.25)), max(0, int(max_y * 0.40)), max(0, int(max_y * 0.55))})
        for x in xs:
            for y in ys:
                key = (x, y, crop_w, crop_h)
                if key in seen:
                    continue
                seen.add(key)
                dest = cand_dir / f"cover_w{crop_w:04d}_x{x:04d}_y{y:04d}.jpg"
                vf = f"crop={crop_w}:{crop_h}:{x}:{y},scale={target_w}:{target_h}:flags=lanczos,eq=brightness=0.02:contrast=1.10:saturation=1.18:gamma=1.02,unsharp=5:5:0.75:3:3:0.3"
                run(["ffmpeg", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", "-vf", vf, "-q:v", "2", str(dest)], timeout=120)
                out.append({"path": str(dest), "x": x, "y": y, "w": crop_w, "h": crop_h})
    return out


def choose_crop(candidates: list[dict[str, Any]], outdir: Path, brand: str, model: str) -> dict[str, Any]:
    # Create labelled crop copies so the critic can choose by filename/label.
    labelled = outdir / "crop_labeled"
    labelled.mkdir(parents=True, exist_ok=True)
    for idx, c in enumerate(candidates, 1):
        label = f"C{idx}"
        dest = labelled / f"{label}_y{int(c['y']):04d}.jpg"
        vf = "drawbox=x=8:y=8:w=90:h=40:color=black@0.65:t=fill," + f"drawtext=text='{label}':x=18:y=14:fontsize=26:fontcolor=white"
        run(["ffmpeg", "-y", "-i", c["path"], "-vf", vf, str(dest)], timeout=60)
        c["label"] = label
        c["labelled_path"] = str(dest)
    sheet = make_sheet(str(labelled / "*.jpg"), outdir / "crop_candidates_sheet.jpg", cols=2, rows=math.ceil(len(candidates) / 2), scale_w=270)
    rubric = FIG_BLOOM_RUBRIC if brand.lower() in {"fig-and-bloom", "fig_bloom", "fig & bloom", "figandbloom"} else ""
    prompt = f"""
These are labelled 4:5 crop candidates from the selected Reel frame. Pick the best crop for a premium Instagram feed cover.
Prefer balanced subject, complete bouquet/vase, clean negative space, no awkward cutoffs, no floor/cabinet clutter unless it improves lifestyle context.
{rubric}
Return strict JSON only: {{"best_label":"C2", "why":"..."}}.
""".strip()
    choice = parse_jsonish(openrouter_vision(sheet, prompt, model=model))
    best_label = str(choice.get("best_label", "C1")).upper()
    best = next((c for c in candidates if c.get("label", "").upper() == best_label), candidates[0])
    best["crop_choice"] = choice
    best["crop_sheet"] = str(sheet)
    return best


def maybe_ai_finish(input_path: Path, output_path: Path) -> tuple[Path, str]:
    cmd_tmpl = os.environ.get("REEL_COVER_AI_EDIT_CMD")
    if not cmd_tmpl:
        return input_path, "ffmpeg_deterministic_enhancement"
    prompt = (
        "Polish this Instagram Reel still as a premium florist feed cover. Preserve the exact bouquet, vase, room, and composition. "
        "Improve white balance, natural warmth, flower vibrancy, local contrast, fine detail, and subtle upscale. Remove video compression artifacts only. "
        "Do not add objects, text, logos, new flowers, or change the arrangement."
    )
    cmd = cmd_tmpl.format(input=str(input_path), output=str(output_path), prompt=prompt)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if p.returncode or not output_path.exists():
        print(f"AI edit command failed; using deterministic output. STDERR={p.stderr[-1000:]}", file=sys.stderr)
        return input_path, "ffmpeg_deterministic_enhancement_ai_edit_failed"
    return output_path, "external_ai_edit"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url", help="Instagram Reel URL")
    ap.add_argument("--outdir", default="/opt/data/tmp/instagram-reel-cover", help="Output working directory")
    ap.add_argument("--brand", default="fig-and-bloom")
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--cookies", help="Path to cookies.txt or browser name for yt-dlp --cookies-from-browser")
    ap.add_argument("--target-width", type=int, default=1080)
    ap.add_argument("--target-height", type=int, default=1350)
    args = ap.parse_args()

    for c in ("uvx", "ffmpeg", "ffprobe"):
        need(c)

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    video = download_reel(args.url, outdir, args.cookies)
    w, h, duration = video_dims(video)
    frames = extract_frames(video, outdir, args.fps)
    label_frames(frames, outdir)
    sheet = make_sheet(str(outdir / "frames_labeled" / "*.jpg"), outdir / "contact_sheet_labeled.jpg", cols=5, scale_w=240)

    frame_choice = choose_frame(sheet, args.brand, args.model)
    label = str(frame_choice.get("best_label") or frame_choice.get("frame_number") or "001")
    label_int = int(re.sub(r"\D", "", label) or "1")
    timestamp = float(frame_choice.get("timestamp_seconds") or max(0, (label_int - 1) / args.fps))
    timestamp = max(0.0, min(duration, timestamp))

    candidates = generate_crop_candidates(video, timestamp, outdir, args.target_width, args.target_height)
    crop = choose_crop(candidates, outdir, args.brand, args.model)

    deterministic = outdir / "instagram_reel_cover_4x5.jpg"
    shutil.copyfile(crop["path"], deterministic)
    ai_out = outdir / "instagram_reel_cover_4x5_ai.jpg"
    final_path, method = maybe_ai_finish(deterministic, ai_out)

    final_w, final_h, _ = video_dims(final_path)
    if final_w * 5 != final_h * 4:
        raise RuntimeError(f"Final output is not 4:5: {final_w}x{final_h}")

    report = {
        "url": args.url,
        "video": str(video),
        "source_width": w,
        "source_height": h,
        "duration_seconds": duration,
        "model": args.model,
        "contact_sheet": str(sheet),
        "frame_choice": frame_choice,
        "selected_timestamp_seconds": timestamp,
        "crop": crop,
        "enhancement_method": method,
        "final_cover": str(final_path),
        "final_width": final_w,
        "final_height": final_h,
    }
    report_path = outdir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"FINAL_COVER={final_path}")
    print(f"REPORT={report_path}")


if __name__ == "__main__":
    main()
