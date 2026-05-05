#!/usr/bin/env python3
"""
Florist Review Intelligence — stdlib CLI pipeline
Handles: query seeding, URL harvesting, deduplication, analysis, CSV export, Notion sync.

Usage:
    python3 review_intel_pipeline.py seed-queries --config ../templates/config.example.json --out queries.txt
    python3 review_intel_pipeline.py harvest-url --brand "Daily Blooms" --market Melbourne --source Google --url "https://..." --out data/raw/2026-01-01.jsonl
    python3 review_intel_pipeline.py analyse --in data/raw/2026-01-01.jsonl --out data/analysed/2026-01-01.jsonl --report reports/2026-01-01.md
    python3 review_intel_pipeline.py sync-notion --in data/analysed/2026-01-01.jsonl
    python3 review_intel_pipeline.py dedupe --in data/raw/2026-01-01.jsonl --out data/deduped/2026-01-01.jsonl
    python3 review_intel_pipeline.py export-csv --in data/analysed/2026-01-01.jsonl --out exports/2026-01-01.csv
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_FLORIST_DATABASE_ID = os.getenv("NOTION_FLORIST_REVIEW_DATABASE_ID", "")
NOTION_FLORIST_DATA_SOURCE_ID = os.getenv("NOTION_FLORIST_REVIEW_DATA_SOURCE_ID", "")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_jsonl(path: str):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def save_jsonl(records, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def notion_post(endpoint: str, payload: dict) -> dict:
    if not NOTION_API_KEY:
        raise SystemExit("NOTION_API_KEY not set.")
    url = f"https://api.notion.com/v1/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers=NOTION_HEADERS, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def notion_patch(endpoint: str, payload: dict) -> dict:
    if not NOTION_API_KEY:
        raise SystemExit("NOTION_API_KEY not set.")
    url = f"https://api.notion.com/v1/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers=NOTION_HEADERS, method="PATCH"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def notion_get(endpoint: str) -> dict:
    if not NOTION_API_KEY:
        raise SystemExit("NOTION_API_KEY not set.")
    url = f"https://api.notion.com/v1/{endpoint}"
    req = urllib.request.Request(url, headers=NOTION_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Command: seed-queries
# ---------------------------------------------------------------------------

def cmd_seed_queries(args):
    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)

    brands = {b["name"]: b for b in config["brands"]}
    markets = config.get("markets", ["Melbourne", "Sydney", "Brisbane"])
    templates = config.get("query_templates", [])

    seen = set()
    lines = []

    for brand_cfg in config["brands"]:
        name = brand_cfg["name"]
        aliases = brand_cfg.get("aliases", [name])
        for market in markets:
            for tpl in templates:
                for alias in aliases:
                    q = tpl.replace("{brand}", alias).replace("{market}", market)
                    if q not in seen:
                        seen.add(q)
                        lines.append(q)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} queries to {args.out}")


# ---------------------------------------------------------------------------
# Command: harvest-url
# ---------------------------------------------------------------------------

def extract_reviews_from_url(url: str, brand: str, market: str, source: str) -> list[dict]:
    """
    Attempt to fetch and extract review records from a URL.
    Falls back to recording the URL as a pending/manual-capture record.
    """
    records = []
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; FloristReviewBot/1.0; "
                    "+https://figandbloom.com.au/bot)"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/json" not in content_type:
                # Not a parseable page; record as blocked source
                return [
                    {
                        "id": stable_id(url),
                        "brand": brand,
                        "market": market,
                        "source": source,
                        "source_url": url,
                        "review_url": None,
                        "reviewer": None,
                        "rating": None,
                        "review_date": None,
                        "collected_at": now_iso(),
                        "text": "",
                        "language": "en",
                        "status": "blocked_source",
                        "reason": f"Non-HTML content-type: {content_type}",
                    }
                ]
            html = resp.read().decode("utf-8", errors="replace")
            records = _parse_html_reviews(html, url, brand, market, source)
    except urllib.error.HTTPError as e:
        records = [
            {
                "id": stable_id(url),
                "brand": brand,
                "market": market,
                "source": source,
                "source_url": url,
                "review_url": None,
                "reviewer": None,
                "rating": None,
                "review_date": None,
                "collected_at": now_iso(),
                "text": "",
                "language": "en",
                "status": "blocked_source",
                "reason": f"HTTP {e.code}: {e.reason}",
            }
        ]
    except Exception as e:
        records = [
            {
                "id": stable_id(url),
                "brand": brand,
                "market": market,
                "source": source,
                "source_url": url,
                "review_url": None,
                "reviewer": None,
                "rating": None,
                "review_date": None,
                "collected_at": now_iso(),
                "text": "",
                "language": "en",
                "status": "blocked_source",
                "reason": f"Error: {e}",
            }
        ]

    # Always add a record even on success (may be 0 extracted reviews + 1 blocked)
    if not records:
        records.append(
            {
                "id": stable_id(url),
                "brand": brand,
                "market": market,
                "source": source,
                "source_url": url,
                "review_url": None,
                "reviewer": None,
                "rating": None,
                "review_date": None,
                "collected_at": now_iso(),
                "text": "",
                "language": "en",
                "status": "blocked_source",
                "reason": "No content extracted",
            }
        )
    return records


def _parse_html_reviews(html: str, url: str, brand: str, market: str, source: str) -> list[dict]:
    """
    Lightweight heuristic extraction from HTML.
    Looks for common review markup patterns: JSON-LD structured data,
    microdata, and plain-text paragraph blocks near rating indicators.
    """
    records = []

    # 1. Try JSON-LD structured data (Google/Schema.org Review / ProductReview)
    json_ld_pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in json_ld_pattern.finditer(html):
        try:
            data = json.loads(m.group(1))
            # Normalize to a list
            if isinstance(data, dict):
                data = [data]
            for item in data:
                @item_type = item.get("@type", "")
                if "Review" not in item_type and "ReviewAggregateRating" not in item_type:
                    continue
                review_body = (
                    item.get("reviewBody") or item.get("description") or ""
                ).strip()
                if not review_body:
                    continue
                rating_val = None
                if "reviewRating" in item:
                    rr = item["reviewRating"]
                    rating_val = float(rr.get("ratingValue", 0)) or None
                author = (
                    item.get("author", {})
                    if isinstance(item.get("author"), dict)
                    else item.get("author", None)
                )
                author_name = author.get("name") if isinstance(author, dict) else author
                date_published = item.get("datePublished") or None
                records.append(
                    {
                        "id": stable_id(f"{url}|{review_body[:80]}"),
                        "brand": brand,
                        "market": market,
                        "source": source,
                        "source_url": url,
                        "review_url": url,
                        "reviewer": author_name,
                        "rating": rating_val,
                        "review_date": date_published,
                        "collected_at": now_iso(),
                        "title": item.get("name") or None,
                        "text": review_body,
                        "language": "en",
                        "status": "new",
                    }
                )
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Heuristic: Google star patterns like aria-label="5 stars"
    star_pattern = re.compile(
        r'aria-label=["\'](\d+(?:\.\d+)?)\s*stars?["\'][^>]*>([^<]{5,500}?)<',
        re.IGNORECASE,
    )
    for m in star_pattern.finditer(html):
        rating_val = float(m.group(1))
        snippet = m.group(2).strip()
        snippet = re.sub(r"<[^>]+>", " ", snippet).strip()
        if len(snippet) < 10:
            continue
        # Avoid duplicates with JSON-LD already found
        sid = stable_id(f"{url}|{snippet[:80]}")
        if any(r["id"] == sid for r in records):
            continue
        records.append(
            {
                "id": sid,
                "brand": brand,
                "market": market,
                "source": source,
                "source_url": url,
                "review_url": url,
                "reviewer": None,
                "rating": rating_val,
                "review_date": None,
                "collected_at": now_iso(),
                "title": None,
                "text": snippet,
                "language": "en",
                "status": "new",
            }
        )

    return records


def cmd_harvest_url(args):
    records = extract_reviews_from_url(
        url=args.url,
        brand=args.brand,
        market=args.market,
        source=args.source,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(records, args.out)
    new = sum(1 for r in records if r.get("status") == "new")
    blocked = sum(1 for r in records if r.get("status") == "blocked_source")
    print(f"Saved {len(records)} records to {args.out}  (new={new}, blocked={blocked})")


# ---------------------------------------------------------------------------
# Command: dedupe
# ---------------------------------------------------------------------------

def cmd_dedupe(args):
    """
    Deduplicate JSONL by (source_url OR review_url) + (reviewer OR text[:80]).
    Keeps the first occurrence; records secondary occurrences as duplicates.
    """
    records = load_jsonl(args.in_) if Path(args.in_).exists() else []
    seen_keys = {}
    unique, duplicates = [], []

    for r in records:
        url = r.get("review_url") or r.get("source_url") or ""
        reviewer = r.get("reviewer") or ""
        text_key = r.get("text", "")[:80]
        key = f"{url}|{reviewer}|{text_key}"
        if key not in seen_keys:
            seen_keys[key] = True
            unique.append(r)
        else:
            r["status"] = "duplicate"
            duplicates.append(r)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(unique, args.out)
    dup_path = args.out.replace(".jsonl", "-duplicates.jsonl")
    save_jsonl(duplicates, dup_path)
    print(
        f"Deduped: {len(unique)} unique, {len(duplicates)} duplicates "
        f"(saved to {args.out}, {dup_path})"
    )


# ---------------------------------------------------------------------------
# Command: analyse
# ---------------------------------------------------------------------------

POSITIVE_PATTERNS = [
    r"beautiful", r"stunning", r"amazing", r"love[sd]?", r"perfect",
    r"fresh", r"gorgeous", r"exactly like", r"looked like the photo",
    r"best florist", r"recommend", r"made her day", r"made my day",
    r"arrived on time", r"prompt", r"helpful", r"friendly", r"reliable",
    r"premium", r"elegant", r"high quality", r"exceeded expectations",
    r"fresh for", r"lasted well", r"wow", r"wowed",
]

NEGATIVE_PATTERNS = [
    r"late", r"never arrived", r"not delivered", r"missing",
    r"wrong", r"incorrect", r"damaged", r"poor quality", r"not fresh",
    r"wilted", r"didn'?t match", r"not like the photo", r"smaller than",
    r"disappointed", r"expensive", r"overpriced", r"refund",
    r"no one answered", r"couldn'?t reach", r"unhelpful", r"rude",
    r"unreliable", r"never again", r"worst", r"terrible", r"awful",
    r"embarrassing", r"waste of money", r"complaint", r"complained",
]

DELIVERY_KEYWORDS = [
    "late", "on time", "delayed", "next day", "same day",
    "delivered", "delivery", "arrived", "courier", "driver",
    "missed", "wrong address", "left at door",
]

QUALITY_KEYWORDS = [
    "fresh", "wilted", "damaged", "bruised", "poor quality",
    "not fresh", "beautiful", "stunning", "gorgeous", "photo match",
    "looked like", "exactly like", "fresh for",
]

SERVICE_KEYWORDS = [
    "helpful", "friendly", "unhelpful", "rude", "no answer",
    "couldn't reach", "phone", "email", "response", "customer service",
    "refund", "exchange", "replacement", "complaint",
]

VALUE_KEYWORDS = [
    "expensive", "overpriced", "cheap", "value", "price", "worth",
    "for the price", "money", "affordable", "budget",
]


def analyse_record(record: dict) -> dict:
    """Heuristic analysis of a single review record. Mutates and returns it."""
    text = (record.get("text") or "").lower()
    title = (record.get("title") or "").lower()
    combined = f"{title} {text}"

    rating = record.get("rating")
    sentiment = "unknown"
    if rating is not None:
        if rating >= 4.0:
            sentiment = "positive"
        elif rating <= 2.0:
            sentiment = "negative"
        else:
            sentiment = "mixed"

    # Override with pattern detection
    pos_count = sum(len(re.findall(p, combined)) for p in POSITIVE_PATTERNS)
    neg_count = sum(len(re.findall(p, combined)) for p in NEGATIVE_PATTERNS)
    if pos_count > neg_count * 1.5:
        sentiment = "positive"
    elif neg_count > pos_count * 1.5:
        sentiment = "negative"
    elif pos_count and neg_count:
        sentiment = "mixed"

    # Themes
    themes = []
    if any(k in combined for k in DELIVERY_KEYWORDS):
        themes.append("delivery_speed")
    if any(k in combined for k in QUALITY_KEYWORDS):
        themes.append("product_quality")
    if any(k in combined for k in SERVICE_KEYWORDS):
        themes.append("customer_service")
    if any(k in combined for k in VALUE_KEYWORDS):
        themes.append("value_price")
    if not themes:
        themes.append("general")

    # Complaints / Delight drivers
    complaints = []
    delight_drivers = []
    if sentiment in ("negative", "mixed"):
        for p in NEGATIVE_PATTERNS:
            for m in re.finditer(p, combined):
                phrase = text[max(0, m.start() - 20) : m.end() + 20].strip()
                phrase = re.sub(r"\s+", " ", phrase)
                if phrase not in complaints and len(phrase) > 5:
                    complaints.append(phrase)
    if sentiment in ("positive", "mixed"):
        for p in POSITIVE_PATTERNS:
            for m in re.finditer(p, combined):
                phrase = text[max(0, m.start() - 20) : m.end() + 20].strip()
                phrase = re.sub(r"\s+", " ", phrase)
                if phrase not in delight_drivers and len(phrase) > 5:
                    delight_drivers.append(phrase)

    # Customer phrases (short, punchy snippets)
    customer_phrases = []
    for p in POSITIVE_PATTERNS + NEGATIVE_PATTERNS:
        for m in re.finditer(p, combined):
            phrase = text[m.start() : m.end() + 60].strip()
            phrase = re.sub(r"\s+", " ", phrase)
            sentence_end = max(phrase.find("."), phrase.find("!"), phrase.find("?"))
            if sentence_end > 5:
                phrase = phrase[: sentence_end + 1]
            if phrase not in customer_phrases and len(phrase) > 10:
                customer_phrases.append(phrase)

    # Operational issue
    operational_issue = "none"
    if any(k in combined for k in ["late", "delayed", "never arrived", "not delivered", "missed"]):
        operational_issue = "delivery"
    elif any(k in combined for k in ["not fresh", "wilted", "damaged", "poor quality"]):
        operational_issue = "quality"
    elif any(k in combined for k in ["refund", "exchange", "replacement", "complaint"]):
        operational_issue = "refund"
    elif any(k in combined for k in ["unhelpful", "no answer", "couldn't reach", "rude"]):
        operational_issue = "communication"
    elif any(k in combined for k in ["website", "checkout", "order"]):
        operational_issue = "website"

    # Emotion words
    emotion_words = []
    for p in POSITIVE_PATTERNS + NEGATIVE_PATTERNS:
        for m in re.finditer(p, combined):
            w = m.group(0)
            if w not in emotion_words:
                emotion_words.append(w)

    # Purchase drivers (heuristic — pick up keywords from positive records)
    purchase_drivers = []
    driver_map = {
        "same-day delivery": ["same day", "last minute", "urgent"],
        "beautiful design": ["beautiful", "stunning", "gorgeous", "elegant"],
        "photo accuracy": ["photo", "looked like", "exactly like", "matched"],
        "freshness": ["fresh", "fresh for", "lasted"],
        "gift reaction": ["made her day", "made my day", "reaction", "surprised"],
        "ease of order": ["easy", "simple", "website", "order"],
        "price value": ["price", "value", "worth", "affordable"],
    }
    for driver, keywords in driver_map.items():
        if any(k in combined for k in keywords):
            purchase_drivers.append(driver)

    # JTBD
    jtbd = "unknown"
    if any(k in combined for k in ["birthday", "b-day"]):
        jtbd = "birthday"
    elif any(k in combined for k in ["sympathy", "funeral", "condolence", "passed away"]):
        jtbd = "sympathy"
    elif any(k in combined for k in ["romantic", "anniversary", "valentine", "love"]):
        jtbd = "romance"
    elif any(k in combined for k in ["apolog", "sorry", "make up"]):
        jtbd = "apology"
    elif any(k in combined for k in ["corporate", "business", "office", "work"]):
        jtbd = "corporate"
    elif any(k in combined for k in ["same day", "last minute", "urgent"]):
        jtbd = "same_day"
    elif any(k in combined for k in ["mother", "mum", "moms"]):
        jtbd = "mother_appreciation"

    record["sentiment"] = sentiment
    record["themes"] = list(set(themes))
    record["complaints"] = complaints[:8]
    record["delight_drivers"] = delight_drivers[:8]
    record["purchase_drivers"] = list(set(purchase_drivers))
    record["customer_phrases"] = customer_phrases[:6]
    record["emotion_words"] = emotion_words[:12]
    record["job_to_be_done"] = jtbd
    record["operational_issue"] = operational_issue
    record["competitor_opportunity"] = None
    record["confidence"] = round(min(0.3 + (len(text) / 500) * 0.3, 0.85), 2)
    record["status"] = "analysed"
    return record


def write_summary(records: list[dict], report_path: str):
    brands = {}
    for r in records:
        brands.setdefault(r.get("brand", "Unknown"), []).append(r)

    lines = [
        f"# Florist Review Intelligence — {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Coverage",
        f"- Total reviews: {len(records)}",
        f"- Sources: {', '.join(sorted(set(r.get('source','') for r in records)))}",
        f"- Markets: {', '.join(sorted(set(r.get('market','') for r in records)))}",
        "",
        "## Executive Takeaways",
        "",
    ]

    for brand, recs in sorted(brands.items()):
        pos = [r for r in recs if r.get("sentiment") == "positive"]
        neg = [r for r in recs if r.get("sentiment") == "negative"]
        mixed = [r for r in recs if r.get("sentiment") == "mixed"]
        lines.append(f"## Brand: {brand}")
        lines.append(f"- Total: {len(recs)}  |  Positive: {len(pos)}  |  Mixed: {len(mixed)}  |  Negative: {len(neg)}")
        lines.append("")

        # Top complaints
        all_complaints = []
        for r in recs:
            all_complaints.extend(r.get("complaints", []))
        if all_complaints:
            lines.append("### Top Complaints")
            for c in all_complaints[:6]:
                lines.append(f"- {c}")
            lines.append("")

        # Top delights
        all_delights = []
        for r in recs:
            all_delights.extend(r.get("delight_drivers", []))
        if all_delights:
            lines.append("### Top Delight Drivers")
            for d in all_delights[:6]:
                lines.append(f"- {d}")
            lines.append("")

        # Language bank
        all_phrases = []
        for r in recs:
            all_phrases.extend(r.get("customer_phrases", []))
        if all_phrases:
            lines.append("### Customer Language")
            for ph in all_phrases[:8]:
                lines.append(f"- \"{ph}\"")
            lines.append("")

        # Purchase drivers
        all_drivers = []
        for r in recs:
            all_drivers.extend(r.get("purchase_drivers", []))
        if all_drivers:
            driver_counts = {d: all_drivers.count(d) for d in set(all_drivers)}
            lines.append("### Purchase Drivers")
            for d, cnt in sorted(driver_counts.items(), key=lambda x: -x[1]):
                lines.append(f"- {d} ({cnt})")
            lines.append("")

        # Operational issues
        issues = [r.get("operational_issue") for r in recs if r.get("operational_issue") != "none"]
        if issues:
            issue_counts = {i: issues.count(i) for i in set(issues)}
            lines.append("### Operational Issues")
            for iss, cnt in sorted(issue_counts.items(), key=lambda x: -x[1]):
                lines.append(f"- {iss}: {cnt}")
            lines.append("")

    lines.append("## Cross-category Language Bank")
    all_phrases = []
    for r in records:
        all_phrases.extend(r.get("customer_phrases", []))
    for ph in list(dict.fromkeys(all_phrases))[:15]:
        lines.append(f"- \"{ph}\"")

    lines.append("")
    lines.append("## Next Crawl Targets")
    lines.append("- Expand to additional suburbs per city")
    lines.append("- Check Google Business profiles for each brand × city combination")
    lines.append("- Explore ProductReview.com.au comment threads")

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def cmd_analyse(args):
    records = load_jsonl(args.in_) if Path(args.in_).exists() else []
    analysed = []
    for r in records:
        if r.get("status") in ("blocked_source", "duplicate"):
            analysed.append(r)
        else:
            analysed.append(analyse_record(r.copy()))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(analysed, args.out)

    if args.report:
        write_summary(analysed, args.report)

    sentiment_counts = {}
    for r in analysed:
        s = r.get("sentiment", "unknown")
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
    print(
        f"Analysed {len(analysed)} records → {args.out}"
        f"  (sentiment: {sentiment_counts})"
    )
    if args.report:
        print(f"Summary written to {args.report}")


# ---------------------------------------------------------------------------
# Command: export-csv
# ---------------------------------------------------------------------------

CSV_COLS = [
    "id", "brand", "market", "source", "source_url", "reviewer", "rating",
    "review_date", "collected_at", "sentiment", "themes", "complaints",
    "delight_drivers", "purchase_drivers", "customer_phrases",
    "job_to_be_done", "operational_issue", "confidence", "status", "text",
]


def cmd_export_csv(args):
    records = load_jsonl(args.in_) if Path(args.in_).exists() else []
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = {k: (", ".join(v) if isinstance(v, list) else v) for k, v in r.items()}
            writer.writerow(row)
    print(f"Exported {len(records)} rows to {args.out}")


# ---------------------------------------------------------------------------
# Command: sync-notion
# ---------------------------------------------------------------------------

NOTION_DB_PROPS = {
    "Name": "title",
    "Brand": "brand",
    "Market": "market",
    "Source": "source",
    "Source URL": "source_url",
    "Review URL": "review_url",
    "Rating": "rating",
    "Review Date": "review_date",
    "Collected At": "collected_at",
    "Sentiment": "sentiment",
    "Themes": "themes",
    "Complaints": "complaints",
    "Delight Drivers": "delight_drivers",
    "Purchase Drivers": "purchase_drivers",
    "Customer Phrases": "customer_phrases",
    "Job To Be Done": "job_to_be_done",
    "Operational Issue": "operational_issue",
    "Opportunity": "competitor_opportunity",
    "Raw Text": "text",
    "Local ID": "id",
    "Status": "status",
}


def notion_property_type(key: str, value) -> dict:
    if value is None:
        return {"rich_text": [{"text": {"content": ""}}]}
    if isinstance(value, bool):
        return {"checkbox": value}
    if isinstance(value, (int, float)):
        return {"number": float(value)}
    if isinstance(value, list):
        return {"multi_select": [{"name": str(v)} for v in value]}
    return {"rich_text": [{"text": {"content": str(value)}}]}


def create_notion_page(record: dict) -> Optional[str]:
    if not NOTION_FLORIST_DATABASE_ID:
        print("  NOTION_FLORIST_REVIEW_DATABASE_ID not set — skipping Notion sync")
        return None

    title = f"{record.get('brand','?')} · {record.get('source','?')} · {str(record.get('title') or record.get('text','')[:50])[:50]}"
    properties = {
        "Name": {"title": [{"text": {"content": title[:100]}}]},
    }
    for notion_prop, record_key in NOTION_DB_PROPS.items():
        if notion_prop == "Name":
            continue
        val = record.get(record_key)
        if val is not None:
            properties[notion_prop] = notion_property_type(record_key, val)

    try:
        result = notion_post("pages", {
            "parent": {"database_id": NOTION_FLORIST_DATABASE_ID},
            "properties": properties,
        })
        if result.get("id"):
            return result["id"]
        print(f"  Unexpected Notion response: {result}")
    except Exception as e:
        print(f"  Notion error: {e}")
    return None


def notion_query_existing(database_id: str, local_id: str) -> Optional[str]:
    """
    Check if a page with this Local ID already exists.
    Returns page ID if found, else None.
    """
    try:
        result = notion_post(f"databases/{database_id}/query", {
            "filter": {
                "property": "Local ID",
                "rich_text": {"equals": local_id},
            },
            "page_size": 1,
        })
        results = result.get("results", [])
        if results:
            return results[0]["id"]
    except Exception:
        pass
    return None


def cmd_sync_notion(args):
    records = load_jsonl(args.in_) if Path(args.in_).exists() else []
    records = [r for r in records if r.get("status") == "analysed"]

    if not NOTION_FLORIST_DATABASE_ID:
        print("NOTION_FLORIST_REVIEW_DATABASE_ID not set — skipping Notion sync")
        print("  Set it with:  export NOTION_FLORIST_REVIEW_DATABASE_ID=<your-id>")
        return

    created, updated, failed = 0, 0, 0

    for r in records:
        local_id = r.get("id", "")
        existing_page_id = notion_query_existing(NOTION_FLORIST_DATABASE_ID, local_id)

        if existing_page_id:
            # Update existing page
            try:
                properties = {}
                for notion_prop, record_key in NOTION_DB_PROPS.items():
                    if notion_prop == "Name":
                        continue
                    val = r.get(record_key)
                    if val is not None:
                        properties[notion_prop] = notion_property_type(record_key, val)
                notion_patch(f"pages/{existing_page_id}", {"properties": properties})
                updated += 1
            except Exception as e:
                print(f"  Update failed for {local_id}: {e}")
                failed += 1
        else:
            page_id = create_notion_page(r)
            if page_id:
                created += 1
            else:
                failed += 1

    print(
        f"Notion sync complete: {created} created, {updated} updated, {failed} failed"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Florist Review Intelligence — stdlib CLI pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_q = sub.add_parser("seed-queries", help="Generate search queries from config")
    p_q.add_argument("--config", required=True, help="Path to config JSON")
    p_q.add_argument("--out", required=True, help="Output .txt path")

    p_h = sub.add_parser("harvest-url", help="Fetch and extract reviews from a URL")
    p_h.add_argument("--brand", required=True)
    p_h.add_argument("--market", required=True)
    p_h.add_argument("--source", required=True)
    p_h.add_argument("--url", required=True)
    p_h.add_argument("--out", required=True)

    p_d = sub.add_parser("dedupe", help="Deduplicate a JSONL file")
    p_d.add_argument("--in", dest="in_", required=True)
    p_d.add_argument("--out", required=True)

    p_a = sub.add_parser("analyse", help="Analyse raw reviews into schema")
    p_a.add_argument("--in", dest="in_", required=True)
    p_a.add_argument("--out", required=True)
    p_a.add_argument("--report", default=None)

    p_e = sub.add_parser("export-csv", help="Export analysed JSONL to CSV")
    p_e.add_argument("--in", dest="in_", required=True)
    p_e.add_argument("--out", required=True)

    p_s = sub.add_parser("sync-notion", help="Sync analysed records to Notion")
    p_s.add_argument("--in", dest="in_", required=True)

    args = parser.parse_args()

    if args.command == "seed-queries":
        cmd_seed_queries(args)
    elif args.command == "harvest-url":
        cmd_harvest_url(args)
    elif args.command == "dedupe":
        cmd_dedupe(args)
    elif args.command == "analyse":
        cmd_analyse(args)
    elif args.command == "export-csv":
        cmd_export_csv(args)
    elif args.command == "sync-notion":
        cmd_sync_notion(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
