import sqlite3

DB_PATH = "deals.db"


def connect(path=DB_PATH):
  return sqlite3.connect(path)


def create_tables(conn):
  conn.execute(
  """
  CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  price REAL NOT NULL,
  currency TEXT,
  old_price REAL,
  rating REAL,
  source TEXT
)
"""
  )
  conn.commit()


def save_products(conn, products):
  """Записує список Product у таблицю (спочатку очищує стару версію)."""
  conn.execute("DELETE FROM products")
  rows = [(p.title, p.price, p.currency, p.old_price, p.rating, p.source) for p in products]
  conn.executemany(
  "INSERT INTO products (title, price, currency, old_price, rating, source) "
  "VALUES (?, ?, ?, ?, ?, ?)",
  rows,
)
  conn.commit()
  return len(rows)