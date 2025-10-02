from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Initialize OpenAI client with API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

def read_captions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(captions_text):
    return f"""
You are a data extraction assistant.

The captions may be in Dutch or English.

Extract all discount codes from the following Instagram caption. For each code, return:
- the webshop or brand it's valid for (as "webshop"),
- the discount code itself (as "code"),
- and the percentage off (as "percentage", if mentioned).

Important notes about "percentage":
- Usually this is a percentage off (e.g., 20% → percentage=20).
- Sometimes it is an amount in euros (e.g., €10 korting → percentage=€10).
- If the caption does not explicitly mention a discount, look at the code itself and see if you can reasonably infer the percentage from it (e.g., SUMMER20 → 20, HANNAH15 → 15).

Return only raw JSON in this format:
[
  {{
    "webshop": "...",
    "code": "...",
    "percentage": ...
  }},
  ...
]

If any value is missing (like percentage), use null for that field.
If no discount codes are found, return an empty list: [].
Do NOT include any explanation, notes, or markdown — ONLY return raw JSON.

Captions:
\"\"\"
{captions_text}
\"\"\"
"""

def extract_discount_codes(captions_text):
    prompt_text = build_prompt(captions_text)

    # Send prompt and get response from OpenAI API
    response = client.responses.create(
        model="gpt-5-mini",  # or another suitable model like "gpt-4.1-mini" or "gpt-4-turbo"
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt_text},
            ],
        }]
    )

    # Process the raw response and extract structured JSON
    result_text = response.output_text.strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        print("Warning: Model output is not valid JSON.\nHere is the raw output:\n")
        print(result_text)
        return None

if __name__ == "__main__":
    load_dotenv()
    captions_file = "captions.txt"
    captions = read_captions(captions_file)

    structured_data = extract_discount_codes(captions)

    if structured_data is not None:
        print(json.dumps(structured_data, indent=2, ensure_ascii=False))
