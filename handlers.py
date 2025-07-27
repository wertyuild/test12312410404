from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import get_main_menu_keyboard, get_withdrawal_keyboard, get_referral_share_keyboard
from config import STARS_PER_REFERRAL

# --- Пользовательские хендлеры ---
def register_user_handlers(dp: Dispatcher):
    @dp.message_handler(lambda m: m.text == "🔗 Реферальная ссылка")
    async def show_referral_link(message: types.Message):
        # Заглушка, вставьте свою логику
        referral_link = f"https://t.me/yourbot?start={message.from_user.id}"
        await message.answer(
            f"🔗 <b>Ваша реферальная ссылка:</b>\n\n<code>{referral_link}</code>\n\n"
            f"📤 Поделитесь этой ссылкой с друзьями!\n⭐ За каждого реферала, подтвердившего подписку, вы получите <b>{STARS_PER_REFERRAL}</b> звезд(ы).",
            parse_mode="HTML",
            reply_markup=get_referral_share_keyboard(referral_link)
        )

    @dp.message_handler(lambda m: m.text == "💰 Баланс")
    async def show_balance(message: types.Message):
        # Заглушка, вставьте свою логику
        await message.answer(
            f"💰 <b>Ваш баланс:</b> <b>0</b> ⭐\n"
            f"💫 <b>Минимальная сумма вывода:</b> 20 ⭐",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )

    @dp.message_handler(lambda m: m.text == "👤 Профиль")
    async def show_profile(message: types.Message):
        # Заглушка, вставьте свою логику
        await message.answer(
            f"👤 <b>Ваш профиль</b>\n\n"
            f"🆔 <b>Юзернейм:</b> @{message.from_user.username or 'не указан'}\n"
            f"👥 <b>Рефералов:</b> 0\n"
            f"⭐ <b>Всего заработано звезд:</b> 0\n"
            f"📅 <b>Дата регистрации:</b> неизвестно",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )

    @dp.message_handler(lambda m: m.text == "💸 Вывод")
    async def show_withdrawal(message: types.Message):
        # Заглушка, вставьте свою логику
        await message.answer(
            f"💸 <b>Вывод средств</b>\n\n"
            f"💰 <b>Доступный баланс:</b> 0 ⭐\n"
            f"💫 <b>Минимальная сумма вывода:</b> 20 ⭐\n\n"
            f"📋 <b>Правила вывода:</b>\n"
            f"• Вывод отклоняется при подозрении в накрутке\n"
            f"• Вывод отклоняется для авторегнутых аккаунтов\n"
            f"• Обработка заявок может занимать до 24 часов",
            parse_mode="HTML",
            reply_markup=get_withdrawal_keyboard()
        )

    @dp.message_handler(lambda m: m.text == "🆘 Поддержка")
    async def show_support(message: types.Message):
        await message.answer(
            "🆘 <b>Поддержка</b>\n\n"
            "По всем вопросам обращайтесь к администратору:\n"
            "@Yawinka\n\n"
            "📞 <b>Время работы поддержки:</b> 24/7",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        ) 