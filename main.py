from bot_setup import setup_bot_data
from config import TOKEN
from handlers.general_handler import *

from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    filters,
)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

from states import START

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


def main():
    try:
        app = Application.builder().token(TOKEN).build()
        setup_bot_data(app)

        user_handler = app.bot_data["user"]["handler"]
        admin_handler = app.bot_data["admin"]["handler"]

        start = CommandHandler("start", start_handler)
        restart = CommandHandler("start", start_handler)

        conv_handler = ConversationHandler(
            entry_points=[start, restart],
            states={
                START: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler)],
                **user_handler,
                **admin_handler,
            },
            fallbacks=[start],
            per_message=False,
        )

        app.add_handler(conv_handler)

        app.run_polling()

    except KeyboardInterrupt:
        app.bot_data["logger"].debug("Бот остановлен.")
    except Exception as e:
        app.bot_data["logger"].error(f"Ошибка: {e}")
    finally:
        if "db" in locals():
            app.bot_data["db"]["db"].close()
            app.bot_data["logger"].debug("База данных закрыта.")


if __name__ == "__main__":
    main()
