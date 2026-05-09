#!/usr/bin/env python3
"""Create a polished 4:5 Instagram cover from a Reel URL.

Dependencies: uvx, yt-dlp via uvx, ffmpeg/ffprobe, OPENAI_API_KEY for default GPT Image enhancement.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import mimetypes
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

OPENAI_IMAGES_EDIT_URL = "https://api.openai.com/v1/images/edits"
DEFAULT_IMAGE_MODEL = os.environ.get("REEL_COVER_IMAGE_MODEL", "gpt-image-2")

FIG_BLOOM_SOCIAL_FEED_RUBRIC = """
Fig & Bloom social-feed direction: romantic, intimate, editorial, botanical, warm, and slightly luxe.
Use a premium fashion-florist feel with natural realistic flowers, warm clean whites, cream/charcoal/sage/blush/burgundy tones,
subtle contrast, and elegant negative space. Preserve the real bouquet/product and composition. Remove only video compression,
minor noise, distracting floor/cabinet clutter, and small artefacts where safe. Do not add text, logos, new flowers, neon colour,
cartoon styling, or corporate stock-photo polish.
""".strip()


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    print("+ " + " ".join(cmd), flush=True)
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_bytes,
        capture_output=True,
        timeout=timeout,
    )
    if p.returncode:
        raise RuntimeError(
            f"command failed {p.returncode}: {' '.join(cmd)}\nSTDOUT={p.stdout[-2000:].decode(errors='ignore')}\nSTDERR={p.stderr[-4000:].decode(errors='ignore')}"
        )
    return p


def need(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Required command not found on PATH: {cmd}")


def ffprobe_json(path: Path) -> dict[str, Any]:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], timeout=120)
    return json.loads(p.stdout.decode())


def media_dims(path: Path) -> tuple[int, int, float]:
    data = ffprobe_json(path)
    stream = next(s for s in data.get("streams", []) if s.get("codec_type") in {"video", "image"})
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
    for p in candidates:
        if p.suffix.lower() == ".mp4":
            return p
    return candidates[0]


def extract_frames(video: Path, outdir: Path, fps: float) -> list[Path]:
    frames = outdir / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps},scale=540:-1", str(frames / "frame_%03d.jpg")], timeout=600)
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
        vf = "drawbox=x=8:y=8:w=92:h=36:color=black@0.65:t=fill," + f"drawtext=text='{label}':x=18:y=13:fontsize=24:fontcolor=white"
        run(["ffmpeg", "-y", "-i", str(f), "-vf", vf, str(dest)], timeout=60)
        labelled_files.append(dest)
    return labelled_files


def make_sheet(files: list[Path], dest: Path, cols: int = 5, scale_w: int = 240) -> Path:
    if not files:
        raise RuntimeError("No images for sheet")
    list_file = dest.parent / f"{dest.stem}_inputs.txt"
    list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in files))
    rows = max(1, math.ceil(len(files) / cols))
    vf = f"scale={scale_w}:-1,tile={cols}x{rows}:padding=4:margin=4:color=white"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-vf", vf, "-frames:v", "1", str(dest)], timeout=120)
    return dest


def raw_rgb(path: Path, width: int = 160) -> tuple[int, int, bytes]:
    # Scale preserving aspect ratio, then emit raw RGB bytes for dependency-free scoring.
    p = run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={width}:-1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], timeout=60)
    w, h, _ = media_dims(path)
    scaled_h = max(1, round(h * width / w))
    return width, scaled_h, p.stdout


def image_metrics(path: Path) -> dict[str, float]:
    w, h, data = raw_rgb(path, width=160)
    n = max(1, len(data) // 3)
    lumas: list[float] = []
    sats: list[float] = []
    warm_sat = 0
    green_sat = 0
    too_dark = 0
    too_bright = 0
    for i in range(0, len(data), 3):
        r, g, b = data[i], data[i + 1], data[i + 2]
        mx, mn = max(r, g, b), min(r, g, b)
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        sat = 0.0 if mx == 0 else (mx - mn) / mx
        lumas.append(lum)
        sats.append(sat)
        if lum < 22:
            too_dark += 1
        if lum > 238:
            too_bright += 1
        if sat > 0.22 and r > g * 0.9 and r > b * 1.05:
            warm_sat += 1
        if sat > 0.18 and g > r * 0.85 and g > b * 1.05:
            green_sat += 1
    mean_l = statistics.fmean(lumas)
    contrast = statistics.pstdev(lumas) if len(lumas) > 1 else 0.0
    saturation = statistics.fmean(sats)
    # Simple focus/detail proxy: average neighbour luminance gradients.
    grad_sum = 0.0
    grad_n = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            idx = row + x
            if x + 1 < w:
                grad_sum += abs(lumas[idx] - lumas[idx + 1])
                grad_n += 1
            if y + 1 < h:
                grad_sum += abs(lumas[idx] - lumas[idx + w])
                grad_n += 1
    sharpness = grad_sum / max(1, grad_n)
    exposure_penalty = abs(mean_l - 132) / 132
    clipping = (too_dark + too_bright) / n
    botanical_signal = (warm_sat + green_sat) / n
    score = (
        sharpness * 1.35
        + contrast * 0.36
        + saturation * 52
        + botanical_signal * 70
        - exposure_penalty * 28
        - clipping * 45
    )
    return {
        "score": round(score, 4),
        "mean_luma": round(mean_l, 4),
        "contrast": round(contrast, 4),
        "saturation": round(saturation, 4),
        "sharpness": round(sharpness, 4),
        "botanical_signal": round(botanical_signal, 4),
        "clipping": round(clipping, 4),
    }


def choose_frame_heuristic(frames: list[Path], fps: float, duration: float) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for f in frames:
        label = f.stem.split("_")[-1]
        label_int = int(re.sub(r"\D", "", label) or "1")
        timestamp = max(0.0, (label_int - 1) / fps)
        m = image_metrics(f)
        # Avoid very first/last moments where Reel transitions/UI artifacts are common.
        edge_penalty = 6.0 if timestamp < 0.75 or (duration and timestamp > max(0, duration - 0.75)) else 0.0
        m["score"] = round(float(m["score"]) - edge_penalty, 4)
        scored.append({"label": label, "path": str(f), "timestamp_seconds": timestamp, "metrics": m})
    scored.sort(key=lambda x: x["metrics"]["score"], reverse=True)
    best = scored[0]
    return {
        "selection_mode": "ffmpeg_heuristic",
        "best_label": best["label"],
        "timestamp_seconds": best["timestamp_seconds"],
        "why": "Chosen by dependency-free frame scoring: focus/detail, healthy contrast, floral/botanical colour signal, balanced exposure, low clipping, and transition-edge penalty.",
        "metrics": best["metrics"],
        "runners_up": scored[1:6],
    }


def generate_crop_candidates(video: Path, timestamp: float, outdir: Path, target_w: int, target_h: int) -> list[dict[str, Any]]:
    w, h, _ = media_dims(video)
    cand_dir = outdir / "cover_candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for width_factor in (1.0, 0.92, 0.84, 0.76):
        crop_w = min(w, int(round(w * width_factor)))
        crop_h = min(h, int(round(crop_w * target_h / target_w)))
        if crop_h > h:
            crop_h = h
            crop_w = int(round(crop_h * target_w / target_h))
        max_x = max(0, w - crop_w)
        max_y = max(0, h - crop_h)
        xs = sorted({0, max_x, max(0, max_x // 2)}) if max_x else [0]
        ys = sorted({0, max_y, max(0, int(max_y * 0.22)), max(0, int(max_y * 0.40)), max(0, int(max_y * 0.58))}) if max_y else [0]
        for x in xs:
            for y in ys:
                key = (x, y, crop_w, crop_h)
                if key in seen:
                    continue
                seen.add(key)
                dest = cand_dir / f"cover_w{crop_w:04d}_x{x:04d}_y{y:04d}.jpg"
                vf = f"crop={crop_w}:{crop_h}:{x}:{y},scale={target_w}:{target_h}:flags=lanczos,eq=brightness=0.015:contrast=1.07:saturation=1.10:gamma=1.015,unsharp=5:5:0.55:3:3:0.2"
                run(["ffmpeg", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", "-vf", vf, "-q:v", "2", str(dest)], timeout=120)
                metrics = image_metrics(dest)
                # Prefer tighter editorial crops only when they score strongly; penalise excessive zoom a little.
                zoom_penalty = (1.0 - width_factor) * 8
                metrics["score"] = round(float(metrics["score"]) - zoom_penalty, 4)
                out.append({"path": str(dest), "x": x, "y": y, "w": crop_w, "h": crop_h, "width_factor": width_factor, "metrics": metrics})
    return out


def choose_crop_heuristic(candidates: list[dict[str, Any]], outdir: Path) -> dict[str, Any]:
    if not candidates:
        raise RuntimeError("No crop candidates generated")
    candidates = sorted(candidates, key=lambda c: c["metrics"]["score"], reverse=True)
    labelled = outdir / "crop_labeled"
    labelled.mkdir(parents=True, exist_ok=True)
    labelled_files: list[Path] = []
    for idx, c in enumerate(candidates[:12], 1):
        label = f"C{idx}"
        c["label"] = label
        dest = labelled / f"{label}_score{float(c['metrics']['score']):.1f}.jpg"
        vf = "drawbox=x=8:y=8:w=120:h=40:color=black@0.65:t=fill," + f"drawtext=text='{label}':x=18:y=14:fontsize=26:fontcolor=white"
        run(["ffmpeg", "-y", "-i", c["path"], "-vf", vf, str(dest)], timeout=60)
        c["labelled_path"] = str(dest)
        labelled_files.append(dest)
    sheet = make_sheet(labelled_files, outdir / "crop_candidates_sheet.jpg", cols=3, scale_w=270)
    best = candidates[0]
    best["crop_choice"] = {"selection_mode": "ffmpeg_heuristic", "best_label": best.get("label", "C1"), "why": "Highest crop score after focus/detail, botanical colour, exposure, clipping, and over-zoom penalty."}
    best["crop_sheet"] = str(sheet)
    best["runners_up"] = candidates[1:6]
    return best


def multipart_form(fields: dict[str, str], files: dict[str, Path]) -> tuple[bytes, str]:
    boundary = "----HermesReelCover" + str(int(time.time() * 1000))
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    for name, path in files.items():
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{path.name}\"\r\nContent-Type: {ctype}\r\n\r\n".encode()
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def openai_image_enhance(input_path: Path, output_path: Path, *, model: str, size: str) -> tuple[Path, str]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required because AI image enhancement is enabled by default")
    prompt = (
        "Enhance this Instagram Reel still into a premium Fig & Bloom feed cover. "
        + FIG_BLOOM_SOCIAL_FEED_RUBRIC
        + " Output must remain a 4:5 vertical cover; preserve the crop, bouquet, product, room, and all real subject geometry."
    )
    body, boundary = multipart_form(
        {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": os.environ.get("REEL_COVER_IMAGE_QUALITY", "high"),
            "n": "1",
        },
        {"image": input_path},
    )
    req = urllib.request.Request(
        OPENAI_IMAGES_EDIT_URL,
        data=body,
        method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:2000]
        raise RuntimeError(f"OpenAI image enhancement failed for model={model}: HTTP {e.code} {e.reason}. {body}") from e
    except Exception as e:
        raise RuntimeError(f"OpenAI image enhancement failed for model={model}: {e}") from e
    item = data["data"][0]
    if "b64_json" in item:
        output_path.write_bytes(base64.b64decode(item["b64_json"]))
    elif "url" in item:
        with urllib.request.urlopen(item["url"], timeout=300) as r:
            output_path.write_bytes(r.read())
    else:
        raise RuntimeError(f"OpenAI image response had no b64_json/url keys: {item.keys()}")
    return output_path, f"openai_image_edit:{model}"


def maybe_ai_finish(input_path: Path, output_path: Path, *, enabled: bool, model: str, size: str) -> tuple[Path, str]:
    if not enabled:
        return input_path, "ffmpeg_deterministic_enhancement_ai_disabled"
    # Custom command remains available for non-OpenAI backends, but OpenAI is the default.
    cmd_tmpl = os.environ.get("REEL_COVER_AI_EDIT_CMD")
    if cmd_tmpl:
        prompt = FIG_BLOOM_SOCIAL_FEED_RUBRIC
        cmd = cmd_tmpl.format(input=str(input_path), output=str(output_path), prompt=prompt)
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        if p.returncode or not output_path.exists():
            raise RuntimeError(f"AI edit command failed. STDERR={p.stderr[-1000:]}")
        return output_path, "external_ai_edit"
    return openai_image_enhance(input_path, output_path, model=model, size=size)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url", help="Instagram Reel URL")
    ap.add_argument("--outdir", default="/opt/data/tmp/instagram-reel-cover", help="Output working directory")
    ap.add_argument("--brand", default="fig-and-bloom")
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--cookies", help="Path to cookies.txt or browser name for yt-dlp --cookies-from-browser")
    ap.add_argument("--target-width", type=int, default=1080)
    ap.add_argument("--target-height", type=int, default=1350)
    ap.add_argument("--image-model", default=DEFAULT_IMAGE_MODEL, help="OpenAI image edit model; default REEL_COVER_IMAGE_MODEL or gpt-image-2")
    ap.add_argument("--image-size", default="1024x1536", help="OpenAI image output size closest to 4:5/vertical; final is normalized back to target size")
    ap.add_argument("--no-ai-enhance", action="store_true", help="Disable default AI image enhancement and return deterministic ffmpeg output")
    args = ap.parse_args()

    for c in ("uvx", "ffmpeg", "ffprobe"):
        need(c)

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    video = download_reel(args.url, outdir, args.cookies)
    w, h, duration = media_dims(video)
    frames = extract_frames(video, outdir, args.fps)
    labelled = label_frames(frames, outdir)
    sheet = make_sheet(labelled, outdir / "contact_sheet_labeled.jpg", cols=5, scale_w=240)

    frame_choice = choose_frame_heuristic(frames, args.fps, duration)
    timestamp = float(frame_choice["timestamp_seconds"])
    timestamp = max(0.0, min(duration, timestamp)) if duration else max(0.0, timestamp)

    candidates = generate_crop_candidates(video, timestamp, outdir, args.target_width, args.target_height)
    crop = choose_crop_heuristic(candidates, outdir)

    deterministic = outdir / "instagram_reel_cover_4x5_deterministic.jpg"
    shutil.copyfile(crop["path"], deterministic)
    ai_out = outdir / "instagram_reel_cover_4x5_ai.png"
    final_candidate, method = maybe_ai_finish(
        deterministic,
        ai_out,
        enabled=not args.no_ai_enhance,
        model=args.image_model,
        size=args.image_size,
    )

    # Always normalize the final deliverable back to exact 4:5 JPEG, regardless of image-editor output size.
    final_path = outdir / "instagram_reel_cover_4x5.jpg"
    run([
        "ffmpeg", "-y", "-i", str(final_candidate),
        "-vf", f"scale={args.target_width}:{args.target_height}:force_original_aspect_ratio=increase,crop={args.target_width}:{args.target_height},setsar=1",
        "-q:v", "2", str(final_path)
    ], timeout=120)

    final_w, final_h, _ = media_dims(final_path)
    if final_w * args.target_height != final_h * args.target_width:
        raise RuntimeError(f"Final output is not requested aspect ratio: {final_w}x{final_h}")

    report = {
        "url": args.url,
        "video": str(video),
        "source_width": w,
        "source_height": h,
        "duration_seconds": duration,
        "selection_mode": "ffmpeg_heuristic_no_gemini",
        "social_feed_rubric": FIG_BLOOM_SOCIAL_FEED_RUBRIC,
        "contact_sheet": str(sheet),
        "frame_choice": frame_choice,
        "selected_timestamp_seconds": timestamp,
        "crop": crop,
        "enhancement_method": method,
        "ai_enhance_enabled": not args.no_ai_enhance,
        "image_model": args.image_model if not args.no_ai_enhance else None,
        "deterministic_cover": str(deterministic),
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
