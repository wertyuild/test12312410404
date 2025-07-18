import json
import asyncio
import os
from aiogram import Bot

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, encoding='utf-8') as f:
    config = json.load(f)
BOT_TOKEN = config['bot_token']
ADMINS = config['admins']
bot = Bot(token=BOT_TOKEN)

async def notify_admins(username: str, stars: int, payment_method: str = None, price: float = None):
    text = f"\u2b50 Новый заказ!\nПользователь: @{username}\nКоличество звёзд: {stars}"
    if payment_method:
        text += f"\nСпособ оплаты: {payment_method}"
    if price is not None:
        text += f"\nСумма: {price} ₽"
    for admin in ADMINS:
        try:
            if admin.get('id'):
                await bot.send_message(admin['id'], text)
            elif admin.get('username'):
                await bot.send_message(f"@{admin['username']}", text)
        except Exception:
            pass

def notify(username: str, stars: int, payment_method: str = None, price: float = None):
    asyncio.run(notify_admins(username, stars, payment_method, price)) 