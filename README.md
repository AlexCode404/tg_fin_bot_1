# Telegram Expense Tracking Bot

Этот Telegram бот помогает отслеживать расходы по категориям, создавать статистические отчеты и экспортировать данные в форматах CSV и PDF.

## Функции

- Добавление расходов с указанием суммы и категории
- Просмотр статистики расходов за месяц 
- Экспорт данных в CSV и PDF форматах
- Управление категориями расходов

## Команды бота

- `/add <сумма> <категория>` - добавить расход
- `/stats [месяц]` - сводка расходов за месяц (формат месяца: YYYY-MM)
- `/categories` - список доступных категорий
- `/export [месяц] [формат]` - выгрузка транзакций в CSV/PDF

## Установка и запуск

### Быстрая установка на сервер

Просто скопируйте файлы на сервер и запустите скрипт:

```bash
sudo bash deploy.sh YOUR_TELEGRAM_TOKEN
```

### Обновление бота на сервере

Для обновления:

```bash
bash update.sh
```

### Локальный запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/your-username/tg_fin_bot_1.git
cd tg_fin_bot_1
```

2. Создайте виртуальное окружение (рекомендуется Python 3.9):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или 
.\venv\Scripts\activate   # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` с переменными окружения:

```
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URI=sqlite:///expenses.db
BOT_LANGUAGE=ru
```

5. Запустите бота:

```bash
python bot.py
```

### Запуск через Docker

1. Создайте файл `.env` с переменными окружения
2. Запустите с помощью Docker Compose:

```bash
docker-compose up -d
```

## Технические детали

- Python 3.9
- SQLite для хранения данных
- python-telegram-bot для работы с Telegram API
- Docker и Docker Compose для контейнеризации

## Структура проекта

- `bot.py` - основной файл с логикой бота
- `config.py` - конфигурация с переменными окружения
- `database.py` - работа с базой данных
- `expense_manager.py` - управление расходами
- `export.py` - экспорт данных
- `Dockerfile` и `docker-compose.yml` - для контейнеризации
- `deploy.sh` - скрипт для быстрой установки
- `update.sh` - скрипт для обновления 