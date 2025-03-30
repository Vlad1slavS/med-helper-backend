import os

import dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import psycopg2
import re

BASE_URL = "https://clinica.chitgma.ru/"
TARGET_KEYWORDS = [
    "ультразвуковая диагностика",
    "функциональная диагностика",
    "рентгенологический кабинет",
    "справки (абитуриентам)",
    "справки (бассейн)"
]


dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analysis (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(100) NOT NULL,
                    full_text TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('russian', full_text)) STORED
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_analysis_search ON analysis USING GIN(search_vector);")
            conn.commit()
    finally:
        conn.close()



def save_to_db(data: list):
    """Сохраняет данные в базу данных"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            for item in data:
                cur.execute("""
                    INSERT INTO analysis (type, full_text, price)
                    VALUES (%s, %s, %s)
                """, (item['type'], item['full_text'], item['price']))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
    finally:
        conn.close()




def get_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_navigation_links(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    main_li = soup.find("li", class_="item-770")

    if not main_li:
        return links

    for a in main_li.find_all("a"):
        href = a.get("href")
        name = a.get_text(strip=True)

        if not href:
            continue

        abs_url = urljoin(BASE_URL, href)
        link_text = name.lower()
        parent_li = a.find_parent("li")
        section = ""

        if "справок" and "бассейн" in link_text:
            links.append({"name": name, "url": abs_url, "section": "справки (бассейн)"})
        if "справок" and "абитуриентам" in link_text:
            links.append({"name": name, "url": abs_url, "section": "справки (абитуриентам)"})
        else:
            parent_li = a.find_parent("li")
            section_span = None
        while parent_li:
            section_span = parent_li.find("span", class_="separator")
            if section_span:
                section = section_span.get_text(strip=True).lower()
                break
            parent_li = parent_li.find_parent("li")

        if any(keyword in section for keyword in TARGET_KEYWORDS):
            links.append({"name": name, "url": abs_url, "section": section})

    return links


def extract_table_services(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for table in soup.find_all("table"):
        if "Наименование медицинской услуги" in table.get_text():
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    service = cols[0].get_text(strip=True)
                    price_str = cols[1].get_text(strip=True)
                    price = int(re.sub(r'\D', '', price_str)) if price_str else 0
                    results.append({
                        "service": service,
                        "price": price
                    })
    return results


def process_service_page(url: str) -> list:
    try:
        return extract_table_services(get_page(url))
    except Exception as e:
        print(f"Ошибка обработки {url}: {e}")
        return []


def main():
    create_table()
    main_url = urljoin(BASE_URL, "diagnosticheskaya-poliklinika")

    try:
        main_html = get_page(main_url)
        nav_links = extract_navigation_links(main_html)

        db_data = []
        for link in nav_links:
            services = process_service_page(link["url"])
            for service in services:
                db_data.append({
                    "type": link["section"],
                    "full_text": service["service"],
                    "price": service["price"]
                })

        save_to_db(db_data)
        print(f"Успешно сохранено {len(db_data)} записей в БД")

    except Exception as e:
        print(f"Ошибка в основном потоке: {e}")


if __name__ == "__main__":
    main()