"""One-off backfill: load every remaining local JSON under jsons/ into
captions_archive — the hashtag, users, tiktok and date-organized mentioned
dumps that were NOT covered by the earlier backfills.

Excludes jsons/insta/mentioned/apify_api_jsons (already done by
backfill_mentioned_to_archive.py). Platform is derived from the path; record
shapes are handled by the same extractors used for the live Apify backfill, so
captions are extracted identically:
  - jsons/insta/users/...      -> profile records with latestPosts
  - jsons/insta/hashtag/...    -> flat post records (ownerUsername/caption/url)
  - jsons/insta/mentioned/...  -> flat post records (tagged-scraper dumps)
  - jsons/tiktok/...           -> tiktok post records (authorMeta/text/webVideoUrl)

Captions are normalized like the live pipeline and inserted via INSERT IGNORE,
so this is safe to re-run and dedupes against existing rows.
"""
import glob
import json
import os

from util.captions_util import normalize_caption
from db.db_insert_captions import insert_archive_records
from backfill_apify_runs_to_archive import extract_instagram, extract_tiktok

JSON_GLOB = "jsons/**/*.json"
EXCLUDE_SUBSTR = "apify_api_jsons"  # already backfilled from local files


def platform_for(path):
    return "tiktok" if "/tiktok/" in path else "instagram"


def extractor_for(platform):
    return extract_tiktok if platform == "tiktok" else extract_instagram


def collect():
    files = sorted(f for f in glob.glob(JSON_GLOB, recursive=True) if EXCLUDE_SUBSTR not in f)
    print(f"Found {len(files)} local JSON file(s) to process (excluding {EXCLUDE_SUBSTR}).")

    buckets = {"instagram": [], "tiktok": []}
    seen = {"instagram": set(), "tiktok": set()}
    raw_counts = {"instagram": 0, "tiktok": 0}

    for path in files:
        platform = platform_for(path)
        extractor = extractor_for(platform)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ! Skipping {path}: {e}")
            continue
        if not isinstance(data, list):
            continue

        for record in data:
            if not isinstance(record, dict):
                continue
            for post in extractor(record):
                raw_counts[platform] += 1
                url = post["post_url"]
                caption = normalize_caption(post["caption"])  # keeps empty captions as ""
                key = (url, caption[:255])
                if key in seen[platform]:
                    continue
                seen[platform].add(key)
                buckets[platform].append({
                    "influencer_name": post["influencer_name"],
                    "caption": caption,
                    "post_url": url,
                    "post_date": post["post_date"],
                })

    for p in ("instagram", "tiktok"):
        print(f"  {p}: {raw_counts[p]} extracted -> {len(buckets[p])} unique")
    return buckets


def main():
    buckets = collect()
    for platform, records in buckets.items():
        insert_archive_records(records, platform)
    print("Local jsons backfill complete.")


if __name__ == "__main__":
    main()
