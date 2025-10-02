import json
from pathlib import Path

def get_usernames_from_jsons(directory_path):
    directory = Path(directory_path)

    # De merken waar je op wilt filteren
    brands = {"myjewellery"}

    # Dictionary: username -> set(brands)
    usernames_with_brands = {}

    # Recursief alle JSON-bestanden vinden
    for json_file in directory.rglob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Fout bij inladen van {json_file}, wordt overgeslagen")
                continue

        for record in data:
            username = record.get('ownerUsername')
            if not username:
                continue

            mentions = record.get('mentions', [])
            matched_brands = brands.intersection(mentions)

            if matched_brands:
                if username not in usernames_with_brands:
                    usernames_with_brands[username] = set()
                usernames_with_brands[username].update(matched_brands)

    # Sorteer usernames alfabetisch en nummer ze
    for i, username in enumerate(sorted(usernames_with_brands), start=1):
        brands_list = sorted(usernames_with_brands[username])  # lijstje voor nette output
        print(f"{i}. {username}: {brands_list}")

if __name__ == "__main__":
    folder_path = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned/2025"
    get_usernames_from_jsons(folder_path)
