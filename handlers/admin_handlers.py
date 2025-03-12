from datetime import datetime
import re
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from keyboards.admin_keyboards import *
from keyboards.general_keyboards import *
from states import *
from utils.formatter import format_date_for_db, format_date_for_db_admin
from utils.utils import create_appointment_from_context

user_data = {}


def get_admin_handlers():
    return {
        ADMIN_ACTIONS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_actions)
        ],
        ADMIN_SELECT_PROCEDURE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_admin_procedure_selection,
            )
        ],
        ADMIN_SELECT_DATE: [
            MessageHandler(
                filters.Regex(
                    "января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря"
                )
                & ~(
                    filters.Regex("^(Следующие 7 дней)$")
                    | filters.Regex("^(Назад)$")
                    | filters.Regex("^(Вернуться к выбору процедуры)$")
                ),
                handle_admin_date_selection,
            ),
        ],
        ADMIN_SELECT_TIME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_admin_time_selection,
            )
        ],
        ADMIN_ENTER_CLIENT_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_admin_enter_client_name
            )
        ],
        ADMIN_ENTER_CLIENT_PHONE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_admin_enter_client_phone
            )
        ],
        ADMIN_ENTER_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text_comment),
            CallbackQueryHandler(handle_admin_skip_comment, pattern="^skip$"),
        ],
        ADMIN_CONFIRMATION: [CallbackQueryHandler(handle_admin_confirmation)],
        ADMIN_AFTER_CONFIRMATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_admin_after_confirmation
            )
        ],
        ADMIN_BLOCK_DAY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_block_day),
        ],
        ADMIN_BLOCK_SEVERAL_DAYS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_block_several_days,
            ),
        ],
    }


async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Добавить запись":
        await update.message.reply_text(
            "Выберите процедуру:",
            reply_markup=context.bot_data["procedures_keyboard"],
        )
        return ADMIN_SELECT_PROCEDURE

    elif text == "Удалить запись":
        await update.message.reply_text(
            "Выберите дату для удаления записи:",
            reply_markup=date_keyboard(context),
        )
        return ADMIN_DELETE_APPOINTMENT

    elif text == "Заблокировать день":
        await update.message.reply_text(
            "Введите дату для блокировки в формате **ДД.ММ.ГГГГ** (например, **28.02.2025**):"
        )
        return ADMIN_BLOCK_DAY

    elif text == "Заблокировать несколько дней":
        await update.message.reply_text(
            "Введите дату начала блокировки и продолжительность в днях в формате **ДД.ММ.ГГГГ ДНИ** (например, **28.02.2025 3**):"
        )
        return ADMIN_BLOCK_SEVERAL_DAYS

    elif text == "Заблокировать время":
        await update.message.reply_text(
            "Введите дату и временной промежуток для блокировки в формате **ДД.ММ.ГГГГ ЧЧ:ММ-ЧЧ:ММ** (например, **28.02.2025 10:00-12:00**):"
        )
        return ADMIN_BLOCK_TIME

    elif text == "Добавить процедуру":
        await update.message.reply_text(
            "Введите название и продолжительность новой процедуры в формате **Название (мин)**, например **Окрашивание ресниц (60)**:",
        )
        return ADMIN_ADD_PROCEDURE

    elif text == "Сделать процедуру неактивной":
        await update.message.reply_text(
            "Выберите процедуру:",
            reply_markup=context.bot_data["procedures_keyboard"],
        )
        return ADMIN_DEACTIVATE_PROCEDURE

    else:
        await update.message.reply_text(
            "Неизвестная команда. Пожалуйста, выберите действие из меню."
        )
        return ADMIN_ACTIONS


async def handle_admin_procedure_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text
    if text == "⬅️ Вернуться в меню":
        await update.message.reply_text(
            "Пожалуйста, выберите действие",
            reply_markup=context.bot_data["admin_main_menu_keyboard"],
        )
        return ADMIN_ACTIONS
    else:
        user_data["procedure_selected"] = " ".join(text.split()[1:])
        await update.message.reply_text(
            f"Вы выбрали процедуру: {text}. Теперь выберите дату.",
            reply_markup=date_keyboard(context),
        )
        return ADMIN_SELECT_DATE


async def handle_admin_date_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text == "Вернуться к выбору процедуры":
        await update.message.reply_text(
            "Пожалуйста, выберите процедуру",
            reply_markup=context.bot_data["procedures_keyboard"],
        )
        return ADMIN_SELECT_PROCEDURE

    else:
        date = text
        formatted_date = format_date_for_db(date)
        user_data["date_selected"] = date
        user_data["date_formatted"] = formatted_date
        keyboard, message = time_keyboard(
            context, formatted_date, user_data["procedure_id"]
        )

    if message:
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            f"Вы выбрали дату: {date}. Теперь выберите время.",
            reply_markup=keyboard,
        )
    return ADMIN_SELECT_TIME


