import sqlite3

DB_PATH = "../data/deals.db"
OUT_PATH = "../data/analysis.txt"

def safe(n):
    return 0 if n is None else n

def analyze():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), AVG(price), MIN(price), MAX(price) FROM deals")
    count, avg_price, min_price, max_price = cur.fetchone()

    # Безопасные значения
    count = safe(count)
    avg_price = safe(avg_price)
    min_price = safe(min_price)
    max_price = safe(max_price)

    cur.execute("SELECT title, price FROM deals WHERE price > 0 ORDER BY price ASC LIMIT 5")
    cheapest = cur.fetchall()

    cur.execute("SELECT title, price FROM deals WHERE price > 0 ORDER BY price DESC LIMIT 5")
    most_expensive = cur.fetchall()

    conn.close()

    # Формируем отчёт
    report = []
    report.append("📊 ANALYSIS REPORT")
    report.append("=====================")
    report.append(f"Total deals: {count}")
    report.append(f"Average price: {avg_price:.2f}")
    report.append(f"Cheapest price: {min_price:.2f}")
    report.append(f"Most expensive price: {max_price:.2f}")

    report.append("\nTOP 5 CHEAPEST:")
    if cheapest:
        for title, price in cheapest:
            report.append(f" - {title} — {price} KZT")
    else:
        report.append("No items")

    report.append("\nTOP 5 MOST EXPENSIVE:")
    if most_expensive:
        for title, price in most_expensive:
            report.append(f" - {title} — {price} KZT")
    else:
        report.append("No items")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("✔ analysis.txt создан!")

if __name__ == "__main__":
    analyze()
