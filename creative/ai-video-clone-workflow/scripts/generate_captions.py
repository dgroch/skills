#!/usr/bin/env python3
"""Generate caption PNG overlays for video clones.

Three approved styles (Instagram Stories aesthetic, approved by Daniel June 2026):
  A = Modern Dark   — white text on opaque dark rounded rectangle
  B = Typewriter    — black text on opaque white rounded rectangle
  C = Classic Meme  — white text with dark outline, no box

All styles: centered horizontally, lower-third position (~72% from top),
28-32px DejaVu Sans Bold, 12px corner radius, 24px horizontal / 14px vertical padding.

Usage:
  uvx --from pillow python3 scripts/generate_captions.py \
    --style B \
    --captions "Me when I get flowers|Like, I literally cannot put them down|Still holding them everywhere I go|Honestly? Best gift ever"

Outputs: /tmp/caption_scene1.png, /tmp/caption_scene2.png, etc.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# Frame dimensions (9:16)
W, H = 720, 1280

# Font
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 28

# Layout
BOX_PADDING_X = 24
BOX_PADDING_Y = 14
BOX_RADIUS = 12
MAX_BOX_WIDTH = int(W * 0.80)  # Never exceed 80% of frame width
Y_POSITION = int(H * 0.72)    # Lower third (~72% from top)

# Style presets
STYLES = {
    "A": {  # Modern Dark
        "box_color": (18, 18, 18, 255),    # Fully opaque near-black
        "text_color": (255, 255, 255, 255), # White
        "name": "Instagram Modern Dark",
    },
    "B": {  # Typewriter
        "box_color": (255, 255, 255, 255), # Fully opaque white
        "text_color": (0, 0, 0, 255),      # Black
        "name": "Instagram Typewriter",
    },
    "C": {  # Classic Meme — no box, text with outline only
        "box_color": None,                  # No background box
        "text_color": (255, 255, 255, 255), # White
        "outline_color": (0, 0, 0, 200),   # Semi-opaque dark outline
        "outline_width": 3,
        "name": "Classic Meme",
    },
}


def render_caption(text, style_key):
    """Render a single caption as a transparent RGBA PNG."""
    style = STYLES[style_key]
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Determine if wrapping is needed (Style C uses larger font)
    effective_font_size = FONT_SIZE + 4 if style_key == "C" else FONT_SIZE
    if style_key == "C":
        font = ImageFont.truetype(FONT_PATH, effective_font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

    use_wrapping = text_w + BOX_PADDING_X * 2 > MAX_BOX_WIDTH
    if use_wrapping:
        words = text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        bbox1 = draw.textbbox((0, 0), line1, font=font)
        bbox2 = draw.textbbox((0, 0), line2, font=font)
        text_w = max(bbox1[2] - bbox1[0], bbox2[2] - bbox2[0])
        text_h = (bbox1[3] - bbox1[1]) + (bbox2[3] - bbox2[1]) + 8
        box_w = text_w + BOX_PADDING_X * 2
        box_h = text_h + BOX_PADDING_Y * 2
    else:
        line1 = text
        line2 = None
        box_w = text_w + BOX_PADDING_X * 2
        box_h = text_h + BOX_PADDING_Y * 2

    box_x = (W - box_w) // 2
    box_y = Y_POSITION

    if style["box_color"] is not None:
        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=BOX_RADIUS,
            fill=style["box_color"],
        )

    def draw_text(text_str, tx, ty):
        if style_key == "C":
            draw.text((tx, ty), text_str, fill=style["text_color"], font=font,
                       stroke_width=style.get("outline_width", 3),
                       stroke_fill=style.get("outline_color", (0, 0, 0, 200)))
        else:
            draw.text((tx, ty), text_str, fill=style["text_color"], font=font)

    if use_wrapping:
        bbox1 = draw.textbbox((0, 0), line1, font=font)
        bbox2 = draw.textbbox((0, 0), line2, font=font)
        line1_w = bbox1[2] - bbox1[0]
        line2_w = bbox2[2] - bbox2[0]
        line_h = bbox1[3] - bbox1[1]
        draw_text(line1, box_x + (box_w - line1_w) // 2, box_y + BOX_PADDING_Y)
        draw_text(line2, box_x + (box_w - line2_w) // 2, box_y + BOX_PADDING_Y + line_h + 8)
    else:
        draw_text(text, box_x + (box_w - text_w) // 2, box_y + BOX_PADDING_Y)

    return img


def main():
    parser = argparse.ArgumentParser(description="Generate caption PNG overlays for video clones")
    parser.add_argument("--style", choices=["A", "B", "C"], default="B",
                        help="Caption style: A=Modern Dark, B=Typewriter (default), C=Classic Meme")
    parser.add_argument("--captions", required=True,
                        help="Pipe-separated caption strings (one per scene)")
    parser.add_argument("--outdir", default="/tmp",
                        help="Output directory (default: /tmp)")
    args = parser.parse_args()

    caption_list = args.captions.split("|")
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    for i, text in enumerate(caption_list, 1):
        img = render_caption(text.strip(), args.style)
        out_path = os.path.join(args.outdir, f"caption_scene{i}.png")
        img.save(out_path)
        print(f"Scene {i}: '{text.strip()}' -> {out_path} ({os.path.getsize(out_path)} bytes)")

    print(f"\nStyle: {STYLES[args.style]['name']}")
    print(f"Generated {len(caption_list)} caption PNGs in {args.outdir}")


if __name__ == "__main__":
    main()