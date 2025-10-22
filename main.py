import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

GIFTS_FILE = "gifts.json"

def load_gifts():
    if not os.path.exists(GIFTS_FILE):
        with open(GIFTS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(GIFTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_gifts(data):
    with open(GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_gifts = load_gifts()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"🎁 Привет, {message.from_user.first_name}! Добро пожаловать в Gift Royale 🖤")

@dp.message(Command("addgift"))
async def add_gift(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 У вас нет прав использовать эту команду.")
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer("⚠️ Использование: /addgift <@username> <название> <фон>")
        return

    username, gift_name, gift_bg = args[1], args[2], args[3]

    if not username.startswith("@"):
        await message.answer("❌ Укажите username в формате @username")
        return

    user_gifts.setdefault(username, []).append({"name": gift_name, "bg": gift_bg})
    save_gifts(user_gifts)

    await message.answer(f"✅ Подарок *{gift_name}* с фоном *{gift_bg}* выдан пользователю {username}.", parse_mode="Markdown")

@dp.message(Command("inventory"))
async def inventory(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
    gifts = user_gifts.get(username, [])

    if not gifts:
        await message.answer("🎁 No Gifts yet.\nBuy one in our Shop or send it to @giftroyaletransfer")
        return

    text = "🎁 Ваши подарки:\n\n" + "\n".join([f"- {g['name']} ({g['bg']})" for g in gifts])
    await message.answer(text)

@dp.message(Command("profile"))
async def profile(message: types.Message):
    await message.answer(f"👤 Профиль @{message.from_user.username or message.from_user.id}\n💬 Support: @StarGiftPlaceBot")

async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
