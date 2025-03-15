from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes
from consts.messages import (
    ADMIN_MESSAGES,
    INLINE_BUTTONS,
    REPLY_ADMIN_BUTTONS,
    USER_MESSAGES,
    EMOJI,
    REPLY_USER_BUTTONS,
)
from utils.formatter import format_date_for_client_interface


class AdminInterface:
    def __init__(self, admin_keyboards, general_keyboards):
        self.admin_keyboards = admin_keyboards
        self.general_keyboards = general_keyboards

    async def main_menu(self, update: Update):
        await update.message.reply_text(
            text=ADMIN_MESSAGES["hello_admin"],
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
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])]],
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

    async def dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["select_date"],
            reply_markup=context.user_data.get("date_keyboard"),
        )

    async def enter_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["enter_client_name"],
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
            text=f"{format_date_for_client_interface(context.user_data['date_selected'])}\n{ADMIN_MESSAGES["select_time"]}",
            reply_markup=context.user_data.get("time_keyboard"),
        )

    async def enter_phone(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["enter_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def invalid_phone_format(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["invalid_phone_format"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def edit_phone(self, update: Update):
        await update.message.reply_text(
            ADMIN_MESSAGES["edit_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def proceed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data["reschedule"]:
            await context.bot.send_message(
                chat_id=context.user_data["chat_id"],
                text=f"Продолжим? {EMOJI['sparkle']}",
                reply_markup=self.admin_keyboards["final"],
            )
        else:
            await context.bot.send_message(
                chat_id=context.user_data["chat_id"],
                text=ADMIN_MESSAGES["continue"],
                reply_markup=self.admin_keyboards["after_edit"],
            )

    async def booking_cancelled(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["booking_cancelled"],
            reply_markup=self.admin_keyboards["final"],
        )

    async def back_to_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["edit_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[REPLY_ADMIN_BUTTONS["back_to_name"]]], resize_keyboard=True
            ),
        )

    # async def appointments(
    #     self, update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
    # ):
    #     appointments_list = context.bot_data["db"][
    #         "appointments"
    #     ].get_client_appointments(client_id)
    #     context.user_data["appointments_list"] = appointments_list
    #     appointments_text = f"{EMOJI['user']} <b>Записи клиента:</b>\n————————————\n"
    #     for appointment in appointments_list:
    #         procedure = appointment[1]
    #         date = appointment[2]
    #         start_time = appointment[3].strftime("%H:%M") if appointment[2] else ""
    #         end_time = appointment[4].strftime("%H:%M") if appointment[3] else ""
    #         formatted_date = format_date_for_client_interface(date)
    #         text = (
    #             f"{EMOJI['sparkle']} <i>{procedure}</i>\n"
    #             f"{EMOJI['calendar']} <i>Дата:</i> {formatted_date}\n"
    #             f"{EMOJI['clock']} <i>Время:</i> {start_time} – {end_time}\n"
    #             "————————————\n"
    #         )
    #         appointments_text += text

    #     await context.bot.send_message(
    #         chat_id=context.user_data["chat_id"],
    #         text=appointments_text,
    #         parse_mode="HTML",
    #         reply_markup=self.admin_keyboards["appointments_list"],
    #     )

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
                    INLINE_BUTTONS["back_to_menu"], callback_data="back_to_menu"
                )
            ]
        )

        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=ADMIN_MESSAGES["select_appointment"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
