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
from keyboards.general_keyboards import *
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
from interfaces.user_interfaces import *


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
        USER_ENTER_PHONE_FOR_ACCOUNT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_user_enter_phone_for_account
            )
        ],
        USER_CLIENT_ACCOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_account_menu)
        ],
        USER_APPOINTMENTS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_appointments)
        ],
        USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE: [
            CallbackQueryHandler(
                handle_user_select_appointment_for_cancel_or_reschedule
            ),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_select_appointment_unexpected_input,
            ),
        ],
        USER_APPOINTMENT_EDIT_ACTIONS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_user_appointment_edit_actions
            )
        ],
        USER_AFTER_EDIT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_after_edit,
            ),
        ],
        USER_SHOW_PERSONAL_DATA: [
            CallbackQueryHandler(handle_user_show_personal_data),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_personal_data_unexpected_input,
            ),
        ],
        USER_UPDATE_PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_update_phone)
        ],
        USER_UPDATE_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_update_name)
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
        await user_show_procedures(update, context)
        return USER_SELECT_PROCEDURE

    elif text == REPLY_USER_BUTTONS["CLIENT_ACCOUNT"]:
        tg_id = update.message.from_user.id
        if context.bot_data["clients"].client_is_registered_by_tg_id(tg_id):
            await user_show_client_account(update, context)
            return USER_CLIENT_ACCOUNT
        else:
            await update.message.reply_text(
                text=f"Пожалуйста, введите свой номер телефона в формате 8ХХХХХХХХХХ.",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(text=REPLY_USER_BUTTONS["BACK_TO_MENU"])]]
                ),
            )
            return USER_ENTER_PHONE_FOR_ACCOUNT

    if text == REPLY_USER_BUTTONS["CONTACT_MASTER"]:
        await show_contact_master(update, context)
        return USER_FINAL_HANDLER

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await show_visit_tg_channel(update, context)
        return USER_FINAL_HANDLER

    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_procedure_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для выбора процедуры."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    elif text in context.bot_data["procedures_keyboard_buttons"]:
        context.user_data["reschedule"] = False
        procedure_name = " ".join(text.split()[1:])
        context.user_data["procedure_selected"] = procedure_name

        await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        await user_show_months(update, context)
        return USER_SELECT_MONTH
    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("procedures_keyboard"),
        )
        return USER_SELECT_PROCEDURE


