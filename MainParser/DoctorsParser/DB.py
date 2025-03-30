import os

import dotenv
import psycopg2
import re
from MainParser.DoctorsParser.doctors_list import parse_service_details

def create_table(conn):
    """Создаёт таблицу в PostgreSQL, если она не существует."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                id SERIAL PRIMARY KEY,
                specialization TEXT,
                academic_degree TEXT,
                type_visit TEXT,
                price INTEGER,
                UNIQUE(specialization, academic_degree, type_visit)
            );
        """)
        conn.commit()

def insert_service(conn, specialization, academic_degree, type_visit, price):
    """Добавляет или обновляет данные в таблице."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO consultations (specialization, academic_degree, type_visit, price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (specialization, academic_degree, type_visit)
            DO UPDATE SET price = EXCLUDED.price;
        """, (specialization, academic_degree, type_visit, price))
        conn.commit()

def store_services(services_data: list):
    dotenv.load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL")

    conn = psycopg2.connect(DATABASE_URL)
    create_table(conn)

    for res in services_data:
        doctor = res['doctor']
        services = res['services']
        specialization = doctor['name']
        for service in services:
            service_name = service['service']
            price_str = service['price']
            details = parse_service_details(service_name)
            academic_degree = details['academic_degree']
            type_visit = details['type_visit']

            price = None
            if price_str:
                price_clean = re.sub(r'[^\d]', '', price_str)
                if price_clean:
                    price = int(price_clean)

            try:
                insert_service(conn, specialization, academic_degree, type_visit, price)
            except Exception as e:
                print(f"Ошибка при вставке данных: {e}")
                conn.rollback()

    conn.close()