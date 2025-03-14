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
            "personal_data": self.personal_data(),
        }

    def main_menu(self) -> ReplyKeyboardMarkup:
        """Клавиатура главного меню пользователя."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["select_procedure"])],
                [KeyboardButton(REPLY_USER_BUTTONS["client_account"])],
                [KeyboardButton(REPLY_USER_BUTTONS["contact_master"])],
                [KeyboardButton(REPLY_USER_BUTTONS["visit_tg_channel"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def go_to_tg_channel(self) -> InlineKeyboardMarkup:
        """Клавиатура для перехода в тг-канал или возврата в меню."""
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["tg_channel"], url=INLINE_BUTTONS["tg_channel_url"]
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["to_menu"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def go_to_tg_channel_with_profile(self) -> InlineKeyboardMarkup:
        """Клавиатура для перехода в тг-канал, возврата в меню или в профиль (личный кабинет)."""
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["tg_channel"], url=INLINE_BUTTONS["tg_channel_url"]
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["to_profile"], callback_data="back_to_profile"
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["to_menu"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def contact_master(self) -> InlineKeyboardMarkup:
        """Клавиатура для перехода в тг-чат с мастером или возврата в меню."""
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["chat_with_master"],
                    url=INLINE_BUTTONS["chat_with_master_url"],
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_menu"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def final(self) -> ReplyKeyboardMarkup:
        """Клавиатура для возврата в главное меню или перехода в тг-канал."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_menu"])],
                [KeyboardButton(REPLY_USER_BUTTONS["visit_tg_channel"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def user_account(self) -> ReplyKeyboardMarkup:
        """Клавиатура для просмотра и отмены записей."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["my_appointments"])],
                [KeyboardButton(REPLY_USER_BUTTONS["my_profile"])],
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_menu"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def appointments(self) -> ReplyKeyboardMarkup:
        """Клавиатура для просмотра и отмены записей."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["reschedule_or_cancel"])],
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_profile"])],
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_menu"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def cancel_reschedule(self) -> ReplyKeyboardMarkup:
        """Клавиатура для выбора действия для применения к записи - отмена или перенос."""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["reschedule_appointment"])],
                [KeyboardButton(REPLY_USER_BUTTONS["cancel_appointment"])],
                [KeyboardButton(REPLY_USER_BUTTONS["to_profile"])],
                [KeyboardButton(REPLY_USER_BUTTONS["to_my_appointments"])],
                [KeyboardButton(REPLY_USER_BUTTONS["to_menu"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def after_edit(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_profile"])],
                [KeyboardButton(REPLY_USER_BUTTONS["back_to_menu"])],
                [KeyboardButton(REPLY_USER_BUTTONS["visit_tg_channel"])],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def personal_data(self) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["telephone"], callback_data="telephone"
                )
            ],
            [InlineKeyboardButton(INLINE_BUTTONS["name"], callback_data="client_name")],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["to_profile"], callback_data="back_to_profile"
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["to_menu"], callback_data="back_to_menu"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)