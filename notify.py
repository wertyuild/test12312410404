import json
import asyncio
from aiogram import Bot
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, encoding='utf-8') as f:
    config = json.load(f)
BOT_TOKEN = config['bot_token']
ADMINS = config['admin_ids']
bot = Bot(token=BOT_TOKEN)

async def notify_admins(username: str, stars: int, payment_method: str = None, price: float = None):
    text = f"\u2b50 Новый заказ!\nПользователь: @{username}\nКоличество звёзд: {stars}"
    if payment_method:
        text += f"\nСпособ оплаты: {payment_method}"
    if price is not None:
        text += f"\nСумма: {price} ₽"
    for admin in ADMINS:
        try:
            await bot.send_message(admin, text)
        except Exception as e:
            print(f"Ошибка отправки админу {admin}: {e}")

def notify(username, stars, payment_method=None, price=None):
    asyncio.create_task(notify_admins(username, stars, payment_method, price)) 