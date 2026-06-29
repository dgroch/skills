#!/usr/bin/env bash
# sample_clip_frames.sh — extract frames at a fixed interval across an animated clip so the
# Motion Critic (SKILL.md Step 9.5) can score rubric Dims 9 (camera/hands logic) and 11 (motion
# authenticity) on MULTI-FRAME evidence — never a single still.
#
# Usage:
#   scripts/sample_clip_frames.sh <clip.mp4> [interval_seconds] [out_dir]
#
# Defaults: interval 0.5s, out_dir /tmp/motion_frames/<clip_basename>/
#
# Output: <out_dir>/frame_0001.png, frame_0002.png, ... and prints each frame path on stdout
# (one per line) so the critic can iterate over them with vision_analyze.

set -euo pipefail

CLIP="${1:?usage: sample_clip_frames.sh <clip.mp4> [interval_seconds] [out_dir]}"
INTERVAL="${2:-0.5}"
BASENAME="$(basename "${CLIP%.*}")"
OUT_DIR="${3:-/tmp/motion_frames/${BASENAME}}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "error: ffmpeg not found on PATH" >&2
  exit 1
fi
if [ ! -f "$CLIP" ]; then
  echo "error: clip not found: $CLIP" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# fps = 1/interval. Guard against a zero/negative interval (fall back to 2 fps).
FPS="$(awk -v i="$INTERVAL" 'BEGIN { if (i+0 <= 0) { print "2" } else { printf "%.6f", 1.0/i } }')"

# -vsync vfr keeps exactly the sampled frames; -y overwrites a prior sample set.
ffmpeg -nostdin -loglevel error -y \
  -i "$CLIP" \
  -vf "fps=${FPS}" \
  -vsync vfr \
  "${OUT_DIR}/frame_%04d.png"

COUNT="$(find "$OUT_DIR" -maxdepth 1 -name 'frame_*.png' | wc -l | tr -d ' ')"
if [ "$COUNT" -eq 0 ]; then
  echo "error: no frames extracted from $CLIP" >&2
  exit 1
fi

echo "sampled ${COUNT} frame(s) from ${CLIP} every ${INTERVAL}s into ${OUT_DIR}" >&2
# Print the frame paths (sorted) on stdout for the Motion Critic to consume.
find "$OUT_DIR" -maxdepth 1 -name 'frame_*.png' | sort
