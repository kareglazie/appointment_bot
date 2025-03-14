from telegram import (
    Update,
)
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from consts.messages import ADMIN_MESSAGES, EMOJI
from states import *
from utils.utils import basic_context_update


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await basic_context_update(update, context)
    context.user_data["reschedule"] = False

    if context.user_data["tg_id"] in ADMIN_IDS:
        await update.message.reply_text(
            text=ADMIN_MESSAGES["hello_admin"],
            reply_markup=context.bot_data["admin"]["keyboards"]["main_menu"],
        )
        return ADMIN_MAIN_MENU

    else:
        await update.message.reply_text(
            f"{EMOJI['sparkle']} Добрый день, {context.user_data['tg_username']}! Чем вам помочь?",
            reply_markup=context.bot_data["user"]["keyboards"]["main_menu"],
        )
        return USER_MAIN_MENU
