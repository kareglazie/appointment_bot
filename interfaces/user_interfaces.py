from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes
from messages import INLINE_BUTTONS, USER_MESSAGES, EMOJI, REPLY_USER_BUTTONS
from utils.formatter import format_date_for_client_interface


async def user_show_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["SELECT_MONTH"],
        reply_markup=context.bot_data.get("month_keyboard"),
    )


async def user_show_procedures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["SELECT_PROCEDURE"],
        reply_markup=context.bot_data.get("procedures_keyboard"),
    )


async def user_show_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["SELECT_MONTH"],
        reply_markup=context.bot_data.get("month_keyboard"),
    )


async def user_show_dates_update_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        USER_MESSAGES["SELECT_DATE"],
        reply_markup=context.user_data.get("date_keyboard"),
    )


async def user_show_dates_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.callback_query.edit_message_text(
        USER_MESSAGES["SELECT_DATE"],
        reply_markup=context.user_data.get("date_keyboard"),
    )


async def show_contact_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["GO_TO_CHAT"],
        reply_markup=context.bot_data.get("contact_master_keyboard"),
    )


async def show_visit_tg_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["GO_TO_TG_CHANNEL"],
        reply_markup=context.bot_data.get("tg_channel_keyboard"),
    )


async def show_visit_tg_channel_with_profile(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        USER_MESSAGES["GO_TO_TG_CHANNEL"],
        reply_markup=context.bot_data.get("tg_channel_with_profile_keyboard"),
    )


async def user_show_on_return_to_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        USER_MESSAGES["ON_RETURN_TO_MENU"],
        reply_markup=context.bot_data.get("user_main_menu_keyboard"),
    )


async def user_show_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=USER_MESSAGES["ENTER_NAME"],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_TIME"])]],
            resize_keyboard=True,
        ),
    )


async def user_show_back_to_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["ENTER_NAME"],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_TIME"])]],
            resize_keyboard=True,
        ),
    )


async def user_show_back_to_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=f"Давайте подберем подходящее время {EMOJI['SPARKLE']}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await update.message.reply_text(
        USER_MESSAGES["SELECT_TIME"],
        reply_markup=context.user_data.get("time_keyboard"),
    )


async def user_show_enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["ENTER_PHONE"],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]],
            resize_keyboard=True,
        ),
    )


async def user_show_invalid_phone_format(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        USER_MESSAGES["INVALID_PHONE_FORMAT"],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]],
            resize_keyboard=True,
        ),
    )


async def user_show_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["EDIT_PHONE"],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]],
            resize_keyboard=True,
        ),
    )


async def user_show_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data["reschedule"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Продолжим? {EMOJI['SPARKLE']}",
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Продолжим? {EMOJI['SPARKLE']}",
            reply_markup=context.bot_data.get("user_after_edit_keyboard"),
        )


async def user_show_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=USER_MESSAGES["BOOKING_CANCELLED"],
        reply_markup=context.bot_data.get("user_final_keyboard"),
    )


async def user_show_back_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=USER_MESSAGES["EDIT_PHONE"],
        reply_markup=ReplyKeyboardMarkup(
            [[REPLY_USER_BUTTONS["BACK_TO_NAME"]]], resize_keyboard=True
        ),
    )


async def user_show_client_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_username = context.user_data.get("tg_username")
    hello_text = f"{EMOJI['SPARKLE']} Здравствуйте, {tg_username}! \nЗдесь вы можете просмотреть, перенести или отменить свои записи, а также изменить данные о себе (имя или телефон).{EMOJI['SPARKLE']}"
    await update.message.reply_text(
        text=hello_text, reply_markup=context.bot_data.get("user_account_keyboard")
    )


async def user_back_to_client_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text=USER_MESSAGES["BACK_TO_PROFILE"],
        reply_markup=context.bot_data.get("user_account_keyboard"),
    )


async def user_show_client_appointments(
    update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
):
    appointments_list = context.bot_data["appointments"].get_client_appointments(
        client_id
    )
    context.user_data["appointments_list"] = appointments_list
    appointments_text = f"{EMOJI['USER']} <b>Ваши записи:</b>\n————————————\n"
    for appointment in appointments_list:
        procedure = appointment[1]
        date = appointment[2]
        start_time = appointment[3].strftime("%H:%M") if appointment[2] else ""
        end_time = appointment[4].strftime("%H:%M") if appointment[3] else ""
        formatted_date = format_date_for_client_interface(date)
        text = (
            f"{EMOJI['SPARKLE']} <i>{procedure}</i>\n"
            f"{EMOJI['CALENDAR']} <i>Дата:</i> {formatted_date}\n"
            f"{EMOJI['CLOCK']} <i>Время:</i> {start_time} – {end_time}\n"
            "————————————\n"
        )
        appointments_text += text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=appointments_text,
        parse_mode="HTML",
        reply_markup=context.bot_data.get("user_appointments_keyboard"),
    )


async def user_show_edit_client_appointments(
    update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
):

    keyboard = []
    for appointment in context.user_data["appointments_list"]:
        id = appointment[0]
        procedure = appointment[1]
        date = appointment[2]
        start_time = appointment[3].strftime("%H:%M") if appointment[2] else ""
        formatted_date = format_date_for_client_interface(date)
        text = f"{procedure} - " f"{formatted_date} - " f"{start_time}"

        keyboard.append(
            [InlineKeyboardButton(text, callback_data=f"select_appointment_{id}")]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["BACK_TO_PROFILE"], callback_data="back_to_profile"
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["BACK_TO_MENU"], callback_data="back_to_menu"
            )
        ]
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, выберите запись, которую хотите отменить или перенести:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def user_show_personal_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = context.user_data["tg_id"]
    clients = context.bot_data.get("clients")
    name = clients.get_client_name_by_tg_id(tg_id)
    phone = clients.get_client_phone_by_tg_id(tg_id)
    await update.message.reply_text(
        text=f"<b> Ваши данные </b> \n {EMOJI['PHONE']} Телефон: {phone}\n {EMOJI['USER']} Имя: {name}. \n Хотите что-то изменить?",
        parse_mode="HTML",
        reply_markup=context.bot_data.get("user_personal_data_keyboard"),
    )
