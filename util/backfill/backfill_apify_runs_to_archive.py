"""One-off backfill: pull the raw datasets of recent Apify runs (still on the
platform within the ~31-day data-retention window) into captions_archive.

Covers the two actors whose raw output we did NOT keep locally:
  - apify/instagram-scraper      (users flow)  -> platform 'instagram'
  - clockworks/free-tiktok-scraper             -> platform 'tiktok'

The mentioned actor (apify/instagram-tagged-scraper) is intentionally skipped:
its output was archived from local JSONs by backfill_mentioned_to_archive.py.

Captions are normalized identically to the live pipeline and inserted via
INSERT IGNORE, so this is safe to re-run and dedupes against existing rows.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from apify_client import ApifyClient
from dotenv import load_dotenv

from util.captions_util import normalize_caption
from db.db_insert_captions import insert_archive_records

# (actor_id, platform) for the actors we want to backfill.
ACTORS = [
    ("shu8hvrXbJbY3Eb9W", "instagram"),   # apify/instagram-scraper
    ("OtzYfK1ndEGdwWFKQ", "tiktok"),      # clockworks/free-tiktok-scraper
]


def extract_instagram(item):
    """Yield post dicts from an instagram-scraper dataset item.

    Items are user-profile records carrying a latestPosts list; fall back to
    treating the item itself as a post if it already looks like one.
    """
    posts = item.get("latestPosts")
    if isinstance(posts, list) and posts:
        for post in posts:
            url = post.get("url")
            if not url:
                continue
            yield {
                "influencer_name": post.get("ownerUsername") or item.get("username"),
                "caption": post.get("caption"),
                "post_url": url,
                "post_date": post.get("timestamp"),
            }
    elif item.get("url") and "caption" in item:
        yield {
            "influencer_name": item.get("ownerUsername") or item.get("username"),
            "caption": item.get("caption"),
            "post_url": item.get("url"),
            "post_date": item.get("timestamp"),
        }


def extract_tiktok(item):
    """Yield a post dict from a tiktok-scraper dataset item, skipping error rows."""
    if not all(k in item for k in ("text", "createTimeISO", "webVideoUrl")):
        return  # error record or non-post
    author = item.get("authorMeta") or {}
    yield {
        "influencer_name": author.get("name"),
        "caption": item.get("text"),
        "post_url": item.get("webVideoUrl"),
        "post_date": item.get("createTimeISO"),
    }


EXTRACTORS = {"instagram": extract_instagram, "tiktok": extract_tiktok}


def backfill_actor(client, actor_id, platform):
    extractor = EXTRACTORS[platform]
    runs = client.actor(actor_id).runs().list(limit=1000, desc=True).items
    succeeded = [r for r in runs if r.get("status") == "SUCCEEDED"]
    print(f"\n=== {platform} (actor {actor_id}): {len(succeeded)}/{len(runs)} succeeded run(s) ===")

    seen = set()        # (post_url, caption[:255]) in-memory dedup
    records = []
    for i, run in enumerate(succeeded, 1):
        ds_id = run.get("defaultDatasetId")
        if not ds_id:
            continue
        added = 0
        for item in client.dataset(ds_id).iterate_items():
            for post in extractor(item):
                url = post["post_url"]
                caption = normalize_caption(post["caption"])  # keeps empty captions as ""
                key = (url, caption[:255])
                if key in seen:
                    continue
                seen.add(key)
                records.append({
                    "influencer_name": post["influencer_name"],
                    "caption": caption,
                    "post_url": url,
                    "post_date": post["post_date"],
                })
                added += 1
        print(f"  [{i}/{len(succeeded)}] {str(run.get('startedAt'))[:19]} ds={ds_id} -> +{added} new (running unique={len(records)})")

    print(f"Unique {platform} captions to archive: {len(records)}")
    insert_archive_records(records, platform)
    return len(records)


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    token = os.environ.get("APIFY_TOKEN", os.getenv("APIFY_KEY"))
    client = ApifyClient(token)

    grand_total = 0
    for actor_id, platform in ACTORS:
        grand_total += backfill_actor(client, actor_id, platform)
    print(f"\nBackfill complete. {grand_total} unique captions processed across actors.")


if __name__ == "__main__":
    main()
