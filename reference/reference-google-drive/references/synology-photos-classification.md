# Synology Photos Shared Drive — Classification & Organization

## Drive Details
- **Name:** Synology Photos
- **Drive ID:** `0AOMVrKhhWKIwUk9PVA`
- **Purpose:** Product photography, UGC, brand assets, ad campaign materials, camera backups

## Root Folder Map (as of May 2026)

| Folder | Classification | Notes |
|---|---|---|
| Products | Products | Existing — primary product photography |
| PhotoLibrary | Products | Deep subfolder tree by product |
| Generated Lifestyle Images | Lifestyle | AI/studio lifestyle shots |
| Generated Lifestyle Video | Video | Video versions of lifestyle |
| Banner Ads | Graphics | Display ad creatives |
| Backgrounds | Graphics | Product backdrop images |
| Ai Backdrops | Graphics | AI-generated backgrounds |
| Illustrations | Graphics | Design/illustration assets |
| Advertising | Graphics | Campaign ad assets |
| NLC \| Best Sellers - Google PMAX | Graphics | PMax campaign statics |
| NLC \| Review Meta Ads | Graphics | Meta ad campaign assets |
| NLC \| WOW Giveaway Statics | Graphics | Giveaway campaign assets |
| UGC Images | UGC | Hashgifted / influencer photos |
| UGC Videos | UGC | Hashgifted / influencer videos |
| Tagbox | UGC | Social proof aggregation |
| Logos | Brand Assets | Brand logo files |

### Folders to skip (archives / raw backups — do not move)
- **Photos** — camera roll / RAW backup (~6,000 files)
- **Right Hook Digital** — agency deliverable archive (~2,000 files)
- **Events** — event photography backup
- **AI Talent** — AI-generated talent images
- **Behind the Scenes** — BTS content archive
- **Social Media** — posted content archive
- **Website** — website asset dump
- **Music** — audio files
- **Content by Monthly Theme** — editorial calendar archive

## Classification Rules

1. **Root folder match** → use FOLDER_CLASSIFICATION map above
2. **Video extension override** (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.mpeg`) → always classify as `Video` regardless of source folder
3. **Skip folders** → leave in place, do not move
4. **Unmatched roots** → skip (safety: don't move what you can't classify)

## Target Structure After Organization

```
Synology Photos (drive root)
├── Products/          ← product photography
├── Lifestyle/         ← generated lifestyle images
├── Video/             ← all video content
├── Graphics/          ← ads, banners, backgrounds, illustrations
├── UGC/               ← user-generated content
├── Brand Assets/      ← logos, brand guidelines
└── [skipped folders remain in place]
```

## File Counts (May 2026 baseline)

- Total drive items: ~15,700
- Classifiable for move: ~5,041
- Skipped archives: ~9,200
- Products: 1,890 | Graphics: 1,600 | Video: 797 | UGC: 679 | Lifestyle: 68 | Brand Assets: 7
