import json
from aiogram import Bot, Dispatcher, types
import asyncio
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../backend/config.json')

with open(CONFIG_PATH, encoding='utf-8') as f:
    config = json.load(f)

BOT_TOKEN = config['8149655584:AAE8F6i5aqykzQrO7wS2gMaC9IafZzEXgMM']
ADMINS = config['1364958631']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def notify_admins(username: str, stars: int):
    text = f"\u2b50 Новый заказ!\nПользователь: @{username}\nКоличество звёзд: {stars}"
    for admin in ADMINS:
        try:
            if admin.get('id'):
                await bot.send_message(admin['id'], text)
            elif admin.get('username'):
                await bot.send_message(f"@{admin['username']}", text)
        except Exception as e:
            print(f"Ошибка отправки админу {admin}: {e}")

# Пример запуска уведомления (для теста)
if __name__ == "__main__":
    asyncio.run(notify_admins("testuser", 5)) 