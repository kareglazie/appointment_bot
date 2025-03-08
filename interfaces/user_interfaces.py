from telegram import KeyboardButton, ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from messages import USER_MESSAGES, EMOJI, REPLY_USER_BUTTONS


class UserInterface:
    """Класс для управления интерфейсом пользователя."""

    @staticmethod
    async def user_show_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["SELECT_MONTH"],
            reply_markup=context.bot_data.get("month_keyboard"),
        )

    @staticmethod
    async def user_show_procedures(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["SELECT_PROCEDURE"],
            reply_markup=context.bot_data.get("procedures_keyboard"),
        )

    @staticmethod
    async def user_show_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["SELECT_MONTH"],
            reply_markup=context.bot_data.get("month_keyboard"),
        )

    @staticmethod
    async def user_show_dates_update_message(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.message.reply_text(
            USER_MESSAGES["SELECT_DATE"],
            reply_markup=context.user_data.get("date_keyboard"),
        )

    @staticmethod
    async def user_show_dates_callback_query(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.callback_query.edit_message_text(
            USER_MESSAGES["SELECT_DATE"],
            reply_markup=context.user_data.get("date_keyboard"),
        )

    @staticmethod
    async def show_contact_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["GO_TO_CHAT"],
            reply_markup=context.bot_data.get("contact_master_keyboard"),
        )

    @staticmethod
    async def show_visit_tg_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["GO_TO_TG_CHANNEL"],
            reply_markup=context.bot_data.get("tg_channel_keyboard"),
        )

    @staticmethod
    async def user_show_on_return_to_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.message.reply_text(
            USER_MESSAGES["ON_RETURN_TO_MENU"],
            reply_markup=context.bot_data.get("user_main_menu_keyboard"),
        )

    @staticmethod
    async def user_show_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=USER_MESSAGES["ENTER_NAME"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_TIME"])]],
                resize_keyboard=True,
            ),
        )

    @staticmethod
    async def user_show_back_to_name(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.message.reply_text(
            USER_MESSAGES["ENTER_NAME"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_TIME"])]],
                resize_keyboard=True,
            ),
        )

    @staticmethod
    async def user_show_back_to_time(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.message.reply_text(
            text=f"Давайте подберем подходящее время {EMOJI['SPARKLE']}",
            reply_markup=ReplyKeyboardRemove(),
        )

        await update.message.reply_text(
            USER_MESSAGES["SELECT_TIME"],
            reply_markup=context.user_data.get("time_keyboard"),
        )

    @staticmethod
    async def user_show_enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["ENTER_PHONE"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]],
                resize_keyboard=True,
            ),
        )

    @staticmethod
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

    @staticmethod
    async def user_show_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            USER_MESSAGES["EDIT_PHONE"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]],
                resize_keyboard=True,
            ),
        )

    @staticmethod
    async def user_show_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=f"Продолжим? {EMOJI['SPARKLE']}",
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )

    @staticmethod
    async def user_show_cancel_booking(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=USER_MESSAGES["BOOKING_CANCELLED"],
            reply_markup=context.bot_data.get("user_final_keyboard"),
        )

    @staticmethod
    async def user_show_back_to_edit(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=USER_MESSAGES["EDIT_PHONE"],
            reply_markup=ReplyKeyboardMarkup(
                [[REPLY_USER_BUTTONS["BACK_TO_NAME"]]], resize_keyboard=True
            ),
        )
