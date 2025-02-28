import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем токен из переменных среды
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Приветствие нового пользователя
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я бот для курьеров. Вот что я умею:\n"
        "🚀 /help – список команд\n"
        "📌 /rules – правила чата\n"
        "📊 /stats – статистика\n"
        "🔗 /links – полезные ссылки"
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
