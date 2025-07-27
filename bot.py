import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp # Для асинхронных HTTP-запросов к Subgram API

# --- Константы (замените своими данными) ---
TELEGRAM_BOT_TOKEN = "ВАШ_ТЕЛЕГРАМ_БОТ_ТОКЕН"  # Получите у @BotFather
SUBGRAM_API_KEY = "ВАШ_SUBGRAM_API_КЛЮЧ"      # Получите в @subgram_officialbot

# Флаг: True, если бот добавлен в Subgram БЕЗ токена (тогда нужно передавать доп. параметры)
# False, если бот добавлен ВМЕСТЕ с токеном.
# Измените это значение в зависимости от того, как вы подключали бота к Subgram.
SUBGRAM_BOT_ADDED_WITHOUT_TOKEN = False 

# URL для запроса к Subgram API
SUBGRAM_REQUEST_OP_URL = "https://api.subgram.ru/request-op/"
# ---

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# --- Функция для запроса к Subgram API ---
async def request_op(
    user_id: int,
    chat_id: int,
    gender: str = None,
    first_name: str = None,
    language_code: str = None,
    is_premium: bool = None,
    max_op: int = None,
    action: str = "subscribe",
    exclude_channel_ids: list = None
) -> tuple[str, int, list, dict]:
    """
    Отправляет запрос к Subgram API для проверки обязательной подписки.
    Возвращает (status, code, links, additional_data).
    """
    payload = {
        "UserId": str(user_id),
        "ChatId": str(chat_id),
        "action": action
    }
    
    headers = {
        "Auth": SUBGRAM_API_KEY,
        "Content-Type": "application/json"
    }

    # Добавляем параметры, если бот добавлен без токена
    if SUBGRAM_BOT_ADDED_WITHOUT_TOKEN:
        if first_name is not None:
            payload["first_name"] = first_name
        if language_code is not None:
            payload["language_code"] = language_code
        if is_premium is not None:
            payload["Premium"] = is_premium # Subgram ожидает 'Premium' с большой буквы
    
    # Добавляем необязательные параметры, если они переданы
    if gender is not None:
        payload["Gender"] = gender
    if max_op is not None:
        payload["MaxOP"] = max_op
    if exclude_channel_ids is not None:
        payload["exclude_channel_ids"] = exclude_channel_ids

    logger.info(f"Отправка запроса в Subgram: {payload}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SUBGRAM_REQUEST_OP_URL, headers=headers, json=payload) as response:
                response.raise_for_status()  # Вызывает исключение для HTTP ошибок 4xx/5xx
                data = await response.json()
                
                status = data.get("status")
                code = data.get("code")
                links = data.get("links", [])
                additional = data.get("additional", {})

                logger.info(f"Ответ от Subgram (пользователь {user_id}): status={status}, code={code}")
                return status, code, links, additional

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Ошибка подключения к Subgram API: {e}")
            return "error", 503, [], {} # Ошибка сервиса
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP ошибка от Subgram API: {e.status} - {e.message}")
            return "error", e.status, [], {} # Ошибка API
        except Exception as e:
            logger.error(f"Неизвестная ошибка при запросе к Subgram: {e}")
            return "error", 500, [], {} # Внутренняя ошибка

# --- Обработчик команды /start ---
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    Обрабатывает команду /start.
    Проверяет подписку пользователя через Subgram API.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_first_name = message.from_user.first_name
    user_language_code = message.from_user.language_code
    user_is_premium = message.from_user.is_premium

    status, code, links, additional = await request_op(
        user_id=user_id,
        chat_id=chat_id,
        first_name=user_first_name,
        language_code=user_language_code,
        is_premium=user_is_premium
    )

    if status == 'ok' and code == 200:
        # Пользователь подписан на все необходимые ресурсы
        await message.answer("Спасибо за подписку! Доступ к боту разрешен. 👍")
        # Здесь вы можете добавить функционал, доступный только подписчикам
    elif status == 'warning':
        # Пользователь не подписан на один или несколько ресурсов
        if links:
            # Если Subgram прислал список ссылок для подписки
            text_to_send = "Чтобы получить доступ, пожалуйста, подпишитесь на следующие каналы:"
            keyboard = InlineKeyboardBuilder()
            
            # Добавляем ссылки на каналы в клавиатуру
            # Используем additional['sponsors'] для получения названий каналов, если доступны
            for sponsor in additional.get('sponsors', []):
                if sponsor.get('status') == 'unsubscribed': # Показываем только те, на которые не подписан
                    link = sponsor.get('link')
                    name = sponsor.get('resource_name', "Канал/Бот") # Fallback name
                    if link:
                        text_to_send += f"\n- <a href='{link}'>{name}</a>"
                        # Добавляем кнопку "Проверить подписку" в конце списка ссылок
                        # Можно сделать отдельную кнопку для каждого канала, но это часто избыточно
            
            # Кнопка для повторной проверки после подписки
            keyboard.button(text="Я подписался!", callback_data="subgram_check_again")
            
            await message.answer(
                text_to_send,
                reply_markup=keyboard.as_markup(),
                disable_web_page_preview=True # Отключаем превью ссылок, чтобы не загромождать сообщение
            )
        else:
            # Если Subgram не прислал ссылки (редкий случай, но возможный)
            await message.answer(
                "Для доступа к боту требуется подписка. Пожалуйста, убедитесь, что вы подписаны на все необходимые ресурсы."
            )
    elif status == 'gender':
        # Subgram запросил пол пользователя
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Мужской", callback_data="subgram_gender_male")
        keyboard.button(text="Женский", callback_data="subgram_gender_female")
        await message.answer(
            "Для продолжения, пожалуйста, укажите ваш пол:",
            reply_markup=keyboard.as_markup()
        )
    else:
        # Общая ошибка или неизвестный статус
        await message.answer(
            "Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже."
        )

# --- Обработчик callback-кнопок ---
@dp.callback_query(F.data.startswith("subgram"))
async def subgram_callback_query(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    user_first_name = callback_query.from_user.first_name
    user_language_code = callback_query.from_user.language_code
    user_is_premium = callback_query.from_user.is_premium

    if callback_query.data == "subgram_check_again":
        await callback_query.message.edit_text("Проверяю вашу подписку, пожалуйста, подождите...")
        status, code, links, additional = await request_op(
            user_id=user_id,
            chat_id=chat_id,
            first_name=user_first_name,
            language_code=user_language_code,
            is_premium=user_is_premium
        )

        if status == 'ok' and code == 200:
            await callback_query.message.edit_text("Спасибо за подписку! Доступ к боту разрешен. 👍")
            # Здесь вы можете вызвать функцию, которая показывает основные функции бота
        elif status == 'warning':
            # Снова предлагаем подписаться
            if links:
                text_to_send = "Вы все еще не подписаны на некоторые каналы. Пожалуйста, завершите подписку:"
                keyboard = InlineKeyboardBuilder()
                for sponsor in additional.get('sponsors', []):
                    if sponsor.get('status') == 'unsubscribed':
                        link = sponsor.get('link')
                        name = sponsor.get('resource_name', "Канал/Бот")
                        if link:
                            text_to_send += f"\n- <a href='{link}'>{name}</a>"
                keyboard.button(text="Я подписался!", callback_data="subgram_check_again")
                await callback_query.message.edit_text(
                    text_to_send,
                    reply_markup=keyboard.as_markup(),
                    disable_web_page_preview=True
                )
            else:
                await callback_query.message.edit_text(
                    "Для доступа к боту требуется подписка. Пожалуйста, убедитесь, что вы подписаны на все необходимые ресурсы."
                )
        elif status == 'gender':
            # Если после повторной проверки снова запросился пол (маловероятно, но на всякий случай)
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="Мужской", callback_data="subgram_gender_male")
            keyboard.button(text="Женский", callback_data="subgram_gender_female")
            await callback_query.message.edit_text(
                "Пожалуйста, укажите ваш пол для проверки подписки:",
                reply_markup=keyboard.as_markup()
            )
        else:
            await callback_query.message.edit_text(
                "Произошла ошибка при повторной проверке подписки. Пожалуйста, попробуйте позже."
            )
        
        await callback_query.answer() # Отвечаем на callback, чтобы убрать "часики"

    elif callback_query.data.startswith("subgram_gender_"):
        gender = callback_query.data.split("_")[2]
        await callback_query.message.edit_text(f"Спасибо, ваш пол '{gender}' учтен. Проверяю подписку...")

        status, code, links, additional = await request_op(
            user_id=user_id,
            chat_id=chat_id,
            gender=gender, # Передаем выбранный пол
            first_name=user_first_name,
            language_code=user_language_code,
            is_premium=user_is_premium
        )

        if status == 'ok' and code == 200:
            await callback_query.message.edit_text("Спасибо за подписку! Доступ к боту разрешен. 👍")
        elif status == 'warning':
            if links:
                text_to_send = "Теперь, пожалуйста, подпишитесь на следующие каналы:"
                keyboard = InlineKeyboardBuilder()
                for sponsor in additional.get('sponsors', []):
                    if sponsor.get('status') == 'unsubscribed':
                        link = sponsor.get('link')
                        name = sponsor.get('resource_name', "Канал/Бот")
                        if link:
                            text_to_send += f"\n- <a href='{link}'>{name}</a>"
                keyboard.button(text="Я подписался!", callback_data="subgram_check_again")
                await callback_query.message.edit_text(
                    text_to_send,
                    reply_markup=keyboard.as_markup(),
                    disable_web_page_preview=True
                )
            else:
                await callback_query.message.edit_text(
                    "Для доступа к боту требуется подписка. Пожалуйста, убедитесь, что вы подписаны на все необходимые ресурсы."
                )
        else:
            await callback_query.message.edit_text(
                "Произошла ошибка при проверке подписки после указания пола. Пожалуйста, попробуйте позже."
            )
        
        await callback_query.answer() # Отвечаем на callback

# --- Запуск бота ---
async def main() -> None:
    """Запускает бота."""
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
