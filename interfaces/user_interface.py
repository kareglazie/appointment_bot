from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes
from consts.messages import INLINE_BUTTONS, USER_MESSAGES, EMOJI, REPLY_USER_BUTTONS
from utils.formatter import format_date_for_client_interface


class UserInterface:
    def __init__(self, user_keyboards, general_keyboards):
        self.user_keyboards = user_keyboards
        self.general_keyboards = general_keyboards

    async def months(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["select_month"], reply_markup=self.general_keyboards["months"]
        )

    async def procedures(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["select_procedure"],
            reply_markup=self.general_keyboards["procedures"],
        )

    async def dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text=USER_MESSAGES["select_date"],
            reply_markup=context.user_data.get("date_keyboard"),
        )

    async def contact_master(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["go_to_chat"],
            reply_markup=self.user_keyboards["contact_master"],
        )

    async def visit_tg_channel(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["go_to_tg_channel"],
            reply_markup=self.user_keyboards["go_to_tg_channel"],
        )

    async def visit_tg_channel_with_profile(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["go_to_tg_channel"],
            reply_markup=self.user_keyboards["go_to_tg_channel_with_profile"],
        )

    async def on_return_to_menu(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["on_return_to_menu"],
            reply_markup=self.user_keyboards["main_menu"],
        )

    async def enter_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=USER_MESSAGES["enter_name"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["back_to_time"])]],
                resize_keyboard=True,
            ),
        )

    async def back_to_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=USER_MESSAGES["back_to_time"],
            reply_markup=ReplyKeyboardRemove(),
        )

        await update.message.reply_text(
            USER_MESSAGES["select_time"],
            reply_markup=context.user_data.get("time_keyboard"),
        )

    async def enter_phone(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["enter_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def invalid_phone_format(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["invalid_phone_format"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def edit_phone(self, update: Update):
        await update.message.reply_text(
            USER_MESSAGES["edit_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(REPLY_USER_BUTTONS["back_to_name"])]],
                resize_keyboard=True,
            ),
        )

    async def proceed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data["reschedule"]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Продолжим? {EMOJI['sparkle']}",
                reply_markup=self.user_keyboards["final"],
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=USER_MESSAGES["continue"],
                reply_markup=self.user_keyboards["after_edit"],
            )

    async def booking_cancelled(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=USER_MESSAGES["booking_cancelled"],
            reply_markup=self.user_keyboards["final"],
        )

    async def back_to_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=USER_MESSAGES["edit_phone"],
            reply_markup=ReplyKeyboardMarkup(
                [[REPLY_USER_BUTTONS["back_to_name"]]], resize_keyboard=True
            ),
        )

    async def user_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_username = context.user_data.get("tg_username")
        hello_text = f"{EMOJI['sparkle']} Здравствуйте, {tg_username}!\n\n{USER_MESSAGES["hello_account"]}"
        await update.message.reply_text(
            text=hello_text, reply_markup=self.user_keyboards["user_account"]
        )

    async def back_to_user_account(self, update: Update):
        await update.message.reply_text(
            text=USER_MESSAGES["back_to_profile"],
            reply_markup=self.user_keyboards["user_account"],
        )

    async def appointments(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
    ):
        appointments_list = context.bot_data["db"][
            "appointments"
        ].get_client_appointments(client_id)
        context.user_data["appointments_list"] = appointments_list
        appointments_text = f"{EMOJI['user']} <b>Ваши записи:</b>\n————————————\n"
        for appointment in appointments_list:
            procedure = appointment[1]
            date = appointment[2]
            start_time = appointment[3].strftime("%H:%M") if appointment[2] else ""
            end_time = appointment[4].strftime("%H:%M") if appointment[3] else ""
            formatted_date = format_date_for_client_interface(date)
            text = (
                f"{EMOJI['sparkle']} <i>{procedure}</i>\n"
                f"{EMOJI['calendar']} <i>Дата:</i> {formatted_date}\n"
                f"{EMOJI['clock']} <i>Время:</i> {start_time} – {end_time}\n"
                "————————————\n"
            )
            appointments_text += text

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=appointments_text,
            parse_mode="HTML",
            reply_markup=self.user_keyboards["appointments"],
        )

    async def edit_appointments(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int
    ):

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
                    INLINE_BUTTONS["back_to_profile"], callback_data="back_to_profile"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    INLINE_BUTTONS["back_to_menu"], callback_data="back_to_menu"
                )
            ]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=USER_MESSAGES["select_appointment"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def personal_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        tg_id = context.user_data["tg_id"]
        clients = context.bot_data["db"].get("clients")
        name = clients.get_client_name_by_tg_id(tg_id)
        phone = clients.get_client_phone_by_tg_id(tg_id)

        await update.message.reply_text(
            text=f"<b> Ваши данные </b> \n {EMOJI['phone']} Телефон: {phone}\n {EMOJI['user']} Имя: {name}. \n Хотите что-то изменить?",
            parse_mode="HTML",
            reply_markup=self.user_keyboards["personal_data"],
        )
