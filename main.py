from config import TOKEN
from database.setup import setup_database
from handlers.admin_handlers import *
from handlers.general_handlers import *
from handlers.user_handlers import *

from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

from keyboards.setup import setup_keyboards
from logger import setup_logger
from states import START

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


def main():
    try:
        database = setup_database()
        app = Application.builder().token(TOKEN).build()

        logger = setup_logger(__name__)

        app.bot_data.update(database)
        app.bot_data["logger"] = logger

        setup_keyboards(app)

        user_handlers = get_user_handlers()
        admin_handlers = get_admin_handlers()

        start = CommandHandler("start", start_handler)
        restart = CommandHandler("start", start_handler)

        conv_handler = ConversationHandler(
            entry_points=[start, restart],
            states={
                START: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler)],
                **user_handlers,
                **admin_handlers,
            },
            fallbacks=[start],
            per_message=False,
        )

        app.add_handler(conv_handler)

        app.run_polling()

    except KeyboardInterrupt:
        logger.debug("Бот остановлен.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        if "db" in locals():
            database["db"].close()
            logger.debug("База данных закрыта.")


if __name__ == "__main__":
    main()
