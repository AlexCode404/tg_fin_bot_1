FROM python:3.9.2-slim

WORKDIR /app

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY . .

# Создание директории для экспортов
RUN mkdir -p exports && chmod 777 exports

# Запуск бота
CMD ["python", "bot.py"] 