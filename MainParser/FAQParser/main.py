import os

import dotenv

import FAQParser
from Utils import GigachatUtils
from Utils.GigachatUtils import get_all_files, delete_file, upload_file


def main():
    dotenv.load_dotenv()

    FILENAME = "merged_file.txt"
    API_KEY = os.getenv("GIGACHAT_API_KEY")

    FAQParser.parse(FILENAME)
    auth_token = GigachatUtils.get_auth_token(API_KEY)
    files = get_all_files(auth_token)

    existing_files = [f for f in files if f.get('filename') == FILENAME]
    deleted_ids = []

    new_file = upload_file(API_KEY, FILENAME)
    if new_file:
        print(f"Загружен новый файл с ID: {new_file.id_}")

        for file in existing_files:
            if delete_file(auth_token, file['id']):
                deleted_ids.append(file['id'])
                print(f"Удален файл с ID: {file['id']}")
    else:
        print("Ошибка загрузки файла. Старые файлы не удаляются.")

if __name__ == '__main__':
    main()