async def handle_user_enter_phone_for_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для ввода телефона при поиске аккаунта."""
    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    else:
        phone = text
        if not re.match(r"^8\d{10}$", phone):
            await update.message.reply_text(USER_MESSAGES["INVALID_PHONE_FORMAT"])
            return USER_ENTER_PHONE_FOR_ACCOUNT

        else:
            if context.bot_data["clients"].client_is_registered_by_phone(text):
                await user_show_client_account(update, context)
                return USER_CLIENT_ACCOUNT

            else:
                await update.message.reply_text(
                    USER_MESSAGES["CLIENT_ACCOUNT_NOT_FOUND"],
                    reply_markup=context.bot_data.get("user_main_menu_keyboard"),
                )
                return USER_MAIN_MENU


async def handle_user_account_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для меню личного кабинета."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["MY_APPOINTMENTS"]:
        id = context.bot_data["clients"].get_client_id_by_tg_id(
            context.user_data["tg_id"]
        )
        context.user_data["id"] = id
        if context.bot_data["appointments"].client_has_appointments(id):
            await user_show_client_appointments(update, context, id)
            return USER_APPOINTMENTS
        else:
            await update.message.reply_text(
                text=USER_MESSAGES["NO_APPOINTMENTS"],
                reply_markup=context.bot_data.get("user_main_menu_keyboard"),
            )
            return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["MY_PROFILE"]:
        await user_show_personal_data(update, context)
        return USER_SHOW_PERSONAL_DATA

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    else:
        await update.message.reply_text(
            text=USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_account_keyboard"),
        )

        return USER_CLIENT_ACCOUNT


async def handle_user_show_personal_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для меню с персональными данными клиента."""
    query = update.callback_query
    await query.answer()

    if query.data == "telephone":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"{EMOJI['PHONE']} Пожалуйста, введите новый номер телефона:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])]],
                resize_keyboard=True,
            ),
        )
        return USER_UPDATE_PHONE

    if query.data == "client_name":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"{EMOJI['USER']} Пожалуйста, введите новое имя:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])]],
                resize_keyboard=True,
            ),
        )
        return USER_UPDATE_NAME

    if query.data == "back_to_profile":
        text = USER_MESSAGES["BACK_TO_PROFILE"]
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=context.bot_data.get("user_account_keyboard"),
        )
        return USER_CLIENT_ACCOUNT

    if query.data == "back_to_menu":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["ON_RETURN_TO_MENU"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_update_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT
    else:
        phone = text

        if not re.match(r"^8\d{10}$", phone):
            await update.message.reply_text(
                text=USER_MESSAGES["INVALID_PHONE_FORMAT"],
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])]],
                    resize_keyboard=True,
                ),
            )
            return USER_UPDATE_PHONE
        else:
            context.user_data["phone"] = phone
            clients = context.bot_data["clients"]
            tg_id = context.user_data["tg_id"]

            clients.update_client_phone_by_tg_id(tg_id, phone)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{EMOJI['SUCCESS']} Номер изменен! Новый номер: {phone}.",
                reply_markup=context.bot_data.get("user_after_edit_keyboard"),
            )
            return USER_AFTER_EDIT


async def handle_user_update_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT
    else:
        name = text
        context.user_data["name"] = name
        clients = context.bot_data["clients"]
        tg_id = context.user_data["tg_id"]
        clients.update_client_name_by_tg_id(tg_id, name)
        await update.message.reply_text(
            text=f"{EMOJI['SUCCESS']} Имя изменено! Новое имя: {name}.",
            reply_markup=context.bot_data.get("user_after_edit_keyboard"),
        )
        return USER_AFTER_EDIT


async def handle_personal_data_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text
    if text == REPLY_USER_BUTTONS["MY_APPOINTMENTS"]:
        id = context.bot_data["clients"].get_client_id_by_tg_id(
            context.user_data["tg_id"]
        )
        context.user_data["id"] = id
        if context.bot_data["appointments"].client_has_appointments(id):
            await user_show_client_appointments(update, context, id)
            return USER_APPOINTMENTS
        else:
            await update.message.reply_text(
                text=USER_MESSAGES["NO_APPOINTMENTS"],
                reply_markup=context.bot_data.get("user_main_menu_keyboard"),
            )
            return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["MY_PROFILE"]:
        await user_show_personal_data(update, context)
        return USER_SHOW_PERSONAL_DATA

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU
    
    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT

    else:
        await update.message.reply_text(text=USER_MESSAGES["ERROR_TRY_AGAIN"])
        await user_show_personal_data(update, context)
        return USER_SHOW_PERSONAL_DATA


