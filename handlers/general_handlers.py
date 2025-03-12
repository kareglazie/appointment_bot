from telegram import (
    Update,
)
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from messages import EMOJI
from states import *
from utils.utils import basic_context_update


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await basic_context_update(update, context)
    context.user_data["reschedule"] = False

    if context.user_data["tg_id"] in ADMIN_IDS:
        await update.message.reply_text(
            "ADMIN! Пожалуйста, выберите действие",
            reply_markup=context.bot_data["admin_main_menu_keyboard"],
        )
        return ADMIN_ACTIONS

    else:
        await update.message.reply_text(
            f"{EMOJI['SPARKLE']} Добрый день, {context.user_data['tg_username']}! Чем вам помочь?",
            reply_markup=context.bot_data["user_main_menu_keyboard"],
        )
        return USER_MAIN_MENU
