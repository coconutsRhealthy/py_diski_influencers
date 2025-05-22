from util.read_json_insta import read_insta_json_data
from util.read_json_insta_mentioned import read_insta_mentioned_json_data
from util.read_json_tiktok import read_tiktok_json_data
from db.db_insert_captions import insert_records
from util.captions_util import normalize_caption, check_keywords_in_caption

def main(platform):
    if platform == "instagram_user":
        user_posts = read_insta_json_data()
    elif platform == "instagram_mention":
        user_posts = read_insta_mentioned_json_data()
    elif platform == "tiktok":
        user_posts = read_tiktok_json_data()
    else:
        raise ValueError("Unsupported platform. Use 'instagram' or 'tiktok'.")

    records = []
    for username, posts in user_posts.items():
        for post in posts:
            normalized_caption = normalize_caption(post['caption'])

            if check_keywords_in_caption(normalized_caption):
                records.append({
                    'influencer_name': username,
                    'caption': normalized_caption,
                    'post_url': post['url'],
                    'post_date': post['timestamp']
                })

    insert_records(records, platform)
    print(f"Inserted {len(records)} {platform} records.")

if __name__ == "__main__":
    main("instagram")
