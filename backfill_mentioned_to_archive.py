"""One-off backfill: load every archived 'mentioned' Apify JSON and insert all
captions into the captions_archive table (platform='instagram').

These JSONs (jsons/insta/mentioned/apify_api_jsons/*.json) are the only raw scrape
output we kept on disk, so they let the archive reach back further than today.
Captions are normalized identically to the live pipeline and inserted via
INSERT IGNORE, so this script is safe to re-run and dedupes against existing rows.
"""
import glob
import json
import os

from util.captions_util import normalize_caption
from db.db_insert_captions import insert_archive_records

ARCHIVE_GLOB = "jsons/insta/mentioned/apify_api_jsons/*.json"
PLATFORM = "instagram"


def collect_records():
    files = sorted(glob.glob(ARCHIVE_GLOB))
    print(f"Found {len(files)} mentioned JSON file(s).")

    seen = set()          # (post_url, normalized_caption[:255]) -> in-memory dedup
    records = []
    total_seen = 0
    skipped_no_url = 0

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ! Skipping {os.path.basename(path)}: {e}")
            continue

        if not isinstance(data, list):
            continue

        for record in data:
            total_seen += 1
            url = record.get("url")
            if not url:
                skipped_no_url += 1
                continue  # post_url is the dedup key; unusable without it

            caption = normalize_caption(record.get("caption"))  # keeps empty captions as ""
            key = (url, caption[:255])
            if key in seen:
                continue
            seen.add(key)

            records.append({
                "influencer_name": record.get("ownerUsername"),
                "caption": caption,
                "post_url": url,
                "post_date": record.get("timestamp"),  # raw ISO; MySQL truncates to DATETIME
            })

    print(f"Scanned {total_seen} raw records across all files.")
    print(f"Skipped {skipped_no_url} record(s) without a post_url.")
    print(f"Unique (post_url, caption) pairs to archive: {len(records)}")
    return records


def main():
    records = collect_records()
    insert_archive_records(records, PLATFORM)
    print("Backfill complete.")


if __name__ == "__main__":
    main()
