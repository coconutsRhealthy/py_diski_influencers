from apify_client import ApifyClient
import os


def load_username_input():
    with open("util/apify_input/instagram_mentioned.txt", "r", encoding="utf-8") as f:
        username_input = [line.strip() for line in f if line.strip()]
    return username_input

def fetch_insta_mentioned_json_data(username_input):
    apify_token = os.environ.get("APIFY_TOKEN", "secret")
    client = ApifyClient(apify_token)

    run_input = {
        "resultsLimit": 10,
        "username": username_input,
    }

    run = client.actor("apify/instagram-tagged-scraper").call(run_input=run_input)

    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return dataset_items


def read_insta_mentioned_json_data():
    direct_urls = load_username_input()
    data = fetch_insta_mentioned_json_data(direct_urls)

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
    mentioned_posts = read_insta_mentioned_json_data()
    print(mentioned_posts)
