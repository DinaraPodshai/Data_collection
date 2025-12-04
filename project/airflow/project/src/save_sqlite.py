import json
import sqlite3

CLEAN_PATH = "../data/clean.json"
DB_PATH = "../data/deals.db"

def save_to_sqlite():
    with open(CLEAN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Создаём таблицу
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            old_price REAL,
            city TEXT,
            link TEXT
        );
    """)

    # Чистим таблицу перед загрузкой
    cur.execute("DELETE FROM deals")

    # Загружаем данные
    for item in data:
        cur.execute("""
            INSERT INTO deals (title, price, old_price, city, link)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item["title"],
            item["price"],
            item["old_price"],
            item["city"],
            item["link"]
        ))

    conn.commit()
    conn.close()

    print("✔ deals.db — база успешно создана и заполнена!")

if __name__ == "__main__":
    save_to_sqlite()
