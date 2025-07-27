import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keyboards import get_main_menu_keyboard, get_subscription_keyboard
from handlers import register_user_handlers
from admin_handlers import register_admin_handlers
from config import STARS_PER_REFERRAL

API_TOKEN = '7991051885:AAGgVt3IlyQNjDaCfLYxOsUtfQpBu7HHqsA'
SUBGRAM_API_KEY = 'e2851fc57f083719da32f7c8a99e4c9ee7a0b3d4c1313cb4e631aa7fb2ab203f'
SUBGRAM_REQUEST_OP_URL = 'https://api.subgram.ru/request-op/'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- Subgram API ---
class SubgramAPI:
    def __init__(self):
        self.api_key = SUBGRAM_API_KEY
        self.headers = {
            'Auth': self.api_key,
            'Content-Type': 'application/json'
        }

    async def request_subscription_block(self, user_id: int, chat_id: int, first_name: str = None, language_code: str = 'ru', is_premium: bool = False) -> dict:
        data = {
            "UserId": str(user_id),
            "ChatId": str(chat_id),
            "first_name": first_name,
            "language_code": language_code,
            "Premium": is_premium,
            "MaxOP": 10,
            "action": "subscribe"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SUBGRAM_REQUEST_OP_URL, headers=self.headers, json=data) as response:
                    resp_text = await response.text()
                    print(f"[SubgramAPI][request_subscription_block] Ответ: {resp_text}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {}
        except Exception as e:
            logging.error(f"Subgram API error: {e}")
            return {}

    def is_user_fully_subscribed(self, subscription_data: dict) -> bool:
        if not subscription_data or subscription_data.get('status') != 'ok':
            return False
        sponsors = subscription_data.get('additional', {}).get('sponsors', [])
        return all(s.get('status') == 'subscribed' for s in sponsors)

    def get_unsubscribed_channels(self, subscription_data: dict):
        sponsors = subscription_data.get('additional', {}).get('sponsors', [])
        return [
            {
                'link': s['link'],
                'name': s.get('resource_name', 'Канал'),
                'type': s.get('type', 'channel')
            }
            for s in sponsors if s.get('status') != 'subscribed'
        ]

subgram = SubgramAPI()

# --- Проверка подписки при /start ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    language_code = message.from_user.language_code or 'ru'
    is_premium = getattr(message.from_user, 'is_premium', False)
    subscription_data = await subgram.request_subscription_block(
        user_id=user_id,
        chat_id=chat_id,
        first_name=first_name,
        language_code=language_code,
        is_premium=is_premium
    )
    if subgram.is_user_fully_subscribed(subscription_data):
        await message.answer(
            "🌟 Добро пожаловать в реферальный бот!\n\n✅ Вы подписаны на все необходимые каналы. Теперь доступны все функции!\n\nВыберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        unsubscribed = subgram.get_unsubscribed_channels(subscription_data)
        if unsubscribed:
            channels_list = '\n'.join([
                f"{'📢' if c['type']=='channel' else '🤖'} <a href='{c['link']}'>{c['name']}</a>" for c in unsubscribed
            ])
            text = (
                f"<b>🚀 Добро пожаловать в реферальный бот!</b>\n\n"
                f"Для доступа к возможностям бота подпишитесь на каналы ниже:\n\n"
                f"{channels_list}\n\n"
                f"После подписки нажмите <b>Проверить подписку</b> 👇"
            )
            await message.answer(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(unsubscribed)
            )
        else:
            await message.answer(
                f"👋 Добро пожаловать в реферальный бот StarsovEarn!\n\n"
                f"Здесь вы можете зарабатывать звезды за приглашение друзей.\n\n"
                f"⭐ За каждого друга, который подпишется на все обязательные каналы и подтвердит подписку, вы получите <b>{STARS_PER_REFERRAL} звезд</b>!\n\n"
                f"Сейчас нет обязательных каналов для подписки. Как только появятся новые задания — вы сможете сразу начать зарабатывать!\n\n"
                f"Если есть вопросы — пишите в поддержку: @Yawinka",
                parse_mode="HTML"
            )

# --- Проверка подписки по кнопке ---
@dp.callback_query_handler(lambda c: c.data in ['check_subscription', 'subgram-op'])
async def process_check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    first_name = callback_query.from_user.first_name
    language_code = callback_query.from_user.language_code or 'ru'
    is_premium = getattr(callback_query.from_user, 'is_premium', False)
    subscription_data = await subgram.request_subscription_block(
        user_id=user_id,
        chat_id=chat_id,
        first_name=first_name,
        language_code=language_code,
        is_premium=is_premium
    )
    if subgram.is_user_fully_subscribed(subscription_data):
        await callback_query.message.edit_text(
            "🌟 Добро пожаловать в реферальный бот!\n\n✅ Вы подписаны на все необходимые каналы. Теперь доступны все функции!\n\nВыберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        unsubscribed = subgram.get_unsubscribed_channels(subscription_data)
        if unsubscribed:
            channels_list = '\n'.join([
                f"{'📢' if c['type']=='channel' else '🤖'} <a href='{c['link']}'>{c['name']}</a>" for c in unsubscribed
            ])
            text = (
                f"<b>🚀 Почти готово!</b>\n\n"
                f"Для доступа к возможностям бота подпишитесь на каналы ниже:\n\n"
                f"{channels_list}\n\n"
                f"После подписки нажмите <b>Проверить подписку</b> 👇"
            )
            await callback_query.message.edit_text(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(unsubscribed)
            )
        else:
            await callback_query.message.edit_text(
                f"👋 Добро пожаловать в реферальный бот StarsovEarn!\n\n"
                f"Здесь вы можете зарабатывать звезды за приглашение друзей.\n\n"
                f"⭐ За каждого друга, который подпишется на все обязательные каналы и подтвердит подписку, вы получите <b>{STARS_PER_REFERRAL} звезд</b>!\n\n"
                f"Сейчас нет обязательных каналов для подписки. Как только появятся новые задания — вы сможете сразу начать зарабатывать!\n\n"
                f"Если есть вопросы — пишите в поддержку: @Yawinka",
                parse_mode="HTML"
            )
    await callback_query.answer()

# --- Блокируем доступ к функциям, если не подписан ---
@dp.message_handler(lambda m: m.text in ["🔗 Реферальная ссылка", "💰 Баланс", "👤 Профиль", "💸 Вывод", "🆘 Поддержка"])
async def block_if_not_subscribed(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    language_code = message.from_user.language_code or 'ru'
    is_premium = getattr(message.from_user, 'is_premium', False)
    subscription_data = await subgram.request_subscription_block(
        user_id=user_id,
        chat_id=chat_id,
        first_name=first_name,
        language_code=language_code,
        is_premium=is_premium
    )
    if not subgram.is_user_fully_subscribed(subscription_data):
        unsubscribed = subgram.get_unsubscribed_channels(subscription_data)
        if unsubscribed:
            channels_list = '\n'.join([
                f"{'📢' if c['type']=='channel' else '🤖'} <a href='{c['link']}'>{c['name']}</a>" for c in unsubscribed
            ])
            text = (
                f"<b>🚀 Для доступа к функциям бота подпишитесь на каналы ниже:</b>\n\n"
                f"{channels_list}\n\n"
                f"После подписки нажмите <b>Проверить подписку</b> 👇"
            )
            await message.answer(
                text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(unsubscribed)
            )
        else:
            await message.answer(
                f"👋 Добро пожаловать в реферальный бот StarsovEarn!\n\n"
                f"Здесь вы можете зарабатывать звезды за приглашение друзей.\n\n"
                f"⭐ За каждого друга, который подпишется на все обязательные каналы и подтвердит подписку, вы получите <b>{STARS_PER_REFERRAL} звезд</b>!\n\n"
                f"Сейчас нет обязательных каналов для подписки. Как только появятся новые задания — вы сможете сразу начать зарабатывать!\n\n"
                f"Если есть вопросы — пишите в поддержку: @Yawinka",
                parse_mode="HTML"
            )
        return  # Не пропускаем дальше
    # Если подписан, остальные хендлеры сработают как обычно

# --- Регистрация всех хендлеров ---
register_user_handlers(dp)
register_admin_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 