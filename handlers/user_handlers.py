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
    CallbackContext,
)
from logger import setup_logger
from config import ID_TO_SEND_NOTIFICATIONS
from keyboards.general_keyboards import GeneralKeyboards
from messages import (
    CONFIRMATION_MESSAGE,
    EMOJI,
    INLINE_BUTTONS,
    REPLY_USER_BUTTONS,
    USER_MESSAGES,
)
from utils.utils import create_appointment_from_context
from states import *
from datetime import datetime
from interfaces.user_interfaces import UserInterface


def get_user_handlers():
    return {
        USER_MAIN_MENU: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_main_menu)
        ],
        USER_SELECT_PROCEDURE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_user_procedure_selection
            )
        ],
        USER_SELECT_MONTH: [
            CallbackQueryHandler(handle_user_month_selection),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_month_selection_unexpected_input,
            ),
        ],
        USER_SELECT_DATE: [
            CallbackQueryHandler(handle_user_date_selection),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_date_selection_unexpected_input,
            ),
        ],
        USER_SELECT_TIME: [
            CallbackQueryHandler(handle_user_time_selection),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_time_selection_unexpected_input,
            ),
        ],
        USER_ENTER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_enter_name)
        ],
        USER_ENTER_PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_enter_phone)
        ],
        USER_CONFIRMATION: [
            CallbackQueryHandler(handle_user_confirmation),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_confirmation_unexpected_input,
            ),
        ],
        USER_AFTER_CONFIRMATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_user_after_confirmation
            )
        ],
        USER_FINAL_HANDLER: [
            CallbackQueryHandler(user_final_handler),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_user_final_text_handler
            ),
        ],
    }


async def handle_user_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для главного меню пользователя."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["SELECT_PROCEDURE"]:
        await UserInterface.user_show_procedures(update, context)
        return USER_SELECT_PROCEDURE

    if text == REPLY_USER_BUTTONS["CONTACT_MASTER"]:
        await UserInterface.show_contact_master(update, context)
        return USER_FINAL_HANDLER

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await UserInterface.show_visit_tg_channel(update, context)
        return USER_FINAL_HANDLER

    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_month_selection_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при выборе месяца."""

    await update.message.reply_text(
        text=USER_MESSAGES["ERROR_TRY_AGAIN"] + "\n" + USER_MESSAGES["SELECT_MONTH"],
        reply_markup=context.bot_data.get("month_keyboard"),
    )
    return USER_SELECT_MONTH


async def handle_user_procedure_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для выбора процедуры."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await UserInterface.user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    elif text in context.bot_data["procedures_keyboard_buttons"]:
        procedure_name = " ".join(text.split()[1:])
        context.user_data["procedure_selected"] = procedure_name

        await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        await UserInterface.user_show_months(update, context)
        return USER_SELECT_MONTH
    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("procedures_keyboard"),
        )
        return USER_SELECT_PROCEDURE


async def handle_user_month_selection(update: Update, context: CallbackContext):
    """Хэндлер для выбора месяца."""

    query = update.callback_query
    await query.answer()

    if query.data == "back_to_procedures":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["SELECT_PROCEDURE"],
            reply_markup=context.bot_data.get("procedures_keyboard"),
        )
        return USER_SELECT_PROCEDURE

    elif query.data.startswith("month_"):
        month_str = query.data.replace("month_", "")
        month, year = map(int, month_str.split("_"))
        context.user_data["month_selected"] = (year, month)

        available_dates = context.bot_data["schedule"].get_available_dates(
            procedure=context.user_data.get("procedure_selected"),
            target_month=context.user_data.get("month_selected"),
        )

        if available_dates:
            keyboard = GeneralKeyboards.date_keyboard(year, month, available_dates)
            context.user_data["date_keyboard"] = keyboard
            await query.edit_message_text(
                USER_MESSAGES["SELECT_DATE"], reply_markup=keyboard
            )
            return USER_SELECT_DATE

        else:
            await query.edit_message_text(
                USER_MESSAGES["NO_DATES_AVAILABLE"],
                reply_markup=context.bot_data.get("month_keyboard"),
            )
        return USER_SELECT_MONTH

    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["ERROR_TRY_AGAIN"]
            + "\n"
            + USER_MESSAGES["SELECT_MONTH"],
            reply_markup=context.bot_data.get("month_keyboard"),
        )
        return USER_SELECT_MONTH


async def handle_user_month_selection_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при выборе месяца."""

    await update.message.reply_text(
        text=USER_MESSAGES["ERROR_TRY_AGAIN"] + "\n" + USER_MESSAGES["SELECT_MONTH"],
        reply_markup=context.bot_data.get("month_keyboard"),
    )
    return USER_SELECT_MONTH


