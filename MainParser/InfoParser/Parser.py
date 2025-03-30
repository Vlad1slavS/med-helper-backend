import json
import os
import re

import dotenv
import psycopg2
import requests
from bs4 import BeautifulSoup

URL = "https://clinica.chitgma.ru/diagnosticheskaya-poliklinika"

dotenv.load_dotenv()

def get_page_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_schedule(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    result = {
        "addresses": [],
        "phone": "8(3022)73-70-73"
    }


    addresses_data = {}

    # Проходим по всем строкам таблицы
    for tr in soup.find_all('tr'):
        # Ищем строку с адресом
        p_tag = tr.find('p', style="text-align: center;")
        if p_tag:
            address_text = p_tag.get_text(strip=True)
            # Фильтруем по шаблону (например, адрес должен содержать "ул.")
            if not re.search(r'ул\.', address_text, re.IGNORECASE):
                continue

            next_tr = tr.find_next_sibling('tr')
            if not next_tr:
                continue

            first_td = next_tr.find('td')
            if not first_td:
                continue

            header_text = first_td.get_text(strip=True).lower()
            schedule_type = None
            if "диагностическая" in header_text:
                schedule_type = "diagnostic_schedule"
            elif "сдачи анализов" in header_text:
                # Различаем режим сдачи анализов в поликлинике и лаборатории
                if "поликлинике" in header_text:
                    schedule_type = "diagnostic_schedule"
                elif "лаборатории" in header_text:
                    schedule_type = "lab_schedule"
            # Если тип расписания не определён — пропускаем
            if not schedule_type:
                continue

            table_tag = next_tr.find('table')
            if not table_tag:
                continue

            schedule = []
            for row in table_tag.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    schedule.append({
                        "days": cols[0].get_text(strip=True),
                        "hours": cols[1].get_text(strip=True).replace('\n', ' ')
                    })

            # Если расписание пустое, пропускаем этот адрес
            if not schedule:
                continue

            # Инициализируем структуру для адреса, если он ещё не добавлен
            if address_text not in addresses_data:
                addresses_data[address_text] = {
                    "diagnostic_schedule": [],
                    "lab_schedule": []
                }
            addresses_data[address_text][schedule_type] = schedule

    # Преобразуем словарь в список, добавляя только те адреса, где есть хотя бы одно расписание
    for address, schedules in addresses_data.items():
        if schedules.get("diagnostic_schedule") or schedules.get("lab_schedule"):
            result["addresses"].append({
                "address": address,
                "diagnostic_schedule": schedules.get("diagnostic_schedule", []),
                "lab_schedule": schedules.get("lab_schedule", [])
            })
    return result



def save_to_db(data: dict):

    dotenv.load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL")

    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        # Создаем таблицу (если не существует)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id SERIAL PRIMARY KEY,
                info JSONB NOT NULL
            )
        """)

        # Удаляем старые записи
        cur.execute("DELETE FROM schedule")

        # Вставляем новые данные
        cur.execute(
            "INSERT INTO schedule (info) VALUES (%s)",
            (json.dumps(data, ensure_ascii=False),)
        )
        conn.commit()


# Запуск парсера
html_table = get_page_content(URL)
parsed_data = parse_schedule(html_table)
print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
save_to_db(parsed_data)