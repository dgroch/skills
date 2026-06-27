# ffmpeg Post-Production Patterns for Video Clones

## Per-Scene Captions from a Script (time-based `enable`)

When the user wants the voiceover script rendered as captions instead of audio
(no voiceover, just text), break the script into per-scene segments and use
ffmpeg's `enable` parameter with `between(t,start,end)` to display each caption
only during its scene. This is a SINGLE ffmpeg pass on the concatenated video.

### Example: 4 scenes × 5s each = 20s total

```bash
# Script:
# Scene 1 (0-5s):   "Me when I get flowers"
# Scene 2 (5-10s):  "Like, I literally cannot put them down"
# Scene 3 (10-15s): "Still holding them everywhere I go"
# Scene 4 (15-20s): "Honestly? Best gift ever"

ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='Me when I get flowers':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,0,5)',drawtext=text='Like, I literally cannot put them down':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,5,10)',drawtext=text='Still holding them everywhere I go':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,10,15)',drawtext=text='Honestly? Best gift ever':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,15,20)'" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

### Key technique

- Multiple `drawtext` filters chained with **commas** in a single `-vf`
- Each gets `enable='between(t,START,END)'` to time-gate it to its scene
- `t` is seconds from video start
- Use this when the user wants **script-as-captions** (no voiceover audio)
- In the audio mix step, skip the voiceover input — mix only ambient + music
- Same font, position, and border settings as single-caption burning

## Audio Mixing Without Voiceover

When producing script-as-captions (no voiceover), the audio mix simplifies to
two sources: native ambient + music. No padding needed:

```bash
ffmpeg -y \
  -i /tmp/clone_concat.mp4 \
  -i /tmp/sonilo_music.m4a \
  -filter_complex "[1:a]volume=0.20[music];[0:a]volume=0.3[ambient];[ambient][music]amix=inputs=2:duration=first:dropout_transition=0[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/clone_mixed.mp4
```

## Audio Mixing With Voiceover

Three sources: ambient + voiceover + music. Voiceover needs padding if shorter
than total video:

```bash
# Pad voiceover (e.g. 10.6s voiceover → 20s with silence)
ffmpeg -y -i /tmp/voiceover.mp3 -af "apad=pad_dur=10" -t 20 -c:a libmp3lame -b:a 128k /tmp/voiceover_padded.mp3

# Mix all three
ffmpeg -y \
  -i /tmp/clone_concat.mp4 \
  -i /tmp/voiceover_padded.mp3 \
  -i /tmp/sonilo_music.m4a \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.15[music];[0:a]volume=0.3[ambient];[voice][music][ambient]amix=inputs=3:duration=first:dropout_transition=0[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/clone_mixed.mp4
```

Volume levels (tuned from production):
- Voice: 1.0 — primary audio, must be clearly audible
- Music: 0.15 — background level, should not compete with voiceover
- Ambient: 0.3 — subtle ambience from native generation, adds realism

## Concatenation

```bash
cat > /tmp/concat_list.txt << 'EOF'
file '/tmp/scene1_video.mp4'
file '/tmp/scene2_video.mp4'
file '/tmp/scene3_video.mp4'
file '/tmp/scene4_video.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  /tmp/clone_concat.mp4
```

All scenes must have the same resolution. If not, add `-vf scale=720:1280`.

## Single-Caption Burning (same text throughout)

```bash
ffmpeg -y -i /tmp/clone_mixed.mp4 \
  -vf "drawtext=text='me when i get flowers':fontcolor=white:fontsize=48:x=30:y=h-th-80:borderw=3:bordercolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy \
  -c:v libx264 -preset fast -crf 23 \
  /tmp/clone_final.mp4
```

## Fonts

- DejaVu Sans Bold: `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`
- Noto Color Emoji: `/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`
- Emoji rendering in ffmpeg drawtext can be unreliable — use PNG overlay for complex emoji

## Position Guide for 9:16 (720x1280)

- Lower-left (common TikTok style): `x=30:y=h-th-80`
- Bottom center: `x=(w-text_w)/2:y=h-th-60`
- Upper center: `x=(w-text_w)/2:y=60`