from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def build_normalization_prompt(unknown_webshops, known_webshop_keys):
    # unknown_webshops: list of strings (e.g. ["NA-KD", "ZalandoNL", ...])
    # known_webshop_keys: list of strings (e.g. ["nakdfashion", "zalando", "hm", ...])

    return f"""
You are a webshop name normalization assistant.

You will receive a list of webshop names extracted from captions that may vary in formatting, spelling, or casing.

Your task is to match each webshop name to the closest canonical webshop key from the provided list of known webshop keys.

Instructions:
- For each webshop name in the input list, find the best matching webshop key.
- If no good match exists, respond with "UNKNOWN" for that webshop.
- Matching should be case-insensitive and tolerant to common spelling differences.
- Return ONLY a JSON object that maps each webshop name to its normalized webshop key or "UNKNOWN".
- The JSON format must be exactly as follows (keys and values as strings):

{{
  "NA-KD": "nakdfashion",
  "ZalandoNL": "zalando",
  "UnknownShop": "UNKNOWN"
}}

Input webshop names:
{json.dumps(unknown_webshops, ensure_ascii=False)}

Known webshop keys:
{json.dumps(known_webshop_keys, ensure_ascii=False)}
"""


def normalize_webshops(unknown_webshops, known_webshop_keys):
    prompt_text = build_normalization_prompt(unknown_webshops, known_webshop_keys)

    response = client.responses.create(
        model="gpt-5",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt_text}
            ]
        }]
    )

    result_text = response.output_text.strip()

    try:
        mapping = json.loads(result_text)
        return mapping
    except json.JSONDecodeError:
        print("⚠️ Warning: Model output is not valid JSON. Raw output:")
        print(result_text)
        return None


if __name__ == "__main__":
    load_dotenv()
    unknowns = ["NA-KD", "ZalandoNL", "Hm", "NonExistingShop", "Emma"]
    known_keys = ["nakdfashion", "emmasleepnl", "zalando", "hm", "asos"]

    mapping_result = normalize_webshops(unknowns, known_keys)

    if mapping_result:
        print(json.dumps(mapping_result, indent=2, ensure_ascii=False))
