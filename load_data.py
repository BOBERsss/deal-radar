
from db import connect, create_tables, save_products
from scrapers import BooksScraper, DealsScraper

products = []

for scraper in [BooksScraper(pages=5), DealsScraper(limit=20)]:
    found = scraper.fetch()
    print(f"{scraper.name} зібрано:{len(found)}")
    products.extend(found)


conn = connect()
create_tables(conn)

save_products(conn, products)
conn.close()