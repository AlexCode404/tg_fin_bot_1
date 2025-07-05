# Развертывание Telegram бота на сервере

## Требования
- Docker
- Docker Compose
- Доступ к серверу через SSH

## Шаги по развертыванию

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/tg_fin_bot_1.git
cd tg_fin_bot_1
```

### 2. Настройка переменных окружения
Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

Отредактируйте файл `.env` и укажите ваш токен Telegram бота:
```bash
nano .env
```

```
TELEGRAM_BOT_TOKEN=your_actual_token_from_botfather
DATABASE_URI=sqlite:///expenses.db
BOT_LANGUAGE=ru
```

### 3. Сборка и запуск с Docker Compose
```bash
docker-compose up -d --build
```

Эта команда:
- Соберет Docker-образ согласно Dockerfile
- Запустит контейнер в фоновом режиме
- Настроит автоматический перезапуск контейнера
- Передаст переменные окружения из .env в контейнер

### 4. Проверка логов
```bash
docker-compose logs -f
```

### 5. Обновление бота
Когда вы захотите обновить бота:
```bash
git pull  # Получить последние изменения из репозитория
docker-compose down  # Остановить текущий контейнер
docker-compose up -d --build  # Пересобрать и запустить обновленную версию
```

### 6. Доступ к базе данных
База данных SQLite сохраняется локально и монтируется внутрь контейнера:
```bash
sqlite3 expenses.db
```

### 7. Резервное копирование
Для создания резервной копии базы данных:
```bash
cp expenses.db expenses.db.backup
```

## Важные замечания

- Контейнер настроен на автоматический перезапуск (restart: always)
- База данных (expenses.db) и экспортированные файлы (exports/) хранятся вне контейнера
- Для изменения часового пояса отредактируйте переменную TZ в docker-compose.yml
- НИКОГДА не добавляйте файл .env в репозиторий! Он содержит секретные данные 