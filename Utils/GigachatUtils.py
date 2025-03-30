import logging
import os
from dotenv import load_dotenv
import requests
import uuid

from gigachat import GigaChat


def get_auth_token(api_key, scope='GIGACHAT_API_PERS'):

    logging.info(api_key)

    rq_uid = str(uuid.uuid4())
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {api_key}'
    }
    payload = {'scope': scope}

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Ошибка получения токена: {str(e)}")
        raise



def get_all_files(auth_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/files"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"Ошибка получения файлов: {str(e)}")
        return []


def delete_file(auth_token, file_id):
    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{file_id}/delete"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Ошибка удаления файла {file_id}: {str(e)}")
        return False

def get_last_file_id(auth_token):

    url = "https://gigachat.devices.sberbank.ru/api/v1/files"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        # Получаем список всех файлов
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Проверка на успешный ответ
        files_data = response.json().get('data', [])

        if not files_data:
            print("Файлы не найдены.")
            return None

        # Предполагаем, что файлы отсортированы по времени загрузки, и последний файл будет последним в списке
        last_file = files_data[-1]
        return last_file.get('id')

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных о файлах: {e}")
        return None

def upload_file(API_KEY, file_name):

    giga = GigaChat(
        credentials=API_KEY,
        verify_ssl_certs=False
    )

    new_file = giga.upload_file(open(file_name, "rb"), purpose="general")
    return new_file

