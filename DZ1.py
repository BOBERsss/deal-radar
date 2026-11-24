import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scrapers import HEADERS

URL = "https://books.toscrape.com/catalogue/page-1.html"


def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        print("Помилка запиту:", error)
        return None
    response.encoding = "utf-8"
    time.sleep(1)
    return BeautifulSoup(response.text, "html.parser")


def get_book_links(url, limit=5):
    soup = get_page(url)
    if soup is None:
        return []

    links = []
    for item in soup.select("article.product_pod h3 a"):
        href = item["href"]
        full_url = urljoin(url, href)
        links.append(full_url)
        if len(links) == limit:
            break
    return links


def get_book_info(book_url):
    soup = get_page(book_url)
    if soup is None:
        return None

    title = soup.select_one("div.product_main h1").get_text(strip=True)

    breadcrumbs = soup.select("ul.breadcrumb li a")
    category = breadcrumbs[2].get_text(strip=True)

    stock_text = soup.select_one("p.instock.availability").get_text(strip=True)
    stock = 0
    for part in stock_text.replace("(", "").replace(")", "").split():
        if part.isdigit():
            stock = int(part)
            break

    desc_title = soup.select_one("#product_description")
    description = ""
    if desc_title is not None:
        desc_p = desc_title.find_next_sibling("p")
        if desc_p is not None:
            description = desc_p.get_text(strip=True)

    book = {
        "title": title,
        "category": category,
        "stock": stock,
        "description": description,
    }
    return book


books = []
links = get_book_links(URL, limit=5)

for link in links:
    info = get_book_info(link)
    if info is not None:
        books.append(info)

print("\nЗвіт по книжках:")
for book in books:
    short_desc = book["description"][:80]
    print("-", book["title"], "|", book["category"], "| в наявності:", book["stock"])
    print("  Опис:", short_desc)