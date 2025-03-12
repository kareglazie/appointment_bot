from telegram.ext import Application
from keyboards.user_keyboards import *
from keyboards.general_keyboards import *
from keyboards.admin_keyboards import *


def setup_keyboards(app: Application):

    app.bot_data["user_main_menu_keyboard"] = user_main_menu_keyboard()
    app.bot_data["user_final_keyboard"] = user_final_keyboard()
    app.bot_data["tg_channel_keyboard"] = tg_channel_keyboard()
    app.bot_data["contact_master_keyboard"] = contact_master_keyboard()
    app.bot_data["user_account_keyboard"] = user_account_keyboard()
    app.bot_data["user_appointments_keyboard"] = user_appointments_keyboard()
    app.bot_data["user_cancel_reschedule_keyboard"] = user_cancel_reschedule_keyboard()
    app.bot_data["user_after_edit_keyboard"] = user_after_edit_keyboard()
    app.bot_data["user_personal_data_keyboard"] = user_personal_data_keyboard()
    app.bot_data["tg_channel_with_profile_keyboard"] = (
        tg_channel_with_profile_keyboard()
    )

    app.bot_data["admin_main_menu_keyboard"] = admin_main_menu_keyboard()
    app.bot_data["admin_final_keyboard"] = admin_final_keyboard()

    app.bot_data["procedures_keyboard"] = procedures_keyboard()
    app.bot_data["month_keyboard"] = month_keyboard()
    app.bot_data["confirmation_keyboard"] = confirmation_keyboard()
    app.bot_data["procedures_keyboard_buttons"] = [
        button.text
        for row in app.bot_data["procedures_keyboard"].keyboard
        for button in row
    ]
    app.bot_data["user_appointments_keyboard_buttons"] = [
        button.text
        for row in app.bot_data["user_appointments_keyboard"].keyboard
        for button in row
    ]
