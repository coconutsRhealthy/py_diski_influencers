from apify_client import ApifyClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import json


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

    try:
        save_json_to_file(dataset_items, size)
    except Exception as e:
        print(f"Error saving JSON: {e}")

    return dataset_items

def save_json_to_file(data, size: str):
    folder = Path("/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned/apify_api_jsons")
    folder.mkdir(parents=True, exist_ok=True)  # map aanmaken als die nog niet bestaat

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"mentioned_posts_{size}_{date_str}.json"
    filepath = folder / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Data opgeslagen in {filepath}")

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
