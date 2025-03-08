from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes
from messages import EMOJI, INLINE_BUTTONS, REPLY_USER_BUTTONS, USER_MESSAGES


def user_main_menu_keyboard():
    """Клавиатура главного меню пользователя."""

    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(REPLY_USER_BUTTONS["SELECT_PROCEDURE"])],
            [KeyboardButton(REPLY_USER_BUTTONS["CONTACT_MASTER"])],
            [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def tg_channel_keyboard():
    """Клавиатура для перехода в тг-канал или возврата в меню."""

    keyboard = [
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["TG_CHANNEL"], url=INLINE_BUTTONS["TG_CHANNEL_URL"]
            )
        ],
        [InlineKeyboardButton(INLINE_BUTTONS["TO_MENU"], callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def contact_master_keyboard():
    """Клавиатура для перехода в тг-чат с мастером или возврата в меню."""

    keyboard = [
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["CHAT_WITH_MASTER"],
                url=INLINE_BUTTONS["CHAT_WITH_MASTER_URL"],
            )
        ],
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["BACK_TO_MENU"], callback_data="back_to_menu"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def user_final_keyboard():
    """Клавиатура для возврата в главное меню или перехода в тг-канал."""

    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
            [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


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


async def user_show_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        USER_MESSAGES["SELECT_DATE"],
        reply_markup=context.user_data.get("date_keyboard"),
    )


async def user_show_dates_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def user_show_on_return_to_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        USER_MESSAGES["ON_RETURN_TO_MENU"],
        reply_markup=context.bot_data.get("user_main_menu_keyboard"),
    )


async def user_show_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
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
            [[KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_NAME"])]], resize_keyboard=True
        ),
    )


async def user_show_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=f"Продолжим? {EMOJI['SPARKLE']}",
        reply_markup=context.bot_data.get("user_final_keyboard"),
    )


async def user_show_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=USER_MESSAGES["BOOKING_CANCELLED"],
        reply_markup=context.bot_data.get("user_final_keyboard"),
    )


async def user_show_back_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=USER_MESSAGES["EDIT_PHONE"],
        reply_markup=ReplyKeyboardMarkup(
            [[REPLY_USER_BUTTONS["BACK_TO_NAME"]]], resize_keyboard=True
        ),
    )
