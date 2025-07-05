import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла, если он существует
load_dotenv()

# Telegram Bot Configuration
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7328210279:AAEuM2m0c1pPjG8k1FbrglvHadiIgXxqE4k")

# Database Configuration
DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///expenses.db")

# Available expense categories
CATEGORIES = [
    "food", 
    "transport", 
    "entertainment", 
    "utilities", 
    "rent", 
    "healthcare", 
    "education", 
    "shopping", 
    "travel", 
    "other"
]

# Default language
LANGUAGE = os.environ.get("BOT_LANGUAGE", "ru")  # Russian language 