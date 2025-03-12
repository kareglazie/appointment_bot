from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from messages import INLINE_BUTTONS, REPLY_USER_BUTTONS


def user_main_menu_keyboard() -> ReplyKeyboardMarkup:
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


def tg_channel_keyboard() -> InlineKeyboardMarkup:
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


def tg_channel_with_profile_keyboard() -> InlineKeyboardMarkup:
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


def contact_master_keyboard() -> InlineKeyboardMarkup:
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


def user_final_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для возврата в главное меню или перехода в тг-канал."""

    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
            [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def user_account_keyboard() -> ReplyKeyboardMarkup:
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


def user_appointments_keyboard() -> ReplyKeyboardMarkup:
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


def user_cancel_reschedule_keyboard() -> ReplyKeyboardMarkup:
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


def user_after_edit_keyboard() -> ReplyKeyboardMarkup:

    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_PROFILE"])],
            [KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])],
            [KeyboardButton(REPLY_USER_BUTTONS["VISIT_TG_CHANNEL"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def user_personal_data_keyboard() -> InlineKeyboardMarkup:
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
