new file mode 100644
"""Основной файл Telegram-бота AI-ВЕТЕРИНАР (aiogram 3.x)."""

import asyncio
import logging
import uvicorn
from threading import Thread

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import (

ReplyKeyboardMarkup,
KeyboardButton,
WebAppInfo,
MenuButtonWebApp,

)
from aiogram.enums import ParseMode

from config import BOT_TOKEN, WEBAPP_URL, API_PORT
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):

"""Обработка команды /start."""
webapp_url = WEBAPP_URL
keyboard = ReplyKeyboardMarkup(
text
  keyboard=[
text
      [
text
          KeyboardButton(
text
              text="🐾 Открыть AI-Ветеринар",
text
              web_app=WebAppInfo(url=webapp_url),
text
          )
text
      ]
text
  ],
text
  resize_keyboard=True,
text
  one_time_keyboard=False,
)
await message.answer(
text
  "🐾 <b>Добро пожаловать в AI-ВЕТЕРИНАР!</b>\n\n"
text
  "Я помогу вам получить ветеринарную консультацию для вашего питомца.\n\n"
text
  "Нажмите кнопку ниже, чтобы открыть приложение и выбрать специализацию врача.\n\n"
text
  "⚠️ <i>Помните: ИИ не заменяет очную консультацию ветеринара!</i>",
text
  reply_markup=keyboard,
)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):

"""Обработка данных от Web App."""
logger.info(f"Web App data from {message.from_user.id}: {message.web_app_data.data}")
await message.answer("✅ Данные получены!")

def run_api_server():

"""Запуск FastAPI-сервера в отдельном потоке."""
from api.server import app as fastapi_app
uvicorn.run(fastapi_app, host="0.0.0.0", port=API_PORT, log_level="info")

async def main():

"""Главная функция запуска."""
Инициализация БД
await init_db()
Запуск API-сервера в отдельном потоке
api_thread = Thread(target=run_api_server, daemon=True)
api_thread.start()
logger.info(f"API server started on port {API_PORT}")
Запуск бота
logger.info("Starting bot...")
await dp.start_polling(bot)

if name == "main":

asyncio.run(main())
