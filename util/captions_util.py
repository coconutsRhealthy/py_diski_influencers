import re
import unicodedata

def normalize_caption(caption):
    """
    Normalize the caption to plain text:
    - Remove emojis and non-ASCII characters
    - Normalize unicode
    """
    if not isinstance(caption, str):
        return ""

    # Normalize unicode (e.g. é -> é)
    normalized = unicodedata.normalize("NFKD", caption)

    # Remove emojis and non-ASCII characters
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")

    # Optionally, remove extra whitespace
    return re.sub(r'\s+', ' ', ascii_only).strip()
