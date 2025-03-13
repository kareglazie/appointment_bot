from typing import Dict
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from consts.messages import INLINE_BUTTONS, REPLY_USER_BUTTONS

class UserKeyboards:

    def __init__(self):
        pass

    def get_keyboards(self) -> Dict:
        return {
            "main_menu": self.main_menu(),
            "final": self.final(),
            "go_to_tg_channel": self.go_to_tg_channel(),
            "go_to_tg_channel_with_profile": self.go_to_tg_channel_with_profile(),
            "contact_master": self.contact_master(),
            "user_account": self.user_account(),
            "appointments": self.appointments(),
            "cancel_reschedule": self.cancel_reschedule(),
            "after_edit": self.after_edit(),
            "personal_data": self.personal_data()
        }
    
    def main_menu(self) -> ReplyKeyboardMarkup:
        """Клавиатура главного меню пользователя."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["SELECT_PROCEDURE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["CLIENT_ACCOUNT"])],
                [KeyboardButton(REPLY_USER_BUTTONS["CONTACT_MASTER"])],
                [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def go_to_tg_channel(self) -> InlineKeyboardMarkup:
        """Клавиатура для перехода в тг-канал или возврата в меню."""
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TG_CHANNEL"], url=INLINE_BUTTONS["TG_CHANNEL_URL"]
                )
            ],
            [InlineKeyboardButton(INLINE_BUTTONS["TO_MENU"], callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    def go_to_tg_channel_with_profile(self) -> InlineKeyboardMarkup:
        """Клавиатура для перехода в тг-канал, возврата в меню или в профиль (личный кабинет)."""
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TG_CHANNEL"], url=INLINE_BUTTONS["TG_CHANNEL_URL"]
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TO_PROFILE"], callback_data="back_to_profile"
                )
            ],
            [InlineKeyboardButton(INLINE_BUTTONS["TO_MENU"], callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    def contact_master(self) -> InlineKeyboardMarkup:
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

    def final(self) -> ReplyKeyboardMarkup:
        """Клавиатура для возврата в главное меню или перехода в тг-канал."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
                [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def user_account(self) -> ReplyKeyboardMarkup:
        """Клавиатура для просмотра и отмены записей."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["MY_APPOINTMENTS"])],
                [KeyboardButton(REPLY_USER_BUTTONS["MY_PROFILE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def appointments(self) -> ReplyKeyboardMarkup:
        """Клавиатура для просмотра и отмены записей."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["RESCHEDULE_OR_CANCEL"])],
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def cancel_reschedule(self) -> ReplyKeyboardMarkup:
        """Клавиатура для выбора действия для применения к записи - отмена или перенос."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["RESCHEDULE_APPOINTMENT"])],
                [KeyboardButton(REPLY_USER_BUTTONS["CANCEL_APPOINTMENT"])],
                [KeyboardButton(REPLY_USER_BUTTONS["TO_PROFILE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["TO_MY_APPOINTMENTS"])],
                [KeyboardButton(REPLY_USER_BUTTONS["TO_MENU"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def after_edit(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])],
                [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
                [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def personal_data(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(INLINE_BUTTONS["TELEPHONE"], callback_data="telephone")],
            [InlineKeyboardButton(INLINE_BUTTONS["NAME"], callback_data="client_name")],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["TO_PROFILE"], callback_data="back_to_profile"
                )
            ],
            [InlineKeyboardButton(INLINE_BUTTONS["TO_MENU"], callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)