async def handle_user_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для меню с отменой и переносом записей."""
    text = update.message.text

    if text == REPLY_USER_BUTTONS["RESCHEDULE_OR_CANCEL"]:
        await user_show_edit_client_appointments(
            update, context, context.user_data["id"]
        )
        return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE
    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT
    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU
    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_appointments_keyboard"),
        )
        return USER_APPOINTMENTS


async def handle_user_select_appointment_for_cancel_or_reschedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для выбора записи для переноса или отмены."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("select_appointment"):
        appointment_id = query.data.split("_")[2]
        context.user_data["appointment_id"] = appointment_id

        context.user_data["appointment_for_editing"] = [
            appointment
            for appointment in context.user_data["appointments_list"]
            if appointment[0] == int(context.user_data["appointment_id"])
        ][0]

        context.user_data["procedure_selected"] = context.user_data[
            "appointment_for_editing"
        ][1]

        procedure = context.user_data["procedure_selected"]
        date = format_date_for_client_interface(
            context.user_data["appointment_for_editing"][2]
        )
        time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>Вы выбрали</b>: {procedure} - {date} - {time}.\n<b>Вы хотите отменить или перенести выбранную запись? </b>",
            parse_mode="HTML",
            reply_markup=context.bot_data.get("user_cancel_reschedule_keyboard"),
        )
        return USER_APPOINTMENT_EDIT_ACTIONS

    elif query.data == "back_to_profile":
        text = USER_MESSAGES["BACK_TO_PROFILE"]
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=context.bot_data.get("user_account_keyboard"),
        )
        return USER_CLIENT_ACCOUNT

    elif query.data == "back_to_menu":
        await user_show_edit_client_appointments(
            update, context, context.user_data["id"]
        )
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=USER_MESSAGES["ON_RETURN_TO_MENU"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_select_appointment_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text in context.bot_data["user_appointments_keyboard_buttons"]:
        if text == REPLY_USER_BUTTONS["RESCHEDULE_OR_CANCEL"]:
            await user_show_edit_client_appointments(
                update, context, context.user_data["id"]
            )
            return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE
        elif text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
            await user_back_to_client_account(update, context)
            return USER_CLIENT_ACCOUNT
        elif text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
            await user_show_on_return_to_menu(update, context)
            return USER_MAIN_MENU

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=USER_MESSAGES["ERROR_TRY_AGAIN"]
        )

        await user_show_edit_client_appointments(
            update, context, context.user_data["id"]
        )
        return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE


async def handle_user_appointment_edit_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    procedure = context.user_data["procedure_selected"]
    date = format_date_for_client_interface(
        context.user_data["appointment_for_editing"][2]
    )
    time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

    if text == REPLY_USER_BUTTONS["RESCHEDULE_APPOINTMENT"]:
        context.user_data["reschedule"] = True
        await update.message.reply_text(
            text=f"{procedure} - {date} - {time}",
            reply_markup=ReplyKeyboardRemove(),
        )

        await user_show_months(update, context)
        return USER_SELECT_MONTH

    if text == REPLY_USER_BUTTONS["CANCEL_APPOINTMENT"]:
        context.user_data["reschedule"] = False

        appointment_id = int(context.user_data["appointment_id"])
        print(appointment_id)
        print(type(appointment_id))
        appointments = context.bot_data["appointments"]

        appointment_data = appointments.get_client_data_by_appointment_id(
            appointment_id
        )
        try:
            appointments.delete_appointment(appointment_id)
            db_success = True
        except Exception as e:
            db_success = False
            appointments.logger.error(
                f"Ошибка при обновлении информации в базе данных: {e}"
            )
        notification_message = (
            f"Клиент {appointment_data[3]} отменил запись на процедуру "
            f'"{appointment_data[0]}"\n'
            f"Дата: {appointment_data[1]}\n"
            f"Время: {appointment_data[2].strftime("%H:%M")}\n"
            f"Телефон: {appointment_data[4]}"
        )

        if db_success:
            notification_message += "✅ Информация в базе данных обновлена."
        else:
            notification_message += (
                "❗❗❗ Информация а базе данных не обновлена. "
                "Обратитесь к разработчику или попробуйте удалить запись "
                "самостоятельно через админ-интерфейс бота."
            )

        await context.bot.send_message(
            chat_id=ID_TO_SEND_NOTIFICATIONS, text=notification_message
        )
        await update.message.reply_text(
            text=f"Запись отменена! {EMOJI["SUCCESS"]}",
            reply_markup=context.bot_data.get("user_after_edit_keyboard"),
        )
        return USER_AFTER_EDIT

    if text == REPLY_USER_BUTTONS["TO_MENU"]:
        context.user_data["reschedule"] = False
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["TO_PROFILE"]:
        context.user_data["reschedule"] = False
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT

    if text == REPLY_USER_BUTTONS["TO_MY_APPOINTMENTS"]:
        context.user_data["reschedule"] = False
        await user_show_edit_client_appointments(
            update, context, context.user_data["id"]
        )
        return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE

    else:
        context.user_data["reschedule"] = False
        await update.message.reply_text(
            text=f"{USER_MESSAGES["ERROR_TRY_AGAIN"]} \n Вы хотите отменить или перенести выбранную запись?",
            reply_markup=context.bot_data.get("user_cancel_reschedule_keyboard"),
        )
    return USER_APPOINTMENT_EDIT_ACTIONS


async def handle_user_after_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await show_visit_tg_channel_with_profile(update, context)
        return USER_FINAL_HANDLER

    else:
        await update.message.reply_text(
            text=USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_after_edit_keyboard"),
        )
        return USER_AFTER_EDIT


async def handle_user_month_selection(update: Update, context: CallbackContext):
    """Хэндлер для выбора месяца."""

    query = update.callback_query
    await query.answer()

    if query.data == "back":
        if not context.user_data["reschedule"]:
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=USER_MESSAGES["SELECT_PROCEDURE"],
                reply_markup=context.bot_data.get("procedures_keyboard"),
            )
            return USER_SELECT_PROCEDURE
        else:
            procedure = context.user_data["procedure_selected"]
            date = format_date_for_client_interface(
                context.user_data["appointment_for_editing"][2]
            )
            time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<b>Вы выбрали</b>: {procedure} - {date} - {time}.\n<b>Вы хотите отменить или перенести выбранную запись? </b>",
                parse_mode="HTML",
                reply_markup=context.bot_data.get("user_cancel_reschedule_keyboard"),
            )
        return USER_APPOINTMENT_EDIT_ACTIONS

    elif query.data.startswith("month_"):
        month_str = query.data.replace("month_", "")
        month, year = map(int, month_str.split("_"))
        context.user_data["month_selected"] = (year, month)

        available_dates = context.bot_data["schedule"].get_available_dates(
            procedure=context.user_data.get("procedure_selected"),
            target_month=context.user_data.get("month_selected"),
        )

        if available_dates:
            keyboard = date_keyboard(year, month, available_dates)
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
            chat_id=update.effective_chat.id,
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

        keyboard = date_keyboard(year, month, available_dates)
        context.user_data["date_keyboard"] = keyboard

        await user_show_dates_update_message(update, context)
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

        keyboard = time_keyboard(available_slots)
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

        await user_show_dates_callback_query(update, context)
        return USER_SELECT_DATE

    elif query.data.startswith("time_"):

        time_str = query.data.replace("time_", "")

        try:
            selected_time = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            selected_time = datetime.strptime(time_str, "%H:%M").time()

        context.user_data["time_selected"] = selected_time

        await user_show_enter_name(update, context)
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
        await user_show_back_to_time(update, context)
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

        await user_show_enter_phone(update, context)
        return USER_ENTER_PHONE


async def handle_user_enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хэндлер для ввода телефона."""

    text = update.message.text

    if text == REPLY_USER_BUTTONS["BACK_TO_NAME"]:
        await user_show_back_to_name(update, context)
        return USER_ENTER_NAME
    else:
        phone = text
        if not re.match(r"^8\d{10}$", phone):
            await user_show_invalid_phone_format(update, context)
            return USER_ENTER_PHONE

        context.user_data["phone"] = phone

        confirmation_message = CONFIRMATION_MESSAGE["BOOKING_DETAILS"].format(
            procedure=context.user_data["procedure_selected"],
            date=context.user_data["date_selected"],
            time=context.user_data["time_selected"].strftime("%H:%M"),
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
        await user_show_continue(update, context)
        if context.user_data["reschedule"]:
            appointments = context.bot_data.get("appointments")
            appointment_id = context.user_data.get("appointment_id")
            appointments.delete_appointment(appointment_id)
            notification_message = (
                f'Клиент {context.user_data["name"]} перенес запись на процедуру '
                f'"{context.user_data["procedure_selected"]}".\n'
                f'Прежняя дата: {context.user_data["appointment_for_editing"][2]} \n'
                f'Прежнее время: {context.user_data["appointment_for_editing"][3].strftime("%H:%M")} \n'
                f'Новая дата: {context.user_data["date_selected"]} \n'
                f'Новое время: {context.user_data["time_selected"].strftime("%H:%M")} \n'
                f'Телефон: {context.user_data["phone"]}\n'
            )
        else:
            notification_message = (
                f'Клиент {context.user_data["name"]} записался на процедуру '
                f'"{context.user_data["procedure_selected"]}".\n'
                f'Дата: {context.user_data["date_selected"]}, '
                f'время: {context.user_data["time_selected"].strftime("%H:%M")}.\n'
                f'Телефон: {context.user_data["phone"]}\n'
            )
        try:
            await create_appointment_from_context(update, context)
            db_success = True
        except Exception as e:
            db_success = False
            logger.error(f"Ошибка при записи в базу данных: {e}")

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
        if not context.user_data["reschedule"]:
            return USER_AFTER_CONFIRMATION
        else:
            context.user_data["reschedule"] = False
            return USER_AFTER_EDIT

    elif query.data == "cancel":
        if not context.user_data["reschedule"]:
            await user_show_cancel_booking(update, context)
            return USER_AFTER_CONFIRMATION
        else:
            context.user_data["reschedule"] = False
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{EMOJI['ERROR']} Операция прервана, запись не перенесена.",
                reply_markup=context.bot_data.get("user_after_edit_keyboard"),
            )
            return USER_AFTER_EDIT

    elif query.data == "back_to_edit":
        await user_show_back_to_edit(update, context)
        return USER_ENTER_PHONE


