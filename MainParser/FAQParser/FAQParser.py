import requests
from bs4 import BeautifulSoup
import json
import pdfplumber
from io import BytesIO
import os

url_instructions = 'https://clinica.chitgma.ru/images/documents/pravilapodgotovki.pdf'
url_schedule = 'https://clinica.chitgma.ru/diagnosticheskaya-poliklinika'
url_schedule_lab = 'https://clinica.chitgma.ru/informatsiya-po-otdeleniyu-12'


# сохранение JSON в TXT
def save_to_text(filename):
    with open(filename, 'r', encoding='utf-8') as json_file:
        content = json_file.read()  # считываем

    text_filename = filename.replace('.json', '.txt')  # даем название в другом формате
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        text_file.write(content)  # записываем


# скачивание пдф-документа
def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()  # проверка на ошибки запроса
    return BytesIO(response.content)  # возвращаем содержимое PDF как поток


# получение инструкций к анализам
def extract_tests_and_instructions(pdf_file):
    analysis_dict = {}

    with pdfplumber.open(pdf_file) as pdf:
        current_analysis = None  # переменная текущего анализа
        current_instruction = ""

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line:  # пропускаем пустые строки
                        continue
                    keywords = ["Вы должны подготовить себя к исследованию следующим образом",
                                "Общие правила забора крови",
                                "Общий анализ мочи",
                                "Анализ мочи по Нечипоренко",
                                "Требования к сдаче анализов на бактериологическое исследование",
                                "Требования к забору мочи для микробиологического исследования",
                                "Требования к забору мокроты для микробиологического исследования",
                                "Требования к забору материала из зева и ротовой полости на микрофлору",
                                "Требования к забору материала для исследования кала на дисбактериоз",
                                "Требования к сдаче анализов на ПЦР- исследование",
                                "Особенности взятия клинического материала из влагалища",
                                "Особенности взятия клинического материала из уретры у женщин",
                                "Особенности взятия клинического материала из уретры у мужчин",
                                "Особенности взятия эякулята (семенной жидкости)",
                                "Взятия клинического материала с крайней плоти головки полового члена (ГПЧ)",
                                "Подготовка пациента к дуплексному сканированию",  # 2
                                "Подготовка пациента к исследованию эхоангиография",  # 2
                                "Подготовка пациента к Эхо КГ, ЧПЭхоКГ",
                                "Подготовка пациента к ЭКГ, ХМЭКГ, СМАД",  # 2
                                "Подготовка пациента к ЭКГ по Холтеру",
                                "Перед проведением исследования Холтеровского Мониторирования",  # 2
                                "Перед проведением исследования СМАД",  # 2
                                "Перед проведением Тредмил теста",
                                "Подготовка к проведению ФВД",
                                "Подговка пациента к методам ЭЭГ, ЭхоЭГ, Вызванных потенциалов",  # 2
                                "Видео ЭЭГ мониторинг",
                                "Подготовка к Электронейромиографии",
                                "Подготовка пациента к водородному дыхательному тесту",
                                "Подготовка к УЗИ органов брюшной полости",
                                "Подготовка к УЗИ почек и мочевого пузыря",
                                "Подготовка к УЗИ МАЛОГО ТАЗА (трансабдоминальное)",
                                "Подготовка к УЗИ молочных желез",
                                "При выполнении одновременно УЗИ органов брюшной полости и УЗИ органов малого"  # 2
                                ]
                    if any(keyword in line for keyword in keywords):
                        if current_analysis:
                            analysis_dict[current_analysis] = current_instruction.strip()

                        current_analysis = line  # устанавливаем новый анализ
                        current_instruction = ""  # сбрасываем инструкции для нового анализа

                    elif current_analysis:  # если текущий анализ установлен, добавляем текст инструкции
                        current_instruction += line + " "

        # сохраняем последние инструкции после выхода из цикла
        if current_analysis:
            analysis_dict[current_analysis] = current_instruction.strip()

    return {k: v for k, v in analysis_dict.items()}


# сохранение для инструкций
def save_to_json_instr(data, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)  # сохраняем данные в JSON


# получение расписания
def fetch_schedule(url):
    # получаем HTML-код страницы
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при получении страницы: {response.status_code}")
        return None

    # парсим HTML-код
    soup = BeautifulSoup(response.text, 'html.parser')

    # извлекаем общую информацию
    article_body = soup.find('div', itemprop='articleBody')
    general_info = article_body.get_text(strip=True) if article_body else "Информация не найдена."

    # ищем таблицу
    schedule_table = soup.find('table', style=True)

    if not schedule_table:
        print("Расписание не найдено.")
        return None

    # извлекаем данные из таблицы
    schedule_data = []
    for row in schedule_table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) >= 3:
            entry = {
                "Где": columns[0].get_text(strip=True),
                "Расписание": columns[1].get_text(strip=True)
            }
            schedule_data.append(entry)

    return general_info, schedule_data


# сохранение расписания
def save_to_json_schedule(general_info, schedule_data, filename):
    data = {
        "Общая информация": general_info,
        "Расписание": schedule_data
    }
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# получение расписания лаборатории
def parse_schedule_lab(url):
    # получаем HTML-код страницы
    response = requests.get(url)

    # проверяем успешность запроса
    if response.status_code != 200:
        raise Exception(f"Ошибка при загрузке страницы: {response.status_code}")

    # парсим HTML-код
    soup = BeautifulSoup(response.text, 'html.parser')

    schedule = {}  # словарь для хранения расписания

    # находим все элементы <p> на странице с определенным стилем
    paragraphs = soup.find_all('p',
                               style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 1.5; color: #21347d;")

    for paragraph in paragraphs:
        text = paragraph.get_text(strip=True)

        if ':' in text:
            day, hours = text.split('0', 1)
            schedule[day.strip()] = hours.strip()

    return schedule


# сохранение расписания таблицы
def save_to_json_schedule_lab(data, filename='scheduleLab.json'):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def parse(output_file):
    general_info_schedule, schedule_data = fetch_schedule(url_schedule)

    # расписание
    if schedule_data:
        json_filename = 'schedule.json'
        save_to_json_schedule(general_info_schedule, schedule_data, json_filename)

        save_to_text(json_filename)

    # расписание лаборатории
    scheduleLab = parse_schedule_lab(url_schedule_lab)

    save_to_json_schedule_lab(scheduleLab)
    save_to_text('scheduleLab.json')

    # инструкции к анализам
    pdf_file = download_pdf(url_instructions)
    analysis_data = extract_tests_and_instructions(pdf_file)

    json_filename = 'analysis_instructions.json'
    save_to_json_instr(analysis_data, json_filename)

    save_to_text(json_filename)

    # объединение файлов в 1
    file1 = 'schedule.txt'
    file2 = 'scheduleLab.txt'
    file3 = 'analysis_instructions.txt'
    with open(output_file, 'w') as outfile:
        for filename in (file1, file2, file3):
            with open(filename) as infile:
                outfile.write(infile.read())
                outfile.write('\n')

    os.remove('schedule.json')
    os.remove('scheduleLab.json')
    os.remove('analysis_instructions.json')
    os.remove('schedule.txt')
    os.remove('scheduleLab.txt')
    os.remove('analysis_instructions.txt')


