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

### Деплой на сервер через CI/CD

Для автоматического деплоя на сервер:

1. Настройте сервер согласно инструкциям в [SERVER_SETUP.md](SERVER_SETUP.md)
2. Настройте GitHub секреты:
   - `SSH_PRIVATE_KEY` - приватный SSH ключ для доступа
   - `SERVER_IP` - IP-адрес сервера
   - `SERVER_USER` - имя пользователя на сервере (deployer)
   - `TELEGRAM_BOT_TOKEN` - токен Telegram бота
3. Запушьте изменения в ветку main/master для автоматического деплоя

## Технические детали

- Python 3.9
- SQLite для хранения данных
- python-telegram-bot для работы с Telegram API
- Docker и Docker Compose для контейнеризации
- GitHub Actions для CI/CD
- Prometheus и Grafana для мониторинга

## Структура проекта

- `bot.py` - основной файл с логикой бота
- `config.py` - конфигурация с переменными окружения
- `database.py` - работа с базой данных
- `expense_manager.py` - управление расходами
- `export.py` - экспорт данных
- `Dockerfile` и `docker-compose.yml` - для контейнеризации
- `.github/workflows/` - CI/CD пайплайны
- `tests/` - модульные тесты
- `monitoring/` - конфигурация мониторинга

## DevOps подход

- **CI/CD**: Автоматический деплой через GitHub Actions
- **Контейнеризация**: Docker для изоляции и переносимости
- **Мониторинг**: Prometheus и Grafana для отслеживания производительности
- **Тестирование**: Автоматические тесты при каждом коммите
- **Секреты**: Безопасное хранение токенов через переменные окружения 