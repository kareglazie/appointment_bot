from telegram.ext import Application
from handlers.admin_handler import AdminHandler
from interfaces.admin_interface import AdminInterface
from logger import setup_logger
from database.setup import setup_database
from handlers.user_handler import UserHandler
from interfaces.user_interface import UserInterface
from keyboards.setup import setup_keyboards


def setup_bot_data(app: Application):

    user_keyboards, admin_keyboards, general_keyboards, dyn_keyboards = setup_keyboards(
        app
    )
    user_interface = UserInterface(user_keyboards, general_keyboards)
    user_handler = UserHandler(user_interface, dyn_keyboards).get_handlers()
    admin_interface = AdminInterface(admin_keyboards, general_keyboards)
    admin_handler = AdminHandler(admin_interface, dyn_keyboards).get_handlers()

    database = setup_database()
    app.bot_data["db"] = database

    logger = setup_logger(__name__)
    app.bot_data["logger"] = logger

    app.bot_data["general"] = {"keyboards": general_keyboards}

    app.bot_data["user"] = {
        "keyboards": user_keyboards,
        "interface": user_interface,
        "handler": user_handler,
    }

    app.bot_data["admin"] = {"keyboards": admin_keyboards, "handler": admin_handler}
