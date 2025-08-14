from util.read_json_insta import read_insta_json_data
from util.read_json_insta_mentioned import read_insta_mentioned_json_data
from util.read_json_tiktok import read_tiktok_json_data
from db.db_insert_captions import insert_records
from util.captions_util import normalize_caption, check_keywords_in_caption

def pipeline_insert_captions_in_db(platform):
    if platform == "instagram":
        user_posts = read_insta_json_data()
    elif platform == "instagram_mention":
        platform = "instagram"

        print("Reading BIG Instagram mention posts...")
        user_posts = read_insta_mentioned_json_data("big")
        print(f"Number of usernames in BIG posts: {len(user_posts)}")
        total_big_posts = sum(len(posts) for posts in user_posts.values())
        print(f"Total posts in BIG posts: {total_big_posts}\n")

        print("Reading SMALL Instagram mention posts...")
        small_posts = read_insta_mentioned_json_data("small")
        print(f"Number of usernames in SMALL posts: {len(small_posts)}")
        total_small_posts = sum(len(posts) for posts in small_posts.values())
        print(f"Total posts in SMALL posts: {total_small_posts}\n")

        print("Merging SMALL posts into BIG posts...")
        for username, posts in small_posts.items():
            user_posts.setdefault(username, []).extend(posts)

        print(f"After merge - number of usernames: {len(user_posts)}")
        total_merged_posts = sum(len(posts) for posts in user_posts.values())
        print(f"After merge - total posts: {total_merged_posts}\n")
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
    pipeline_insert_captions_in_db("instagram")
