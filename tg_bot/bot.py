import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import BOT_TOKEN
from tg_bot.handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    """
    Точка входа. Инициализирует бота и запускает long-polling.
    """
    # Инициализация бота с токеном
    bot = Bot(token=BOT_TOKEN)
    
    # Инициализация диспетчера
    dp = Dispatcher()
    
    # Подключение роутера с хэндлерами
    dp.include_router(router)
    
    print("🤖 Бот запущен! Ждет голосовых...")
    
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
