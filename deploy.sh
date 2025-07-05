#!/bin/bash

# Скрипт для автоматического развертывания Telegram бота
# Запускать с sudo: sudo bash deploy.sh YOUR_TELEGRAM_TOKEN

# Проверка наличия токена как аргумента
if [ -z "$1" ]; then
  echo "Ошибка: Необходимо указать токен бота."
  echo "Использование: sudo bash deploy.sh YOUR_TELEGRAM_TOKEN"
  exit 1
fi

TELEGRAM_TOKEN=$1
BOT_DIR="$HOME/tg_fin_bot"

echo "=== Начало установки ==="

# 1. Обновление системы
echo "Обновление системы..."
apt update && apt upgrade -y

# 2. Установка необходимых пакетов
echo "Установка зависимостей..."
apt install -y apt-transport-https ca-certificates curl software-properties-common ufw

# 3. Настройка фаервола
echo "Настройка фаервола..."
ufw allow 22/tcp
ufw --force enable

# 4. Установка Docker
echo "Установка Docker..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
  add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io
  usermod -aG docker $SUDO_USER
else
  echo "Docker уже установлен."
fi

# 5. Установка Docker Compose
echo "Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
  curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
else
  echo "Docker Compose уже установлен."
fi

# 6. Создание директорий для бота
echo "Создание директорий..."
mkdir -p "$BOT_DIR"
mkdir -p "$BOT_DIR/exports"

# 7. Копирование файлов проекта
echo "Копирование файлов проекта..."
cp -r ./* "$BOT_DIR/"

# 8. Создание .env файла
echo "Создание файла с переменными окружения..."
cat > "$BOT_DIR/.env" << EOL
TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN
DATABASE_URI=sqlite:///expenses.db
BOT_LANGUAGE=ru
EOL

# 9. Запуск контейнеров
echo "Запуск бота..."
cd "$BOT_DIR"
docker-compose down 2>/dev/null
docker-compose up -d --build

# 10. Проверка состояния
echo "Проверка состояния контейнеров..."
docker-compose ps

echo "=== Установка завершена ==="
echo "Бот запущен и будет автоматически перезапускаться."
echo "Для просмотра логов: docker-compose -f $BOT_DIR/docker-compose.yml logs -f"
echo "Данные сохраняются в: $BOT_DIR/expenses.db" 