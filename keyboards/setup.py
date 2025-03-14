from telegram.ext import Application
from keyboards.user_keyboards import *
from keyboards.general_keyboards import *
from keyboards.admin_keyboards import *


def setup_keyboards(app: Application):

    user_keyboards = UserKeyboards().get_keyboards()
    admin_keyboards = AdminKeyboards().get_keyboards()
    general_keyboards = GeneralKeyboards().get_keyboards()
    dyn_keyboards = GeneralKeyboards()

    return user_keyboards, admin_keyboards, general_keyboards, dyn_keyboards
