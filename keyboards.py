from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔗 Реферальная ссылка"), KeyboardButton(text="💰 Баланс")],
            [KeyboardButton(text="💸 Вывод"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True
    )

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Все пользователи", callback_data="admin_users")],
            [InlineKeyboardButton(text="💸 Заявки на вывод", callback_data="admin_withdrawals")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        ]
    )

def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💫 Мин. сумма вывода", callback_data="admin_set_min_withdrawal")],
            [InlineKeyboardButton(text="⭐ Звезды за реферала", callback_data="admin_set_stars_per_ref")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")],
        ]
    )

def get_withdrawal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Вывести", callback_data="start_withdrawal")],
            [InlineKeyboardButton(text="📋 Правила вывода", callback_data="withdrawal_rules")],
        ]
    )

def get_withdrawal_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_withdrawal"),
             InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_withdrawal")]
        ]
    )

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
        ]
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_referral_share_keyboard(referral_link: str) -> InlineKeyboardMarkup:
    share_text = f"🌟 Присоединяйся к боту и получай звезды за рефералов! {referral_link}"
    share_url = f"https://t.me/share/url?url={referral_link}&text={share_text}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Поделиться", url=share_url)]
        ]
    )

def get_subscription_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for channel in channels:
        if channel['type'] == 'bot':
            button_text = f"🤖 {channel['name']}"
        elif channel['type'] == 'channel':
            button_text = f"📢 {channel['name']}"
        else:
            button_text = f"🔗 {channel['name']}"
        buttons.append([InlineKeyboardButton(text=button_text, url=channel['link'])])
    buttons.append([InlineKeyboardButton(text="✅ Я выполнил", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) 