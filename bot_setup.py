from database.setup import setup_database
from interfaces.user_interfaces import UserInterface
from keyboards.setup import setup_keyboards
from telegram.ext import Application

from logger import setup_logger

async def setup_bot_data(app: Application):

    # user_keyboards, admin_keyboards, general_keyboards = setup_keyboards(app)
    user_keyboards, general_keyboards = setup_keyboards(app)
    user_interface = UserInterface(user_keyboards, general_keyboards) 
    
    database = setup_database()
    app.bot_data["db"] = database
    
    logger = setup_logger(__name__)
    app.bot_data["logger"] = logger
    
    app.bot_data["user"]["keyboards"] = user_keyboards
    app.bot_data["general"]["keyboards"] = general_keyboards

    app.bot_data["user"]["interface"] = user_interface
    
