import os
from dotenv import load_dotenv
import requests
import json
from Utils.GigachatUtils import get_auth_token


load_dotenv()

API_KEY = os.getenv("GIGACHAT_API_KEY")

COMMANDS = ["запись", "отмена записи", "цена", "маршрут"]

def get_chat_completion(user_message):
    content = (
        f"Обработай голосовое сообщение пользователя: \"{user_message}\" "
        f"и верни JSON с подходящей командой. Доступные команды: {COMMANDS}. "
        f"\n\nПравила формирования ответа:"
        f"\n1. Если это команда записи, верни JSON с ключами: 'command' (команда), 'doctor' (врач), 'date' (дата (день, месяц) без года!), 'time' (время)."
        f"\n2. Если уточняется стоимость, верни JSON с ключами: 'command' ('цена') и 'service' (процедура или врач)."
        f"\n3. Если данные неясны, оставь соответствующие поля пустыми."
        f"\n4. Исправляй ошибки в тексте."
        f"\n5. Ответ должен содержать только JSON, без поясняющего текста."
    )

    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    auth_token = get_auth_token(API_KEY)

    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": "GigaChat-Max",  # Используемая модель
        "messages": [
            {
                "role": "user",  # Роль отправителя (пользователь)
                "content": content  # Содержание сообщения
            }
        ],
        "temperature": 1,  # Температура генерации
        "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
        "n": 1,  # Количество возвращаемых ответов
        "stream": False,  # Потоковая ли передача ответов
        "max_tokens": 512,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1,  # Штраф за повторения
        "update_interval": 0  # Интервал обновления (для потоковой передачи)
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Тип содержимого - JSON
        'Accept': 'application/json',  # Принимаем ответ в формате JSON
        'Authorization': f'Bearer {auth_token}'  # Токен авторизации
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
        return -1