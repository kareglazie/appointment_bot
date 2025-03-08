from telegram.ext import Application
from keyboards.user_keyboards import *
from keyboards.general_keyboards import *


def user_static_keyboards_setup(app: Application):
    app.bot_data["user_main_menu_keyboard"] = user_main_menu_keyboard()
    app.bot_data["user_final_keyboard"] = user_final_keyboard()
    app.bot_data["tg_channel_keyboard"] = tg_channel_keyboard()
    app.bot_data["contact_master_keyboard"] = contact_master_keyboard()


def admin_static_keyboards_setup(app: Application):
    pass


def general_static_keyboards_setup(app: Application):
    app.bot_data["procedures_keyboard"] = procedures_keyboard()
    app.bot_data["month_keyboard"] = month_keyboard()
    app.bot_data["procedures_keyboard_buttons"] = [
        button.text
        for row in app.bot_data["procedures_keyboard"].keyboard
        for button in row
    ]
    app.bot_data["confirmation_keyboard"] = confirmation_keyboard()


def all_static_keyboards_setup(app: Application):
    user_static_keyboards_setup(app)
    admin_static_keyboards_setup(app)
    general_static_keyboards_setup(app)
