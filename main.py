import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()  
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура с нужными кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 PvP"), KeyboardButton(text="💼 Профиль"), KeyboardButton(text="🎒 Инвентарь")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🎁 Добро пожаловать в Gift Royale 🖤",
        reply_markup=keyboard
    )

# Обработка кнопок
@dp.message()
async def handle_buttons(message: types.Message):
    if message.text == "🎮 PvP":
        await message.answer("PvP начался! ⚔️\nИгроков пока нет...")
    elif message.text == "💼 Профиль":
        await message.answer(f"Ваш профиль, {message.from_user.first_name} 🖤")
    elif message.text == "🎒 Инвентарь":
        await message.answer("Ваш инвентарь пуст 👜\nСкоро можно будет добавить предметы!")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
