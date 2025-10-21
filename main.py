import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

TOKEN = "твой_токен_бота"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Это Gift Royale 🖤")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
