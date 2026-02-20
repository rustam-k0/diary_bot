import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Основные настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_URI = os.getenv("OLLAMA_URI", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b-instruct")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env")
