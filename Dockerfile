FROM python:3.13-slim


# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    portaudio19-dev \
    ffmpeg \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта
COPY . .

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения с помощью uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
