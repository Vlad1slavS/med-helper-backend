import os

import dotenv
import psycopg2

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_categories():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT type FROM analysis")  # Замените `procedures` на свою таблицу
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return categories