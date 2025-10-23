import os
import json
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
STORAGE_ID = int(os.getenv("STORAGE_ID"))
TON_API_KEY = os.getenv("TON_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

GIFTS_FILE = "gifts.json"
STORAGE_FILE = "storage_gifts.json"

def load_data(file):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_gifts = load_data(GIFTS_FILE)
storage_gifts = load_data(STORAGE_FILE)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"🎁 Привет, {message.from_user.first_name}!")

@dp.message(Command("addgift"))
async def add_gift(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Нет прав")
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer("⚠️ /addgift <@username> <название> <фон>")
        return

    username, gift_name, gift_bg = args[1], args[2], args[3]
    if not username.startswith("@"):
        await message.answer("❌ username должен быть с @")
        return

    gift = {"name": gift_name, "bg": gift_bg}
    user_gifts.setdefault(username, []).append(gift)
    storage_gifts.setdefault(str(STORAGE_ID), []).append(gift)
    save_data(GIFTS_FILE, user_gifts)
    save_data(STORAGE_FILE, storage_gifts)

    await message.answer(f"✅ Подарок *{gift_name}* выдан пользователю {username}", parse_mode="Markdown")

@dp.message(Command("inventory"))
async def inventory(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
    gifts = user_gifts.get(username, [])
    if not gifts:
        await message.answer("🎁 У вас пока нет подарков.")
        return
    text = "🎁 Ваши подарки:\n\n" + "\n".join([f"- {g['name']} ({g['bg']})" for g in gifts])
    await message.answer(text)

@dp.message(Command("withdraw"))
async def withdraw(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
    gifts = user_gifts.get(username, [])
    if not gifts:
        await message.answer("❌ Нет подарков для вывода")
        return
    await message.answer(
        f"💸 Чтобы вывести подарок, отправьте 25 звёзд на @giftroyaletransfer.\n"
        f"После оплаты бот подтвердит вывод."
    )

async def check_transactions():
    last_tx = None
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {TON_API_KEY}"}
                async with session.get(
                    f"https://tonapi.io/v2/blockchain/getTransactions?account={STORAGE_ID}&limit=5",
                    headers=headers
                ) as resp:
                    data = await resp.json()

            txs = data.get("transactions", [])
            if not txs:
                await asyncio.sleep(60)
                continue

            latest = txs[0]["hash"]
            if latest != last_tx:
                last_tx = latest
                sender = txs[0].get("in_msg", {}).get("source", "")
                amount = txs[0].get("in_msg", {}).get("value", 0)
                stars = int(amount) / 1_000_000_000

                if stars >= 25:
                    await bot.send_message(ADMIN_ID, f"💰 Получено {stars} звёзд от {sender}\n✅ Вывод подтверждён")
        except Exception as e:
            print("Ошибка проверки транзакций:", e)

        await asyncio.sleep(60)

async def main():
    asyncio.create_task(check_transactions())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
