import json
import re

RAW_PATH = "../data/raw.json"
CLEAN_PATH = "../data/clean.json"

def clean_text(t):
    if not t:
        return ""
    return re.sub(r"\s+", " ", t).strip()

def clean():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    for item in data:
        cleaned.append({
            "title": clean_text(item.get("title")),
            "price": float(re.sub(r"[^\d]", "", item.get("price", "0"))) if item.get("price") else 0,
            "old_price": float(re.sub(r"[^\d]", "", item.get("old_price", "0"))) if item.get("old_price") else 0,
            "city": clean_text(item.get("city")),
            "link": item.get("link", "")
        })

    with open(CLEAN_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print("✔ clean.json готов!")

if __name__ == "__main__":
    clean()
