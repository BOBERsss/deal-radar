import requests

URL = "https://books.toscrape.com/"

response = requests.get(URL)
print("Адреса:", response.url)
print("Код відповіді:", response.status_code)
print("Розмір сторінки:", len(response.text), "символів")
print("Початок HTML:")
print(response.text[:120])

# А що, якщо такої сторінки немає?
missing = requests.get("https://books.toscrape.com/no-such-page.html")
print("Неіснуюча сторінка, код:", missing.status_code)
