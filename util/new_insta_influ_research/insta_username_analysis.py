import json
from pathlib import Path
import mysql.connector
import random

def get_usernames_from_jsons(directory_path):
    directory = Path(directory_path)
    brands = {
        "gutsgusto",
        "loavies",
        "getdrezzed",
        "begoldennl",
        "mimamsterdam",
        "paulie__pocket",
        "famousstore",
        "terstalnl",
        "maniacnails.official",
        "tessvfashion"
    }
    usernames_with_brands = {}

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

    return usernames_with_brands


def check_usernames_in_mysql(usernames):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="diski"  # <-- hier zet je je nieuwe DB
    )
    cursor = connection.cursor()

    results = {}
    for username in usernames:
        cursor.execute("SELECT 1 FROM influencers WHERE name = %s", (username,))
        results[username] = cursor.fetchone() is not None

    cursor.close()
    connection.close()
    return results


if __name__ == "__main__":
    folder_path = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned/2025"
    min_brands = 1  # <-- Pas dit aan: minimaal aantal merken per username

    usernames_with_brands = get_usernames_from_jsons(folder_path)

    # Filter usernames op minimaal aantal merken
    filtered_usernames = {u: b for u, b in usernames_with_brands.items() if len(b) >= min_brands}

    db_results = check_usernames_in_mysql(filtered_usernames.keys())

    total_in_db = sum(1 for v in db_results.values() if v)
    total_not_in_db = sum(1 for v in db_results.values() if not v)
    total = total_in_db + total_not_in_db
    percent_not_in_db = (total_not_in_db / total * 100) if total > 0 else 0

    for idx, username in enumerate(sorted(filtered_usernames), start=1):
        brands_list = sorted(filtered_usernames[username])
        in_db = "✅ in DB" if db_results[username] else "❌ niet in DB"
        print(f"{idx}. {username}: {brands_list} --> {in_db}")

    print("\n--- Samenvatting ---")
    print(f"Totaal usernames gevonden (na filter): {total}")
    print(f"In DB: {total_in_db}")
    print(f"Niet in DB: {total_not_in_db}")
    print(f"Percentage niet in DB: {percent_not_in_db:.2f}%")

    # --- NIEUW GEDEELTE: schrijf alleen usernames die NIET in de DB staan ---
    output_file = Path("filtered_usernames_not_in_db8.txt")

    # Maak lijst van usernames die niet in de DB staan
    usernames_not_in_db = [u for u in sorted(filtered_usernames) if not db_results[u]]

    # Parameter: hoeveel random usernames wil je opslaan?
    sample_size = 251
    if sample_size > len(usernames_not_in_db):
        sample_size = len(usernames_not_in_db)  # voorkom fout bij te grote sample

    # Kies random subset
    random_sample = random.sample(usernames_not_in_db, sample_size)

    # Schrijf naar bestand
    with open(output_file, "w", encoding="utf-8") as f:
        for username in random_sample:
            f.write(f"https://www.instagram.com/{username}\n")

    print(f"\n{sample_size} random gekozen usernames (van de {len(usernames_not_in_db)} die niet in DB staan) zijn opgeslagen in: {output_file.resolve()}")