async def handle_user_confirmation_unexpected_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Хэндлер для обработки непредвиденного ввода при подтверждении или отмене записи."""

    text = update.message.text
    if text == REPLY_USER_BUTTONS["BACK_TO_PHONE"]:
        await user_show_edit_phone(update, context)
        return USER_ENTER_PHONE

    if text == REPLY_USER_BUTTONS["BACK_TO_NAME"]:
        await user_show_enter_name(update, context)
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
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]:
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await show_visit_tg_channel(update, context)
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

    if query.data == "back_to_profile":
        text = USER_MESSAGES["BACK_TO_PROFILE"]
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=context.bot_data.get("user_account_keyboard"),
        )
        return USER_CLIENT_ACCOUNT

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )
        return USER_MAIN_MENU


async def handle_user_final_text_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text
    if text == REPLY_USER_BUTTONS["SELECT_PROCEDURE"]:
        await user_show_procedures(update, context)
        return USER_SELECT_PROCEDURE

    if (
        text == REPLY_USER_BUTTONS["BACK_TO_PROFILE"]
        or text == REPLY_USER_BUTTONS["CLIENT_ACCOUNT"]
    ):
        await user_back_to_client_account(update, context)
        return USER_CLIENT_ACCOUNT

    if text == REPLY_USER_BUTTONS["BACK_TO_MENU"]:
        await user_show_on_return_to_menu(update, context)
        return USER_MAIN_MENU

    if text == REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"]:
        await show_visit_tg_channel(update, context)
        return USER_FINAL_HANDLER

    if text == REPLY_USER_BUTTONS["CONTACT_MASTER"]:
        await show_contact_master(update, context)
        return USER_FINAL_HANDLER

    else:
        await update.message.reply_text(
            USER_MESSAGES["ERROR_TRY_AGAIN"],
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )
        return USER_FINAL_HANDLER
