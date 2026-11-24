import sqlite3


def safe_search(conn, word=None, source=None, max_price=None):
    sql = (
        "SELECT p.id, p.title, s.name, p.price "
        "FROM products p "
        "JOIN sources s ON p.source_id = s.id"
    )
    conditions = []
    params = []

    if word is not None:
        conditions.append("p.title LIKE ?")
        params.append(f"%{word}%")

    if source is not None:
        conditions.append("s.name = ?")
        params.append(source)

    if max_price is not None:
        conditions.append("p.price <= ?")
        params.append(max_price)

    if conditions:
        sql = sql + " WHERE " + " AND ".join(conditions)

    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()


def apply_discount(conn, source, percent):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products "
        "SET price = ROUND(price * (1 - ? / 100.0), 2) "
        "WHERE source_id = (SELECT id FROM sources WHERE name = ?)",
        [percent, source],
    )
    conn.commit()
    return cursor.rowcount


conn = sqlite3.connect("radar.db")

# 3. Перевірка на 5 комбінаціях умов
print("--- 1) Усі товари (без умов) ---")
print("Кількість:", len(safe_search(conn)))

print("--- 2) Пошук за словом ---")
for row in safe_search(conn, word="Game")[:5]:
    print(row)

print("--- 3) Фільтр по джерелу ---")
for row in safe_search(conn, source="deals")[:5]:
    print(row)

print("--- 4) Фільтр по максимальній ціні ---")
for row in safe_search(conn, max_price=5.0)[:5]:
    print(row)

print("--- 5) Комбінація слово + джерело + ціна ---")
for row in safe_search(conn, word="War", source="deals", max_price=10.0):
    print(row)

# 4. Перевірка захисту від SQL-ін'єкції
injection_test = "x' OR '1'='1"
res_injection = safe_search(conn, word=injection_test)
print("\nПеревірка ін'єкції:", res_injection)

# 5. Перевірка apply_discount (наприклад, знижка 10% на 'deals')
changed = apply_discount(conn, "deals", 10)
print("Оновлено рядків після знижки:", changed)

conn.close()