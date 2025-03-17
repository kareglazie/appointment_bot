from datetime import date, datetime, time
from typing import List, Tuple
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes
from consts.messages import ADMIN_MESSAGES, INLINE_BUTTONS, REPLY_ADMIN_BUTTONS, EMOJI
from utils.formatter import format_date_for_client_interface, format_date_for_keyboard


class AdminInterface:
    def __init__(self, admin_keyboards, general_keyboards):
        self.admin_keyboards = admin_keyboards
        self.general_keyboards = general_keyboards

    async def main_menu(self, update: Update):
        await update.message.reply_text(
            text=ADMIN_MESSAGES["main_menu"],
            reply_markup=self.admin_keyboards["main_menu"],
        )

    async def dates_menu(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["dates_menu"],
            reply_markup=self.admin_keyboards["dates_menu"],
        )

    async def clients_menu(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["clients_menu"],
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton(REPLY_ADMIN_BUTTONS["fetch_all_clients"])],
                    [KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])],
                ],
                resize_keyboard=True,
            ),
        )

    async def client(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["client_data"],
            reply_markup=self.admin_keyboards["client"],
        )

    async def view_dates(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["view_dates"],
            reply_markup=self.admin_keyboards["view_dates"],
        )

    async def procedures(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["select_procedure"],
            reply_markup=self.general_keyboards["procedures"],
        )

    async def months(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["select_month"],
            reply_markup=self.general_keyboards["months"],
        )

    async def appointments_menu(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["appointments_menu"],
            reply_markup=self.admin_keyboards["appointments_menu"],
        )

    async def dates(self, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["select_date"],
            reply_markup=context.user_data.get("date_keyboard"),
        )

    async def back_to_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=f"{EMOJI['blue_heart']}{EMOJI['time']}{EMOJI['blue_heart']}",
            reply_markup=ReplyKeyboardRemove(),
        )

        await update.message.reply_text(
            text=f"{format_date_for_client_interface(context.user_data['date_selected'])}\n{ADMIN_MESSAGES["select_time"]}",
            reply_markup=context.user_data.get("time_keyboard"),
        )

    async def invalid_phone_format(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["invalid_phone_format"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def edit_phone(self, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["edit_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def enter_block_days(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["enter_day_or_days_for_block"],
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                [[REPLY_ADMIN_BUTTONS["back_to_menu"]]], resize_keyboard=True
            ),
        )

    async def block_day_or_time(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["block_day_or_time_question"],
            reply_markup=self.admin_keyboards["block_day"],
        )

    async def invalid_date_format(self, update: Update):
        keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            ADMIN_MESSAGES["invalid_date_format_or_day"],
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    async def invalid_time_format(self, update: Update):
        keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            ADMIN_MESSAGES["invalid_time_format_or_digit"],
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    async def error_back_to_menu(
        self, update: Update, error_message: str = ADMIN_MESSAGES["error_try_again"]
    ):
        keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            error_message,
            reply_markup=reply_markup,
        )

    async def day_already_blocked(self, update: Update, date: str):
        keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            text=f"{EMOJI['star']} День {date} уже заблокирован",
            reply_markup=reply_markup,
        )

    async def day_is_sunday(self, update: Update, date: str):
        keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            text=f"{EMOJI['blue_heart']} {date} - это воскресенье. Забыла? У тебя выходной!",
            reply_markup=reply_markup,
        )

    async def view_appointments(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
    ):
        appointments_list = context.bot_data["db"][
            "appointments"
        ].get_client_appointments(client_id)
        context.user_data["appointments_list"] = appointments_list

        keyboard = []
        for appointment in context.user_data["appointments_list"]:
            id = appointment[0]
            procedure = appointment[1]
            date = appointment[2]
            start_time = appointment[3].strftime("%H:%M") if appointment[2] else ""
            formatted_date = format_date_for_client_interface(date)
            text = f"{procedure} - " f"{formatted_date} - " f"{start_time}"

            keyboard.append(
                [InlineKeyboardButton(text, callback_data=f"select_appointment_{id}")]
            )

        keyboard.append(
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_admin_menu"], callback_data="back_to_menu"
                )
            ]
        )

        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["select_appointment"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def time_slots(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        available_slots: List[Tuple[time, time]],
    ):
        """Показать доступные временные слоты списком, без клавиатуры."""
        display = f"{EMOJI['calendar']} {format_date_for_keyboard(context.user_data['date_selected'])}\n"
        prev_state = context.user_data.get("prev_state")
        if prev_state == "view_available_dates":
            display += f"{ADMIN_MESSAGES["available_slots"]}:"
        elif prev_state == "procedure_slots":
            procedure = context.user_data.get("procedure_selected")
            display += f"{ADMIN_MESSAGES["available_slots"]}\nдля процедуры\n<b>{procedure}</b>:"
        display += "\n\n"

        total_slots = len(available_slots)

        max_columns = 2

        if total_slots <= max_columns:
            columns = total_slots
            rows = 1
        else:
            columns = max_columns
            rows = (total_slots + columns - 1) // columns

        for row_index in range(rows):
            row = ""
            for col_index in range(columns):
                slot_index = row_index * columns + col_index
                if slot_index < total_slots:
                    start_time, end_time = available_slots[slot_index]
                    time_text = f"<b>{start_time.strftime("%H:%M")}-{end_time.strftime("%H:%M")}</b>"
                    row += "~"
                    row += time_text
                    row += "~ "
            display += row + "\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_admin_menu"],
                    callback_data="back_to_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_dates"], callback_data="back_to_dates"
                )
            ],
        ]

        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=display,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def appointments_for_date(
        self, context: ContextTypes.DEFAULT_TYPE, date: date
    ):
        appointments = context.bot_data["db"].get("appointments")
        appointment_list = appointments.get_appointments_by_date(date)
        if not appointment_list:
            final_message = ADMIN_MESSAGES["no_appointments"]
        else:
            date_str = datetime.strftime(date, "%d.%m.%Y")
            final_message = f"<b>{date_str}</b>\n"
            for appointment in appointment_list:
                text = "---------------\n"
                text += appointment[4].strftime("%H:%M")
                text += "\n"
                text += f"{appointment[1]}\n{appointment[2]}, {appointment[3]}\n"
                final_message += text
        keyboard = [
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_admin_menu"],
                    callback_data="back_to_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_dates"], callback_data="back_to_dates"
                )
            ],
        ]

        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=final_message,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def enter_name(self, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=f"{datetime.strftime(context.user_data['date_selected'], "%d.%m.%Y")}\n{context.user_data['time_selected']}\n\n{ADMIN_MESSAGES["enter_client_name"]}",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_time"])]],
                resize_keyboard=True,
            ),
        )

    async def back_to_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=f"{EMOJI['blue_heart']}{EMOJI['time']}{EMOJI['blue_heart']}",
            reply_markup=ReplyKeyboardRemove(),
        )

        await update.message.reply_text(
            text=f"{context.user_data['date_selected']}\n{ADMIN_MESSAGES["select_time"]}",
            reply_markup=context.user_data.get("time_keyboard"),
        )

    async def enter_phone(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["enter_client_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    