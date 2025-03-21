from typing import Dict
from telegram import KeyboardButton, ReplyKeyboardMarkup

from consts.messages import REPLY_ADMIN_BUTTONS


class AdminKeyboards:

    def __init__(self):
        pass

    def get_keyboards(self) -> Dict:
        return {
            "main_menu": self.main_menu(),
            "dates_menu": self.dates_menu(),
            "appointments_menu": self.appointments_menu(),
            "client": self.client(),
            "view_dates": self.view_dates(),
            "appointments_actions": self.appointments_actions(),
            "delete_client": self.delete_client(),
            "block_day": self.block_day(),
        }

    def main_menu(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["dates"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["clients"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["appointments"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def dates_menu(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["view_available_dates"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["block_day_or_time"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def client(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["view_client_appointments"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["delete_client"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def view_dates(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["select_procedure"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["view_all_dates"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def appointments_menu(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["view_appointments"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["add_appointment"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def appointments_actions(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["reschedule_appointment"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["delete_appointment"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_appointments"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def delete_client(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(REPLY_ADMIN_BUTTONS["delete"])],
            [KeyboardButton(REPLY_ADMIN_BUTTONS["dont_delete_back_to_menu"])],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    def admin_final_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            [[REPLY_ADMIN_BUTTONS["back_to_menu"]]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def block_day(self) -> ReplyKeyboardMarkup:
        keyboard = [
            [REPLY_ADMIN_BUTTONS["block_whole_day"]],
            [REPLY_ADMIN_BUTTONS["select_time"]],
            [REPLY_ADMIN_BUTTONS["back_to_menu"]],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
