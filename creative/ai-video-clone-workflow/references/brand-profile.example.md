# Brand Profile — Fig & Bloom (worked example)

This is the example profile the skill ships with. Copy it, swap the values, and the clone
pipeline runs unmodified for another brand (see SKILL.md → Brand Profile).

**Required minimum to run:** source video URL/handle + a product/asset reference source + a logo
+ voice rules. Everything else has defaults.

```yaml
brand:
  name: "Fig & Bloom"
  voice:
    language: en-AU
    banned_words: [luxury, elevate, curate, curated, stunning, gorgeous, "blooms(noun)"]
    rules:
      - "no exclamation marks"
      - "no em-dashes"
      - "the free card is a 'gold-foiled greeting card', never 'handwritten'"
    tone: "warm, considered, plain"
  product_reference:
    source: "shopify_products_json"        # https://figandbloom.com/products.json?limit=50
    pick_rule: "choose a clean, true-colour shot (neutral/light-grey studio bg) that shows the
                wrap, printed wordmark and ribbon clearly — never a warm/pink-cast shot (R1)"
  talent:
    mode: "casting_matrix"                 # or fixed_reference for a spokesmodel
    casting_matrix:
      groups:
        - "Caucasian women (blonde or brunette)"
        - "Asian (East/Southeast Asian)"
        - "Sub-continental (South Asian)"
        - "African (Sudanese/Somali/Nigerian features, NOT African-American)"
      default: "women (gifting-recipient demographic)"
      rotate: true                         # diversify across the content library
    fixed_reference_id: null
    flaws_required: true                   # GLOBAL: actor flaws on; image degradation off (R2)
  visual_identity:
    palette: ["#14110F", "#FFFFFF", "#D8CCBE"]   # Clay = #D8CCBE
    logo_lockup: "<asset path/url to stacked logo>"
    end_card: "For Moment Makers — stacked logo on Clay, restrained, no hard sell"
  caption:
    default_style: "B"                     # Style B (Typewriter) is the F&B-preferred style
    original_copy_required: true           # R7 — original copy in F&B voice, never a lift
  music:
    source: "epidemic_sound_mcp"           # licensed only; never sonilo_music for final (R8)
  format:
    aspect: "9:16"
    beat_durations: "match source pacing"
    total_target_s: 15
  delivery:
    host: "public_url"                     # media_upload → CloudFront, or brand CDN
    variants: ["captioned", "clean_no_caption", "1:1", "4:5"]
  run:
    one_shot: false                        # true skips the human storyboard checkpoint if gates pass
```

## Notes specific to Fig & Bloom
- **Bouquet is wrapped, not in a glass vase** — keep this as a **negative** constraint (R1); do
  NOT re-describe the wrap, ribbon, or wordmark — seed them from a clean reference image.
- **Wordmark** "Fig & Bloom" must be legible — route to `gpt_image_2` (R5); near-exact is
  acceptable, composite the real product for an exact hero still.
- **Key products (June 2026):** Osaka ($129), Marseille ($145), Broome ($127), Lucerne ($109),
  Genoa ($119), Pyrenees ($119), Monaco Pink ($79), Monaco White ($79).
- **Voice:** AU English, no exclamation marks, no em-dashes; avoid the banned words and "blooms"
  as a noun; the free card is a "gold-foiled greeting card."
- **Close:** "For Moment Makers" stacked-logo end card on Clay `#D8CCBE`.
- **Music:** Epidemic Sound MCP; if not configured, deliver `-an` and let the user add licensed
  audio downstream — never ship `sonilo_music` as final.
- **Australian voiceover:** ElevenLabs AU voices (Arabella, Emma, Sophia; Charlie, Logan) — see
  SKILL.md Step 9 Audio Strategy B.