async def handle_admin_time_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text == "Назад" or text == "Вернуться к выбору даты":
        await update.message.reply_text(
            "Пожалуйста, выберите дату.",
            reply_markup=date_keyboard(context),
        )
        return ADMIN_SELECT_DATE

    else:
        time = text
        time_obj = datetime.strptime(time, "%H:%M").time()

        user_data["time_selected"] = time
        user_data["time_formatted"] = time_obj

        await update.message.reply_text(
            f"Вы выбрали время: {time}. Пожалуйста, введите имя клиента.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ADMIN_ENTER_CLIENT_NAME


async def handle_admin_enter_client_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    name = update.message.text

    if len(name) < 2:
        await update.message.reply_text(
            "Имя должно содержать не менее двух символов. Пожалуйста, введите имя клиента."
        )
        return ADMIN_ENTER_CLIENT_NAME

    user_data["name"] = name
    await update.message.reply_text(
        "Пожалуйста, введите телефон клиента в формате +7XXXXXXXXXX."
    )
    return ADMIN_ENTER_CLIENT_PHONE


async def handle_admin_enter_client_phone(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    phone = update.message.text

    if not re.match(r"^\+7\d{10}$", phone):
        await update.message.reply_text(
            "Пожалуйста, введите телефон в формате **+7XXXXXXXXXX**."
        )
        return ADMIN_ENTER_CLIENT_PHONE
    else:

        user_data["phone"] = phone

        await update.message.reply_text(
            "Если у вас есть комментарий к записи, введите его. Если нет, нажмите 'Пропустить'.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Пропустить", callback_data="skip")]]
            ),
        )

        return ADMIN_ENTER_COMMENT


async def handle_admin_text_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text

    user_data["comment"] = comment

    confirmation_message = (
        f"Пожалуйста, подтвердите запись:\n"
        f"Процедура: {user_data['procedure_selected']}\n"
        f"Дата: {user_data['date_selected']}\n"
        f"Время: {user_data['time_selected']}\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Комментарий: {user_data.get('comment', 'нет комментария')}"
    )
    await update.message.reply_text(
        confirmation_message, reply_markup=context.bot_data["confirmation_keyboard"]
    )
    return ADMIN_CONFIRMATION


async def handle_admin_skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data["comment"] = "нет комментария"

    confirmation_message = (
        f"Пожалуйста, подтвердите запись:\n"
        f"Процедура: {user_data['procedure_selected']}\n"
        f"Дата: {user_data['date_selected']}\n"
        f"Время: {user_data['time_selected']}\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Комментарий: нет"
    )
    await query.edit_message_text(
        confirmation_message, reply_markup=context.bot_data["confirmation_keyboard"]
    )
    return ADMIN_CONFIRMATION


async def handle_admin_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        create_appointment_from_context(update, context)
        await query.edit_message_text(
            "Запись подтверждена✅ Что вы хотите сделать дальше?",
            reply_markup=context.bot_data["admin_final_keyboard"],
        )

    elif query.data == "cancel":
        await query.edit_message_text(
            "Запись отменена❌ Что вы хотите сделать дальше?",
            reply_markup=context.bot_data["admin_final_keyboard"],
        )

        return ADMIN_AFTER_CONFIRMATION


async def handle_admin_after_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text == "Вернуться в главное меню":
        return ADMIN_ACTIONS


async def handle_block_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = update.message.text
    try:
        formatted_date = format_date_for_db_admin(date_str)
        blocked_slots = context.bot_data["blocked_slots"]
        blocked_slots.block_day(formatted_date)
        await update.message.reply_text(f"День {date_str} успешно заблокирован.")
        return ADMIN_ACTIONS
    except ValueError:
        await update.message.reply_text(
            "Неверный формат даты. Используйте **ДД.ММ.ГГГГ** (например, **28.02.2025**)."
        )
        return ADMIN_BLOCK_DAY


async def handle_block_several_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str, days_str = update.message.text.split()
    try:
        start_date = format_date_for_db_admin(date_str)
        days = int(days_str)
        blocked_slots = context.bot_data["blocked_slots"]
        blocked_slots.block_several_days(start_date, days)
        day_form, verb_form = (
            "день" if days == 1 else "дня" if days in [2, 3, 4] else "дней"
        ), ("заблокирован" if days == 1 else "заблокированы")
        await update.message.reply_text(
            f"{days} {day_form}, начиная с {date_str}, {verb_form}."
        )
    except ValueError:
        await update.message.reply_text(
            "Неверный формат. Используйте **ДД.ММ.ГГГГ ДНИ** (например, **28.02.2025 3**)."
        )
    return ADMIN_ACTIONS


async def handle_block_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = update.message.text
    try:
        date_str, time_range = input_text.split()
        start_time_str, end_time_str = time_range.split("-")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        blocked_slots = context.bot_data["blocked_slots"]
        blocked_slots.block_time_slot(date, start_time, end_time)
        await update.message.reply_text(
            f"Временной промежуток {time_range} на {date_str} успешно заблокирован."
        )
    except ValueError:
        await update.message.reply_text(
            "Неверный формат. Используйте **ДД.ММ.ГГГГ ЧЧ:ММ-ЧЧ:ММ** (например, **28.02.2025 10:00-12:00**)."
        )
    return ADMIN_ACTIONS


async def handle_admin_add_appointment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    telephone = update.message.text

    client = await handle_admin_find_client(update, context, telephone)

    if client:
        pass
        # client_id, client_telephone, client_name = client
        # appointments.create_appointment(client_id, procedure, appointment_date, appointment_time)

        await update.message.reply_text("Запись на процедуру добавлена.")
    else:
        await update.message.reply_text(
            "Клиент не найден. В таблицу Clients будет добавлен новый клиент."
        )


async def handle_admin_find_client(
    update: Update, context: ContextTypes.DEFAULT_TYPE, telephone: str
):

    client = context.bot_data["clients"].get_client_by_telephone(telephone)

    if client:
        return client

    else:
        await update.message.reply_text("Клиент не найден.")
