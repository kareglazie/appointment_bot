from telegram.ext import Application
from keyboards.user_keyboards import UserKeyboards
from keyboards.general_keyboards import GeneralKeyboards
from keyboards.admin_keyboards import AdminKeyboards


def setup_keyboards(app: Application):

    user_keyboards = UserKeyboards()
    admin_keyboards = AdminKeyboards()
    general_keyboards = GeneralKeyboards()

    app.bot_data["user_main_menu_keyboard"] = user_keyboards.user_main_menu_keyboard()
    app.bot_data["user_final_keyboard"] = user_keyboards.user_final_keyboard()
    app.bot_data["tg_channel_keyboard"] = user_keyboards.tg_channel_keyboard()
    app.bot_data["contact_master_keyboard"] = user_keyboards.contact_master_keyboard()

    app.bot_data["admin_main_menu_keyboard"] = (
        admin_keyboards.admin_main_menu_keyboard()
    )
    app.bot_data["admin_final_keyboard"] = admin_keyboards.admin_final_keyboard()

    app.bot_data["procedures_keyboard"] = general_keyboards.procedures_keyboard()
    app.bot_data["month_keyboard"] = general_keyboards.month_keyboard()
    app.bot_data["confirmation_keyboard"] = general_keyboards.confirmation_keyboard()
    app.bot_data["procedures_keyboard_buttons"] = [
        button.text
        for row in app.bot_data["procedures_keyboard"].keyboard
        for button in row
    ]
