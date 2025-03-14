from telegram.ext import Application
from keyboards.user_keyboards import *
from keyboards.general_keyboards import *
from keyboards.admin_keyboards import *


def setup_keyboards(app: Application):
    user_keyboards = UserKeyboards().get_keyboards()
    general_keyboards = GeneralKeyboards().get_keyboards()
    dyn_keyboards = GeneralKeyboards()

    app.bot_data["admin_main_menu_keyboard"] = admin_main_menu_keyboard()
    app.bot_data["admin_final_keyboard"] = admin_final_keyboard()

    # app.bot_data["user_appointments_keyboard_buttons"] = [
    #     button.text
    #     for row in app.bot_data["user_appointments_keyboard"].keyboard
    #     for button in row
    # ]

    # return user_keyboards, admin_keyboards, general_keyboards
    return user_keyboards, general_keyboards, dyn_keyboards
