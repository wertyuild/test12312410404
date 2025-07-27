from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import get_admin_menu_keyboard, get_admin_settings_keyboard
from config import STARS_PER_REFERRAL
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

ADMIN_ID = 123456789  # Замените на свой Telegram ID

class AdminStates(StatesGroup):
    waiting_for_stars_per_ref = State()

def register_admin_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["admin"])
    async def cmd_admin(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ У вас нет доступа к административной панели.")
            return
        await message.answer(
            "👑 Административная панель\n\n"
            "📊 Статистика:\n"
            "👥 Всего пользователей: 0\n"
            "✅ Подписанных: 0\n"
            "🔗 Завершенных рефералов: 0\n"
            "⭐ Выдано звезд: 0\n"
            "💸 Ожидающих заявок: 0",
            reply_markup=get_admin_menu_keyboard()
        )

    @dp.callback_query_handler(lambda c: c.data == "admin_menu")
    async def show_admin_menu(callback_query: types.CallbackQuery):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "👑 Административная панель\n\n"
            "📊 Статистика:\n"
            "👥 Всего пользователей: 0\n"
            "✅ Подписанных: 0\n"
            "🔗 Завершенных рефералов: 0\n"
            "⭐ Выдано звезд: 0\n"
            "💸 Ожидающих заявок: 0",
            reply_markup=get_admin_menu_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_settings")
    async def show_admin_settings(callback_query: types.CallbackQuery):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "⚙️ Настройки бота\n\n"
            "💫 Минимальная сумма вывода: 20 звезд\n"
            "⭐ Звезды за реферала: 5 звезд\n\n"
            "Выберите настройку для изменения:",
            reply_markup=get_admin_settings_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_stats")
    async def show_admin_stats(callback_query: types.CallbackQuery):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "📊 Подробная статистика\n\n"
            "👥 Всего пользователей: 0\n"
            "✅ Подписанных пользователей: 0\n"
            "❌ Неподписанных: 0\n\n"
            "🔗 Завершенных рефералов: 0\n"
            "⭐ Всего выдано звезд: 0\n"
            "💰 Общий баланс пользователей: 0 звезд\n\n"
            "💸 Ожидающих заявок на вывод: 0",
            reply_markup=get_admin_menu_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_users")
    async def show_admin_users(callback_query: types.CallbackQuery):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "👥 Все пользователи\n\nСписок пользователей (заглушка)",
            reply_markup=get_admin_menu_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_withdrawals")
    async def show_admin_withdrawals(callback_query: types.CallbackQuery):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "💸 Заявки на вывод\n\nСписок заявок (заглушка)",
            reply_markup=get_admin_menu_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_set_stars_per_ref")
    async def set_stars_per_ref(callback_query: types.CallbackQuery, state: FSMContext):
        if callback_query.from_user.id != ADMIN_ID:
            await callback_query.answer("❌ Нет доступа")
            return
        await callback_query.message.edit_text(
            "Введите новое количество звезд за реферала:",
            reply_markup=get_admin_settings_keyboard()
        )
        await AdminStates.waiting_for_stars_per_ref.set()

    @dp.message_handler(state=AdminStates.waiting_for_stars_per_ref)
    async def process_stars_per_ref(message: types.Message, state: FSMContext):
        global STARS_PER_REFERRAL
        try:
            value = int(message.text)
            if value < 1 or value > 100:
                raise ValueError
            STARS_PER_REFERRAL = value
            await message.answer(f"✅ Количество звезд за реферала обновлено: {STARS_PER_REFERRAL}", reply_markup=get_admin_settings_keyboard())
            await state.finish()
        except Exception:
            await message.answer("❗️ Введите целое число от 1 до 100:") 