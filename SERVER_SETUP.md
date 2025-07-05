# Настройка сервера для деплоя Telegram бота

Данная инструкция описывает настройку Ubuntu сервера для развертывания Telegram бота с использованием Docker и CI/CD.

## Требования
- Ubuntu 20.04 LTS или новее
- Доступ по SSH с правами sudo

## 1. Базовая настройка сервера

### Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### Настройка файрвола
```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP (если нужен)
sudo ufw allow 443/tcp # HTTPS (если нужен)
sudo ufw enable
```

## 2. Установка Docker и Docker Compose

### Установка Docker
```bash
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
```

### Добавление пользователя в группу docker
```bash
sudo usermod -aG docker $USER
# Перезайдите в систему или выполните:
newgrp docker
```

### Установка Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 3. Настройка CI/CD с GitHub Actions

### Создание пользователя для деплоя
```bash
sudo adduser deployer
sudo usermod -aG docker deployer
```

### Настройка SSH ключей для GitHub Actions
```bash
# На локальной машине (не на сервере):
ssh-keygen -t ed25519 -f ~/.ssh/github_actions_deploy -C "github-actions-deploy"

# Скопируйте публичный ключ на сервер:
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub deployer@your_server_ip

# Затем добавьте приватный ключ (содержимое файла ~/.ssh/github_actions_deploy)
# в секреты GitHub репозитория с именем SSH_PRIVATE_KEY
```

### Добавьте другие секреты в GitHub
- `SERVER_IP`: IP-адрес вашего сервера
- `SERVER_USER`: deployer
- `TELEGRAM_BOT_TOKEN`: Токен вашего Telegram бота

## 4. Создание структуры директорий
```bash
# На сервере, под пользователем deployer:
mkdir -p ~/tg_fin_bot
mkdir -p ~/tg_fin_bot/exports
```

## 5. Запуск мониторинга (опционально)

Для запуска системы мониторинга:
```bash
cd ~/tg_fin_bot
docker-compose -f docker-compose.monitoring.yml up -d
```

Доступ к мониторингу:
- Prometheus: http://your_server_ip:9090
- Grafana: http://your_server_ip:3000 (логин: admin, пароль: admin)

## 6. Настройка логирования

Для сбора логов контейнеров можно установить Filebeat:
```bash
sudo apt install -y filebeat
sudo systemctl enable filebeat
sudo systemctl start filebeat
``` 