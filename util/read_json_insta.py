from apify_client import ApifyClient
from dotenv import load_dotenv
import os

def load_direct_urls():
    with open("util/apify_input/instagram_user_urls.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def fetch_insta_json_data(direct_urls):
    apify_token = os.environ.get("APIFY_TOKEN", os.getenv("APIFY_KEY"))
    client = ApifyClient(apify_token)

    run_input = {
        "addParentData": False,
        "directUrls": direct_urls,
        "enhanceUserSearchWithFacebookPage": False,
        "isUserReelFeedURL": False,
        "isUserTaggedFeedURL": False,
        "resultsLimit": 5,
        "resultsType": "details",
        "searchType": "hashtag"
    }

    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return dataset_items


def read_insta_json_data():
    direct_urls = load_direct_urls()
    data = fetch_insta_json_data(direct_urls)

    user_posts = {}

    for record in data:
        username = record.get('username', None)
        if not username:
            continue  # skip records zonder username

        latest_posts = record.get('latestPosts', [])
        if not isinstance(latest_posts, list):
            continue  # skip als latestPosts geen lijst is

        posts_info = []
        for post in latest_posts:
            caption = post.get('caption', '')
            url = post.get('url', '')
            timestamp = post.get('timestamp', None)

            posts_info.append({
                'caption': caption,
                'url': url,
                'timestamp': timestamp
            })

        user_posts[username] = posts_info

    return user_posts

if __name__ == "__main__":
    load_dotenv()
    user_posts = read_insta_json_data()

    for username, posts in user_posts.items():
        print(f"\n{username}:")
        for post in posts:
            print(f"  {post['timestamp']}: {post['url']} - {post['caption'][:40]}...")
