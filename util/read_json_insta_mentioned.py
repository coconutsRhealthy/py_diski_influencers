from apify_client import ApifyClient
from dotenv import load_dotenv
import os


def load_username_input(size: str):
    with open("util/apify_input/instagram_mentioned.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    usernames = []
    capture = False
    for line in lines:
        if line.lower() == f"{size}:":
            capture = True
            continue
        elif line.endswith(":"):
            capture = False

        if capture:
            usernames.append(line)

    return usernames

def fetch_insta_mentioned_json_data(username_input, size: str):
    load_dotenv()
    apify_token = os.environ.get("APIFY_TOKEN", os.getenv("APIFY_KEY"))
    client = ApifyClient(apify_token)

    results_limit = 50 if size == "big" else 10

    run_input = {
        "resultsLimit": results_limit,
        "username": username_input,
    }

    run = client.actor("apify/instagram-tagged-scraper").call(run_input=run_input)

    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return dataset_items


def read_insta_mentioned_json_data(size: str):
    if size not in ("small", "big"):
        raise ValueError("size must be either 'small' or 'big'")

    usernames = load_username_input(size)
    data = fetch_insta_mentioned_json_data(usernames, size)

    mentioned_posts = {}

    for record in data:
        username = record.get('ownerUsername', None)

        if not username:
            continue  # skip records zonder username

        caption = record['caption']
        timestamp = record['timestamp']
        url = record['url']

        post_info = {
            'caption': caption,
            'url': url,
            'timestamp': timestamp
        }

        if username not in mentioned_posts:
            mentioned_posts[username] = []

        mentioned_posts[username].append(post_info)

    return mentioned_posts

if __name__ == "__main__":
    load_dotenv()
    mentioned_posts = read_insta_mentioned_json_data("small")
    print(mentioned_posts)
