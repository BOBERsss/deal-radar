import sqlite3
import pytest
from bs4 import BeautifulSoup
from product import Product




def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        title = card.select_one("h3 a")["title"]
        price_text = card.select_one("p.price_color").get_text(strip=True)
        price = float(price_text.replace("£", "").replace("Â", ""))
        books.append(Product(title, price, "books", currency="£"))
    return books


def parse_deals(data):
    deals = []
    for item in data:
        title = item["title"]
        price = float(item["salePrice"])
        old_price = float(item["normalPrice"])
        deals.append(Product(title, price, "deals", old_price=old_price, currency="$"))
    return deals


def test_product_discount():
    item = Product("Game", 50.0, "deals", old_price=100.0)
    assert item.discount() == 50.0


def test_product_no_discount():
    item = Product("Book", 20.0, "books")
    assert item.discount() == 0


def test_product_invalid_price():
    with pytest.raises(ValueError):
        Product("Bad item", -10.0, "books")


def test_product_to_dict():
    item = Product("Dune", 15.0, "books", currency="£")
    data = item.to_dict()
    assert data["title"] == "Dune"
    assert data["price"] == 15.0
    assert data["source"] == "books"


def test_parse_page():
    sample_html = """
    <article class="product_pod">
        <h3><a title="Test Book">Test Book</a></h3>
        <p class="price_color">£12.50</p>
    </article>
    """
    result = parse_page(sample_html)
    assert len(result) == 1
    assert result[0].title == "Test Book"
    assert result[0].price == 12.5


def test_parse_deals():
    sample_json = [
        {"title": "Cyber Game", "salePrice": "10.00", "normalPrice": "40.00"}
    ]
    result = parse_deals(sample_json)
    assert len(result) == 1
    assert result[0].title == "Cyber Game"
    assert result[0].discount() == 75.0



def create_test_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            price REAL
        )
    """)
    cur.execute("""
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL
        )
    """)
    conn.commit()
    return conn


def test_db_no_duplicates():
    conn = create_test_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO products (title, price) VALUES (?, ?)", ("Book 1", 10.0))
    cur.execute("INSERT OR IGNORE INTO products (title, price) VALUES (?, ?)", ("Book 1", 10.0))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM products")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_db_price_history():
    conn = create_test_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (title, price) VALUES (?, ?)", ("Game 1", 30.0))
    product_id = cur.lastrowid

    cur.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (product_id, 30.0))
    cur.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (product_id, 20.0))
    conn.commit()

    cur.execute("SELECT price FROM price_history WHERE product_id = ?", (product_id,))
    prices = [row[0] for row in cur.fetchall()]
    assert prices == [30.0, 20.0]
    conn.close()