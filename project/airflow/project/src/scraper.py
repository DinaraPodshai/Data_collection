import json
import requests
import os
from bs4 import BeautifulSoup

URL = "https://chocolife.me/beauty/"
BASE_DIR =os.path.expanduser("~/airflow/project")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PATH = os.path.join(DATA_DIR, "raw.json")

def scrape():
    print("▶ Scraping Chocolife...")

    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    items = []

    cards = soup.select(".deal-card")  # Если структура другая — поправим
    for card in cards:
        title = card.select_one(".deal-title")
        price = card.select_one(".deal-price")
        old = card.select_one(".deal-old-price")
        city = card.select_one(".city")
        link_el = card.select_one("a")

        items.append({
            "title": title.text.strip() if title else "",
            "price": price.text.strip() if price else "",
            "old_price": old.text.strip() if old else "",
            "city": city.text.strip() if city else "",
            "link": "https://chocolife.me" + link_el["href"] if link_el else ""
        })

    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("✔ Raw data saved!")

if __name__ == "__main__":
    scrape()
