from telegram.ext import Application
from keyboards.user_keyboards import *
from keyboards.general_keyboards import *
from keyboards.admin_keyboards import *


def setup_keyboards(app: Application):
    user_keyboards = UserKeyboards().get_keyboards()
    app.bot_data["user"]["keyboards"] = user_keyboards

    
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

    # return user_keyboards, admin_keyboards, general_keyboards
    return user_keyboards