async def handle_user_date_selection(update: Update, context: CallbackContext):
    """Хэндлер для выбора даты."""

    query = update.callback_query
    await query.answer()

    if query.data == "back_to_months":
        await query.edit_message_text(
            USER_MESSAGES["SELECT_MONTH"],
            reply_markup=context.bot_data.get("month_keyboard"),
        )
        return USER_SELECT_MONTH

    elif query.data.startswith("prev_month_") or query.data.startswith("next_month_"):
        _, _, year, month = query.data.split("_")
        year, month = int(year), int(month)

        schedule = context.bot_data.get("schedule")

        available_dates = schedule.get_available_dates(
            procedure=context.user_data.get("procedure_selected"),
            target_month=(year, month),
        )

        context.user_data["month_selected"] = (year, month)

        keyboard = GeneralKeyboards.date_keyboard(year, month, available_dates)
        context.user_data["date_keyboard"] = keyboard

        await UserInterface.user_show_dates_update_message(update, context)
        return USER_SELECT_DATE

    elif query.data.startswith("date_"):
        date_str = query.data.replace("date_", "")
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        context.user_data["date_selected"] = selected_date
        context.user_data["month_selected"] = (selected_date.year, selected_date.month)

        schedule = context.bot_data.get("schedule")
        available_slots = schedule.get_available_time_slots(
            selected_date, context.user_data.get("procedure_selected")
        )

        if not available_slots:
            await query.edit_message_text(
                USER_MESSAGES["NO_SLOTS_AVAILABLE"],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                INLINE_BUTTONS["BACK"], callback_data="back_to_dates"
                            )
                        ]
                    ]
                ),
            )
            return USER_SELECT_DATE

        keyboard = GeneralKeyboards.time_keyboard(available_slots)
        context.user_data["time_keyboard"] = keyboard
        await query.edit_message_text(
            USER_MESSAGES["SELECT_TIME"], reply_markup=keyboard
        )
        return USER_SELECT_TIME


async def handle_user_date_selection_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при выборе даты."""

    await update.message.reply_text(
        text=USER_MESSAGES["ERROR_TRY_AGAIN"] + "\n" + USER_MESSAGES["SELECT_DATE"],
        reply_markup=context.user_data.get("date_keyboard"),
    )
    return USER_SELECT_DATE


async def handle_user_time_selection(update: Update, context: CallbackContext):
    """Хэндлер для выбора времени."""

    query = update.callback_query
    await query.answer()

    if query.data == "back_to_dates":
        selected_date = context.user_data.get("date_selected")
        if not selected_date:
            await query.edit_message_text(
                USER_MESSAGES["ERROR_TRY_AGAIN"],
                reply_markup=context.bot_data.get("procedures_keyboard"),
            )
            return USER_SELECT_PROCEDURE

        await UserInterface.user_show_dates_callback_query(update, context)
        return USER_SELECT_DATE

    elif query.data.startswith("time_"):

        time_str = query.data.replace("time_", "")

        try:
            selected_time = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            selected_time = datetime.strptime(time_str, "%H:%M").time()

        context.user_data["time_selected"] = selected_time

        await UserInterface.user_show_enter_name(update, context)
        return USER_ENTER_NAME


async def handle_user_time_selection_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при выборе времени."""

    await update.message.reply_text(
        text=USER_MESSAGES["ERROR_TRY_AGAIN"] + "\n" + USER_MESSAGES["SELECT_TIME"],
        reply_markup=context.user_data.get("time_keyboard"),
    )
    return USER_SELECT_TIME


async def handle_user_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для ввода имени."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_TIME"]:
        await UserInterface.user_show_back_to_time(update, context)
        return USER_SELECT_TIME

    else:
        name = text
        if len(name) < 2:
            await update.message.reply_text(
                USER_MESSAGES["NAME_TOO_SHORT"],
            )
            return USER_ENTER_NAME
        elif len(name) > 50:
            await update.message.reply_text(
                USER_MESSAGES["NAME_TOO_LONG"],
            )
            return USER_ENTER_NAME

        context.user_data["name"] = name

        await UserInterface.user_show_enter_phone(update, context)
        return USER_ENTER_PHONE


