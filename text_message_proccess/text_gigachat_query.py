import logging
import os
import requests  # Добавлен недостающий импорт
import dotenv
from gigachat import GigaChat

# Убрал конфликтующий импорт API_KEY
from Utils.GigachatUtils import get_last_file_id, get_auth_token


def get_answer_to_faq(user_message):
    dotenv.load_dotenv()

    API_KEY = os.getenv('GIGACHAT_API_KEY')

    # Инициализируем клиент GigaChat
    giga = GigaChat(
        credentials=API_KEY,
        verify_ssl_certs=False,
    )

    # Получаем токен и ID последнего файла
    auth_token = get_auth_token(API_KEY)
    last_file_id = get_last_file_id(auth_token)


    # Формируем динамический запрос с использованием user_message
    content = f"Постарайся найти ответ в файле информацию о {user_message}. " \
              "Если ответ не найден, дополни его сам! Не упоминай файл в ответе! Не отвечай на посторонние вопросы не касающиеся поликлиники! - это важно!"

    try:
        # Отправляем запрос с использованием полученных параметров
        result = giga.chat({
            "messages": [{
                "role": "user",
                "content": content,  # Используем динамическое содержимое
                "attachments": [last_file_id]
            }],
            "temperature": 0.5
        })
        print(result)
        return result.choices[0].message.content

    except requests.RequestException as e:
        # Логируем ошибку и возвращаем понятное сообщение
        print(f"Ошибка при выполнении запроса: {str(e)}")
        return "Произошла ошибка при обработке запроса"

def get_clinic_info():

    dotenv.load_dotenv()

    API_KEY = os.getenv('GIGACHAT_API_KEY')

    # Инициализируем клиент GigaChat
    giga = GigaChat(
        credentials=API_KEY,
        verify_ssl_certs=False
    )

    # Получаем токен и ID последнего файла
    auth_token = get_auth_token(API_KEY)
    last_file_id = get_last_file_id(auth_token)


    # Формируем динамический запрос с использованием user_message
    content = f"Найди только в файле информацию о работе Диагностической поликлиники блок {"Расписание"} (часы работы, адрес) и т.д. " \
              "Ничего не придумывай сам! Если данных нет, верни: Не найдено"

    try:
        # Отправляем запрос с использованием полученных параметров
        result = giga.chat({
            "messages": [{
                "role": "user",
                "content": content,  # Используем динамическое содержимое
                "attachments": [last_file_id]
            }],
            "temperature": 0.001
        })
        return result.choices[0].message.content

    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")
        return "Произошла ошибка при обработке запроса"