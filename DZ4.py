import sqlite3


class StatsDatabase:
    def __init__(self, db_path="radar.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def count_by_rating(self):
        self.cursor.execute("""
            SELECT p.rating, COUNT(*)
            FROM products p
            JOIN sources s ON p.source_id = s.id
            WHERE s.name = 'books' AND p.rating IS NOT NULL
            GROUP BY p.rating
            ORDER BY p.rating
        """)
        return self.cursor.fetchall()

    def priciest(self, n):
        self.cursor.execute("""
            SELECT p.title, p.price, s.currency
            FROM products p
            JOIN sources s ON p.source_id = s.id
            ORDER BY p.price DESC
            LIMIT ?
        """, (n,))
        return self.cursor.fetchall()

    def big_deals_count(self, min_discount=50):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM products p
            JOIN sources s ON p.source_id = s.id
            WHERE s.name = 'deals'
              AND p.old_price IS NOT NULL
              AND p.old_price > 0
              AND ((p.old_price - p.price) / p.old_price) * 100 >= ?
        """, (min_discount,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def close(self):
        self.conn.close()


db = StatsDatabase("radar.db")


def show_by_rating():
    print("\nКількість книжок за рейтингом:")
    for rating, total in db.count_by_rating():
        print(f"  Рейтинг {rating}: {total} шт.")


def show_priciest():
    n = int(input("Скільки найдорожчих товарів вивести? "))
    print(f"\nТоп-{n} найдорожчих товарів:")
    for title, price, currency in db.priciest(n):
        print(f"  {title[:45]:45} {currency}{price}")


def show_big_deals():
    total = db.big_deals_count(50)
    print(f"\nКількість ігор зі знижкою від 50%: {total}")


MENU = {
    "1": ("Кількість книжок за рейтингом", show_by_rating),
    "2": ("N найдорожчих товарів", show_priciest),
    "3": ("Ігри зі знижкою від 50%", show_big_deals),
}

while True:
    print("\n=== DZ4: МОЯ СТАТИСТИКА ===")
    for key, (label, _) in MENU.items():
        print(f"{key}. {label}")
    print("0. Вихід")
    choice = input("Обери пункт: ")
    if choice == "0":
        break
    if choice in MENU:
        MENU[choice][1]()
    else:
        print("Такого пункту немає.")

db.close()