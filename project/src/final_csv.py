import sqlite3
import csv

DB_PATH = "../data/deals.db"
CSV_PATH = "../data/final.csv"

def save_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT title, price, old_price, city, link FROM deals")
    rows = cur.fetchall()

    conn.close()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "price", "old_price", "city", "link"])
        writer.writerows(rows)

    print("✔ final.csv создан!")

if __name__ == "__main__":
    save_csv()


