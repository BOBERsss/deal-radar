from product import Product
from scrapers import BaseScraper, BooksScraper, DealsScraper
from storage import save_csv, save_json


class PokemonScraper(BaseScraper):
    name = "pokemon"
    API_URL = "https://pokeapi.co/api/v2/pokemon"

    def __init__(self, limit=20, delay=0.5):
        super().__init__(delay)
        self.limit = limit

    def fetch(self):
        response = self.get(self.API_URL, limit=self.limit)
        if response is None:
            return []

        data = response.json()
        products = []

        for item in data.get("results", []):
            detail = self.get(item["url"])
            if detail is None:
                continue
            info = detail.json()
            title = info["name"].capitalize()
            price = float(info.get("base_experience") or 10)
            products.append(Product(title, price, self.name, currency="PTS"))

        return products


scrapers = [BooksScraper(pages=5), DealsScraper(limit=20), PokemonScraper(limit=20)]

products = []
for scraper in scrapers:
    found = scraper.fetch()
    print(f"[{scraper.name}] зібрано: {len(found)}")
    products.extend(found)

print(f"\nУсього товарів: {len(products)}")

stats_by_source = {
    scraper.name: len([p for p in products if p.source == scraper.name])
    for scraper in scrapers
}
print("Статистика за джерелами:", stats_by_source)

for scraper in scrapers:
    group = [p for p in products if p.source == scraper.name]
    if group:
        print(f"Найдешевше ({scraper.name}):", min(group, key=lambda p: p.price))

best_deal = max(products, key=lambda p: p.discount())
print("Найбільша знижка:", best_deal)

save_json(products, "products_dz2.json")
save_csv(products, "products_dz2.csv")
print("Збережено: products_dz2.json, products_dz2.csv")