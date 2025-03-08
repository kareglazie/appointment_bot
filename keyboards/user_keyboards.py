from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from messages import INLINE_BUTTONS, REPLY_USER_BUTTONS


class UserKeyboards:
    @staticmethod
    def user_main_menu_keyboard():
        """Клавиатура главного меню пользователя."""

        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["SELECT_PROCEDURE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["CONTACT_MASTER"])],
                [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    @staticmethod
    def tg_channel_keyboard():
        """Клавиатура для перехода в тг-канал или возврата в меню."""

        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TG_CHANNEL"], url=INLINE_BUTTONS["TG_CHANNEL_URL"]
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TO_MENU"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def contact_master_keyboard():
        """Клавиатура для перехода в тг-чат с мастером или возврата в меню."""

        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["CHAT_WITH_MASTER"],
                    url=INLINE_BUTTONS["CHAT_WITH_MASTER_URL"],
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["BACK_TO_MENU"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def user_final_keyboard():
        """Клавиатура для возврата в главное меню или перехода в тг-канал."""

        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
                [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
