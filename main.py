import os
import json
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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


@dp.message()
async def inventory(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
    gifts = user_gifts.get(username, [])
    if not gifts:
        await message.answer("🎁 У вас пока нет подарков.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, gift in enumerate(gifts):
        button = InlineKeyboardButton(
            text=f"{gift['name']} ({gift['bg']}) - вывести за 25⭐",
            callback_data=f"withdraw_{i}"
        )
        keyboard.add(button)

    await message.answer("🎁 Ваши подарки:", reply_markup=keyboard)


@dp.callback_query()
async def handle_withdraw(call: CallbackQuery):
    username = f"@{call.from_user.username}" if call.from_user.username else str(call.from_user.id)
    gifts = user_gifts.get(username, [])
    if not gifts:
        await call.message.edit_text("❌ У вас нет подарков для вывода.")
        return

    index = int(call.data.split("_")[1])
    if index >= len(gifts):
        await call.message.edit_text("❌ Некорректный подарок.")
        return

    gift = gifts[index]
    await call.message.edit_text(
        f"💸 Чтобы вывести {gift['name']}, отправьте 25⭐ на аккаунт @giftroyaletransfer.\n"
        "После оплаты бот автоматически передаст NFT."
    )
    # Логика автоматической проверки и передачи NFT должна быть реализована в check_transactions()


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
                    # Тут нужно найти, какой подарок выводит пользователь и передать NFT
                    await bot.send_message(ADMIN_ID, f"💰 Получено {stars}⭐ от {sender}\n✅ Вывод подтверждён")
        except Exception as e:
            print("Ошибка проверки транзакций:", e)

        await asyncio.sleep(60)


async def main():
    asyncio.create_task(check_transactions())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    

