from telegram import (
    Update,
)
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from messages import EMOJI
from states import *
from utils.utils import basic_context_update
from keyboards.user_keyboards import user_main_menu_keyboard
from keyboards.admin_keyboards import admin_main_menu_keyboard


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await basic_context_update(update, context)

    if context.user_data["user_id"] in ADMIN_IDS:
        await update.message.reply_text(
            "ADMIN! Пожалуйста, выберите действие",
            reply_markup=admin_main_menu_keyboard(),
        )
        return ADMIN_ACTIONS

    else:
        await basic_context_update(update, context)
        await update.message.reply_text(
            f"{EMOJI['SPARKLE']} Добрый день, {context.user_data['user_tg_username']}! Чем вам помочь?",
            reply_markup=user_main_menu_keyboard(),
        )
        return USER_MAIN_MENU
