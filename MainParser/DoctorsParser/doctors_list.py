import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def get_doctors(base_url: str) -> list:
    """Парсит список врачей с главной страницы."""
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы {base_url}: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    separator = soup.find("span", class_="separator", string=lambda t: t and "Консультации специалистов" in t)
    doctors = []
    if separator:
        parent_li = separator.find_parent("li")
        nested_ul = parent_li.find("ul", class_="nav-child unstyled small")
        if nested_ul:
            for a in nested_ul.find_all("a"):
                name = a.get_text(strip=True)
                href = a.get("href")
                if href:
                    link = urljoin(base_url, href)
                    doctors.append({"name": name, "url": link})
    return doctors

def extract_services_and_prices(html: str) -> list:
    """Извлекает услуги и цены из HTML-таблицы."""
    soup = BeautifulSoup(html, "html.parser")
    results = []
    tables = soup.find_all("table")
    target_table = None
    for table in tables:
        if "Наименование медицинской услуги" in table.get_text():
            target_table = table
            break
    if target_table:
        rows = target_table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                service = cols[0].get_text(strip=True)
                price = cols[1].get_text(strip=True)
                results.append({"service": service, "price": price})
    return results

def parse_service_details(service_str: str) -> dict:
    """Извлекает учёную степень и тип приёма из строки услуги."""
    academic_degree = ''
    type_visit = ''
    degree_pattern = r'(к\.м\.н\.|д\.м\.н\.|профессор)'
    visit_pattern = r'(первичный|повторный)'
    degree_match = re.search(degree_pattern, service_str)
    if degree_match:
        academic_degree = degree_match.group(1)
    visit_match = re.search(visit_pattern, service_str)
    if visit_match:
        type_visit = visit_match.group(1)
    return {'academic_degree': academic_degree, 'type_visit': type_visit}

def process_doctor(doctor: dict) -> dict:
    """Обрабатывает страницу врача и возвращает данные об услугах."""
    url = doctor["url"]
    response = requests.get(url)
    if response.status_code != 200:
        return {"doctor": doctor, "services": []}
    services = extract_services_and_prices(response.text)
    return {"doctor": doctor, "services": services}