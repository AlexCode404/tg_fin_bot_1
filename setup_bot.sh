#!/bin/bash

# Скрипт для полной установки Telegram бота на пустой сервер
# Использование: 
# curl -O https://raw.githubusercontent.com/your-username/tg_fin_bot_1/main/setup_bot.sh && chmod +x setup_bot.sh
# sudo ./setup_bot.sh YOUR_TELEGRAM_TOKEN YOUR_GITHUB_REPO

# Проверка аргументов
if [ -z "$1" ]; then
  echo "Ошибка: Необходимо указать токен бота."
  echo "Использование: sudo ./setup_bot.sh YOUR_TELEGRAM_TOKEN [YOUR_GITHUB_REPO]"
  exit 1
fi

# Установка переменных
TELEGRAM_TOKEN=$1
GITHUB_REPO=${2:-"https://github.com/AlexCode404/tg_fin_bot_1.git"}
BOT_DIR="/opt/tg_fin_bot"

echo "=== Начало установки Telegram бота ==="
echo "Репозиторий: $GITHUB_REPO"
echo "Директория установки: $BOT_DIR"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
  echo "Ошибка: Этот скрипт должен быть запущен с правами root (используйте sudo)."
  exit 1
fi

# 1. Обновление системы
echo "1. Обновление системы..."
apt update && apt upgrade -y

# 2. Установка необходимых пакетов
echo "2. Установка зависимостей..."
apt install -y apt-transport-https ca-certificates curl software-properties-common git ufw

# 3. Настройка фаервола
echo "3. Настройка фаервола..."
ufw allow 22/tcp
ufw --force enable

# 4. Установка Docker
echo "4. Установка Docker..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
  add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io
  
  # Убеждаемся, что служба Docker запущена и включена
  systemctl enable docker.service
  systemctl start docker.service
else
  echo "Docker уже установлен."
fi

# Проверка существования службы Docker
if ! systemctl list-unit-files | grep -q docker; then
  echo "ВНИМАНИЕ: Служба docker.service не найдена, устанавливаем Docker иначе..."
  apt remove -y docker-ce docker-ce-cli containerd.io
  apt install -y docker.io
  systemctl enable docker.service
  systemctl start docker.service
fi

# 5. Установка Docker Compose
echo "5. Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
  curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
else
  echo "Docker Compose уже установлен."
fi

# 6. Создание директорий для бота
echo "6. Создание директорий..."
mkdir -p "$BOT_DIR"
mkdir -p "$BOT_DIR/exports"

# 7. Клонирование репозитория
echo "7. Клонирование репозитория..."
if [ -d "$BOT_DIR/.git" ]; then
  echo "Репозиторий уже существует, выполняем обновление..."
  cd "$BOT_DIR"
  git pull
else
  git clone "$GITHUB_REPO" "$BOT_DIR"
fi

# 8. Создание .env файла
echo "8. Создание файла с переменными окружения..."
cat > "$BOT_DIR/.env" << EOL
TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN
DATABASE_URI=sqlite:///expenses.db
BOT_LANGUAGE=ru
EOL

# 9. Запуск контейнеров
echo "9. Запуск бота..."
cd "$BOT_DIR"
docker-compose down 2>/dev/null
docker-compose up -d --build

# 10. Создание скрипта для обновления
echo "10. Создание скрипта для обновления..."
cat > "$BOT_DIR/update.sh" << 'EOL'
#!/bin/bash
BOT_DIR="/opt/tg_fin_bot"

echo "=== Обновление бота ==="

cd "$BOT_DIR"
echo "1. Остановка контейнеров..."
docker-compose down

echo "2. Создание резервной копии базы данных..."
if [ -f "expenses.db" ]; then
  cp expenses.db expenses.db.backup
fi

echo "3. Обновление из репозитория..."
git pull

echo "4. Запуск обновленных контейнеров..."
docker-compose up -d --build

echo "5. Проверка состояния..."
docker-compose ps

echo "=== Обновление завершено ==="
EOL

chmod +x "$BOT_DIR/update.sh"

# 11. Проверка состояния
echo "11. Проверка состояния контейнеров..."
docker-compose ps

# 12. Создание скрипта автозапуска
echo "12. Создание скрипта автозапуска..."
cat > "$BOT_DIR/start.sh" << 'EOL'
#!/bin/bash
BOT_DIR="/opt/tg_fin_bot"
cd "$BOT_DIR"
docker-compose up -d
EOL

chmod +x "$BOT_DIR/start.sh"

# 13. Создание службы Systemd для автозапуска
echo "13. Создание службы systemd..."

# Определение доступной службы Docker
DOCKER_SERVICE="docker.service"
if systemctl list-unit-files | grep -q "docker.socket"; then
  DOCKER_SERVICE="docker.socket"
elif systemctl list-unit-files | grep -q "containerd.service"; then
  DOCKER_SERVICE="containerd.service"
elif systemctl list-unit-files | grep -q "docker.io.service"; then
  DOCKER_SERVICE="docker.io.service"
fi

echo "Обнаружена служба Docker: $DOCKER_SERVICE"

cat > "/etc/systemd/system/tgbot.service" << EOL
[Unit]
Description=Telegram Finance Bot
After=$DOCKER_SERVICE
Requires=$DOCKER_SERVICE

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/start.sh
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl enable tgbot.service
systemctl start tgbot.service

# 14. Добавление задания в crontab для автоматического перезапуска
echo "14. Настройка автоматического перезапуска через cron..."
(crontab -l 2>/dev/null; echo "@reboot $BOT_DIR/start.sh > /dev/null 2>&1") | crontab -

echo "=== Установка завершена ==="
echo "Бот установлен и запущен. Он будет автоматически перезапускаться при перезагрузке сервера."
echo ""
echo "Полезные команды:"
echo "- Просмотр логов: docker-compose -f $BOT_DIR/docker-compose.yml logs -f"
echo "- Обновление бота: sudo $BOT_DIR/update.sh"
echo "- Перезапуск бота вручную: $BOT_DIR/start.sh"
echo "- Директория бота: $BOT_DIR"
echo "- База данных: $BOT_DIR/expenses.db" 