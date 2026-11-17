from db import Database
from scrapers import BooksScraper, DealsScraper

db = Database()


def update():
    products = []
    for scraper in [BooksScraper(pages=5), DealsScraper(limit=20)]:
        products.extend(scraper.fetch())
    print(f"Оновлено товарів: {db.update_from(products)}. У базі всього: {db.count()}")


def search():
    word = input("Слово для пошуку: ")
    for product_id, title, price, currency in db.find(word):
        print(f"  #{product_id} {title[:50]:50} {currency}{price}")


def top_deals():
    for product_id, title, price, old_price, discount, currency in db.top_discounts(5):
        print(f"  #{product_id} {title[:34]:34} -{int(discount)}%  {currency}{price} (було {currency}{old_price})")


def stats():
    for name, currency, items, avg_price, cheapest, priciest in db.stats_by_source():
        print(f"  {name}: {items} шт., середня {currency}{avg_price}, від {currency}{cheapest} до {currency}{priciest}")


def history():
    product_id = int(input("Номер товару (#): "))
    for checked_at, price in db.price_history(product_id):
        print(f"  {checked_at}  {price}")
    drop = db.price_drop(product_id)
    print("  Ціна впала!" if drop else "  Падіння ціни не зафіксовано.", drop or "")



MENU = {"1": ("Оновити дані", update), "2": ("Пошук за словом", search), "3": ("Топ-5 знижок", top_deals),
        "4": ("Статистика по джерелах", stats), "5": ("Історія цін товару", history)}

while True:
    print("\n=== DEAL RADAR ===")
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
print("До зустрічі!")