async def handle_user_enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для ввода телефона."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_NAME"]:
        await UserInterface.user_show_back_to_name(update, context)
        return USER_ENTER_NAME
    else:
        phone = text
        if not re.match(r"^8\d{10}$", phone):
            await UserInterface.user_show_invalid_phone_format(update, context)
            return USER_ENTER_PHONE

        context.user_data["phone"] = phone

        confirmation_message = CONFIRMATION_MESSAGE["BOOKING_DETAILS"].format(
            procedure=context.user_data["procedure_selected"],
            date=context.user_data["date_selected"],
            time=context.user_data["time_selected"],
            name=context.user_data["name"],
            phone=context.user_data["phone"],
            sparkle=EMOJI["SPARKLE"],
            calendar=EMOJI["CALENDAR"],
            clock=EMOJI["CLOCK"],
            emoji_name=EMOJI["NAME"],
            emoji_phone=EMOJI["PHONE"],
        )

        keyboard = context.bot_data.get("confirmation_keyboard")
        context.user_data["confirmation_message"] = confirmation_message

        await update.message.reply_text(
            f"{USER_MESSAGES['CONFIRM_BOOKING']} \n {confirmation_message}",
            reply_markup=keyboard,
        )

        return USER_CONFIRMATION


async def handle_user_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для подтверждения или отмены записи."""

    logger = setup_logger(__name__)
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        await query.edit_message_text(USER_MESSAGES["BOOKING_SUCCESS"])
        await UserInterface.user_show_continue(update, context)
        try:
            await create_appointment_from_context(update, context)
            db_success = True
        except Exception as e:
            db_success = False
            logger.error(f"Ошибка при записи в базу данных: {e}")

        notification_message = (
            f'Клиент {context.user_data["name"]} записался на процедуру '
            f'"{context.user_data["procedure_selected"]}".\n'
            f'Дата: {context.user_data["date_selected"]}, '
            f'время: {context.user_data["time_selected"]}.\n'
            f'Телефон: {context.user_data["phone"]}.\n'
        )

        if db_success:
            notification_message += "✅ Запись добавлена в базу данных."
        else:
            notification_message += (
                "❗❗❗ Информация не добавлена в базу данных. "
                "Обратитесь к разработчику или попробуйте добавить запись "
                "самостоятельно через админ-интерфейс бота."
            )

        await context.bot.send_message(
            chat_id=ID_TO_SEND_NOTIFICATIONS,
            text=notification_message,
        )
        return USER_AFTER_CONFIRMATION

    elif query.data == "cancel":
        await UserInterface.user_show_cancel_booking(update, context)
        return USER_AFTER_CONFIRMATION

    elif query.data == "back_to_edit":
        await UserInterface.user_show_back_to_edit(update, context)
        return USER_ENTER_PHONE


async def handle_user_confirmation_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при подтверждении или отмене записи."""

    text = update.message.text
    if text == REPLY_USER_BUTTONS["BACK_TO_PHONE"]:
        await UserInterface.user_show_edit_phone(update, context)
        return USER_ENTER_PHONE

    elif text == REPLY_USER_BUTTONS["BACK_TO_NAME"]:
        await UserInterface.user_show_enter_name(update, context)
        return USER_ENTER_NAME

    else:
        await context.bot.send_message(
            chat_id=update.message.chat.id, text=USER_MESSAGES["ERROR_TRY_AGAIN"]
        )

        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=f"{USER_MESSAGES['CONFIRM_BOOKING']} \n {context.user_data['confirmation_message']}",
            reply_markup=context.user_data["confirmation_keyboard"],
        )
    return USER_CONFIRMATION


async def handle_user_after_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для возврата в главное меню или перехода в тг-канал."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await UserInterface.user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await UserInterface.show_visit_tg_channel(update, context)
        return USER_FINAL_HANDLER
    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )
        return USER_FINAL_HANDLER


async def user_final_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для возврата в главное меню или перехода в тг-канал."""

    query = update.callback_query
    await query.answer()
    if query.data == "back_to_menu":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["ON_RETURN_TO_MENU"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_final_text_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text
    if text == REPLY_USER_BUTTONS["SELECT_PROCEDURE"]:
        await UserInterface.user_show_procedures(update, context)
        return USER_SELECT_PROCEDURE

    elif text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await UserInterface.user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    elif text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await UserInterface.show_visit_tg_channel(update, context)
        return USER_FINAL_HANDLER

    elif text == REPLY_USER_BUTTONS["CONTACT_MASTER"]:
        await UserInterface.show_contact_master(update, context)
        return USER_FINAL_HANDLER

    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )
        return USER_FINAL_HANDLER
