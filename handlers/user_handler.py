import re
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CallbackContext,
)
from logger import setup_logger
from config import ID_TO_SEND_NOTIFICATIONS
from keyboards.general_keyboards import *
from consts.messages import (
    CONFIRMATION_MESSAGE,
    EMOJI,
    INLINE_BUTTONS,
    REPLY_USER_BUTTONS,
    USER_MESSAGES,
)
from utils.utils import create_appointment_from_context
from states import *
from datetime import datetime
from interfaces.user_interface import *


class UserHandler:
    def __init__(self, interface, dyn_keyboards):
        self.interface = interface
        self.dyn_keyboards = dyn_keyboards

    def get_handlers(self):
        return {
            USER_MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.main_menu)
            ],
            USER_SELECT_PROCEDURE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_procedure)
            ],
            USER_ENTER_PHONE_FOR_ACCOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.enter_phone_for_account
                )
            ],
            USER_CLIENT_ACCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_account_menu)
            ],
            USER_APPOINTMENTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.appointments)
            ],
            USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE: [
                CallbackQueryHandler(self.select_appointment_for_cancel_or_reschedule),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.select_appointment_unexpected_input,
                ),
            ],
            USER_APPOINTMENT_EDIT_ACTIONS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.appointment_edit_actions
                )
            ],
            USER_AFTER_EDIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.after_edit),
            ],
            USER_SHOW_PERSONAL_DATA: [
                CallbackQueryHandler(self.personal_data),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.personal_data_unexpected_input
                ),
            ],
            USER_UPDATE_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.update_phone)
            ],
            USER_UPDATE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.update_name)
            ],
            USER_SELECT_MONTH: [
                CallbackQueryHandler(self.select_month),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.select_month_unexpected_input
                ),
            ],
            USER_SELECT_DATE: [
                CallbackQueryHandler(self.select_date),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.select_date_unexpected_input
                ),
            ],
            USER_SELECT_TIME: [
                CallbackQueryHandler(self.select_time),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.select_time_unexpected_input
                ),
            ],
            USER_ENTER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_name)
            ],
            USER_ENTER_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_phone)
            ],
            USER_CONFIRMATION: [
                CallbackQueryHandler(self.confirmation),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.confirmation_unexpected_input,
                ),
            ],
            USER_AFTER_CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.after_confirmation)
            ],
            USER_FINAL_HANDLER: [
                CallbackQueryHandler(self.final_handler),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.final_text_handler
                ),
            ],
        }

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для главного меню пользователя."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["select_procedure"]:
            await self.interface.procedures(update)
            return USER_SELECT_PROCEDURE

        elif text == REPLY_USER_BUTTONS["client_account"]:
            tg_id = update.message.from_user.id
            if context.bot_data["db"]["clients"].client_is_registered_by_tg_id(tg_id):
                await self.interface.user_account(update, context)
                return USER_CLIENT_ACCOUNT
            else:
                await update.message.reply_text(
                    text=USER_MESSAGES["enter_phone_for_account"],
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(text=REPLY_USER_BUTTONS["back_to_menu"])]]
                    ),
                )
                return USER_ENTER_PHONE_FOR_ACCOUNT

        if text == REPLY_USER_BUTTONS["contact_master"]:
            await self.interface.contact_master(update)
            return USER_FINAL_HANDLER

        if text == REPLY_USER_BUTTONS["visit_tg_channel"]:
            await self.interface.visit_tg_channel(update)
            return USER_FINAL_HANDLER

        else:
            await update.message.reply_text(
                USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["main_menu"],
            )
            return USER_MAIN_MENU

    async def select_procedure(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для выбора процедуры."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        elif text in self.dyn_keyboards.procedures_buttons():
            context.user_data["reschedule"] = False
            procedure_name = " ".join(text.split()[1:])
            context.user_data["procedure_selected"] = procedure_name

            await update.message.reply_text(
                text=text, reply_markup=ReplyKeyboardRemove()
            )

            await self.interface.months(update)
            return USER_SELECT_MONTH
        else:
            await update.message.reply_text(
                USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.general_keyboards["procedures"],
            )
            return USER_SELECT_PROCEDURE

    async def enter_phone_for_account(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для ввода телефона при поиске аккаунта."""
        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        else:
            phone = text
            if not re.match(r"^8\d{10}$", phone):
                await update.message.reply_text(USER_MESSAGES["invalid_phone_format"])
                return USER_ENTER_PHONE_FOR_ACCOUNT

            else:
                clients = context.bot_data["db"]["clients"]
                client_data = clients.get_client_by_telephone(phone)

                if client_data:
                    if len(client_data) > 1:
                        await update.message.reply_text(
                            USER_MESSAGES["multiple_clients_found"],
                            reply_markup=self.interface.user_keyboards["main_menu"],
                        )
                        return USER_MAIN_MENU
                    else:
                        context.user_data["client_data"] = client_data[0]
                        await self.interface.user_account(update, context)
                        return USER_CLIENT_ACCOUNT
                else:
                    await update.message.reply_text(
                        USER_MESSAGES["client_account_not_found"],
                        reply_markup=self.interface.user_keyboards["main_menu"],
                    )
                    return USER_MAIN_MENU

    async def user_account_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для меню личного кабинета."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["my_appointments"]:
            id = context.bot_data["db"]["clients"].get_client_id_by_tg_id(
                context.user_data["tg_id"]
            )
            context.user_data["id"] = id
            if context.bot_data["db"]["appointments"].client_has_appointments(id):
                await self.interface.appointments(update, context, id)
                return USER_APPOINTMENTS
            else:
                await update.message.reply_text(
                    text=USER_MESSAGES["no_appointments"],
                    reply_markup=self.interface.user_keyboards["main_menu"],
                )
                return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["my_profile"]:
            await self.interface.personal_data(update, context)
            return USER_SHOW_PERSONAL_DATA

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        else:
            await update.message.reply_text(
                text=USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["user_account"],
            )
            return USER_CLIENT_ACCOUNT

    async def personal_data(self, update: Update, context: CallbackContext):
        """Хэндлер для меню с персональными данными клиента."""
        query = update.callback_query
        await query.answer()
        await query.delete_message()
        chat_id = context.user_data["chat_id"]

        if query.data == "telephone":
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["update_phone"],
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(REPLY_USER_BUTTONS["back_to_profile"])]],
                    resize_keyboard=True,
                ),
            )
            return USER_UPDATE_PHONE

        if query.data == "client_name":
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["update_name"],
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(REPLY_USER_BUTTONS["back_to_profile"])]],
                    resize_keyboard=True,
                ),
            )
            return USER_UPDATE_NAME

        if query.data == "back_to_profile":
            text = USER_MESSAGES["back_to_profile"]
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.interface.user_keyboards["user_account"],
            )
            return USER_CLIENT_ACCOUNT

        if query.data == "back_to_menu":
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["on_return_to_menu"],
                reply_markup=self.interface.user_keyboards["main_menu"],
            )
            return USER_MAIN_MENU

    async def update_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT
        else:
            phone = text
            if not re.match(r"^8\d{10}$", phone):
                await update.message.reply_text(
                    text=USER_MESSAGES["invalid_phone_format"],
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(REPLY_USER_BUTTONS["back_to_profile"])]],
                        resize_keyboard=True,
                    ),
                )
                return USER_UPDATE_PHONE
            else:
                context.user_data["phone"] = phone
                clients = context.bot_data["db"]["clients"]
                tg_id = context.user_data["tg_id"]

                clients.update_client_phone_by_tg_id(tg_id, phone)

                await context.bot.send_message(
                    chat_id=context.user_data["chat_id"],
                    text=f"{USER_MESSAGES["phone_updated"]}: {phone}.",
                    reply_markup=self.interface.user_keyboards["after_edit"],
                )
                return USER_AFTER_EDIT

    async def update_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT
        else:
            name = text
            context.user_data["name"] = name
            clients = context.bot_data["db"]["clients"]
            tg_id = context.user_data["tg_id"]
            clients.update_client_name_by_tg_id(tg_id, name)
            await update.message.reply_text(
                text=f"{USER_MESSAGES["name_updated"]}: {name}.",
                reply_markup=self.interface.user_keyboards["after_edit"],
            )
            return USER_AFTER_EDIT

    async def personal_data_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text
        if text == REPLY_USER_BUTTONS["my_appointments"]:
            id = context.bot_data["db"]["clients"].get_client_id_by_tg_id(
                context.user_data["tg_id"]
            )
            context.user_data["id"] = id
            if context.bot_data["db"]["appointments"].client_has_appointments(id):
                await self.interface.appointments(update, context, id)
                return USER_APPOINTMENTS
            else:
                await update.message.reply_text(
                    text=USER_MESSAGES["no_appointments"],
                    reply_markup=self.interface.user_keyboards["main_menu"],
                )
                return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["my_profile"]:
            await self.interface.personal_data(update, context)
            return USER_SHOW_PERSONAL_DATA

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        else:
            await update.message.reply_text(text=USER_MESSAGES["error_try_again"])
            await self.interface.personal_data(update, context)
            return USER_SHOW_PERSONAL_DATA

    async def appointments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для меню с отменой и переносом записей."""
        text = update.message.text

        if text == REPLY_USER_BUTTONS["reschedule_or_cancel"]:
            await self.interface.edit_appointments(
                update, context, context.user_data["id"]
            )
            return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        else:
            await update.message.reply_text(
                USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["appointments"],
            )
            return USER_APPOINTMENTS

    async def select_appointment_for_cancel_or_reschedule(
        self, update: Update, context: CallbackContext
    ):
        """Хэндлер для выбора записи для переноса или отмены."""
        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]
        await query.delete_message()

        if query.data.startswith("select_appointment"):
            appointment_id = query.data.split("_")[2]
            context.user_data["appointment_id"] = appointment_id

            context.user_data["appointment_for_editing"] = [
                appointment
                for appointment in context.user_data["appointments_list"]
                if appointment[0] == int(context.user_data["appointment_id"])
            ][0]

            context.user_data["procedure_selected"] = context.user_data[
                "appointment_for_editing"
            ][1]

            procedure = context.user_data["procedure_selected"]
            date = format_date_for_client_interface(
                context.user_data["appointment_for_editing"][2]
            )
            time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"<b>Вы выбрали</b>: {procedure} - {date} - {time}.\n<b>{USER_MESSAGES["cancel_or_reschedule"]}</b>",
                parse_mode="HTML",
                reply_markup=self.interface.user_keyboards["cancel_reschedule"],
            )
            return USER_APPOINTMENT_EDIT_ACTIONS

        elif query.data == "back_to_profile":
            text = USER_MESSAGES["back_to_profile"]
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.interface.user_keyboards["user_account"],
            )
            return USER_CLIENT_ACCOUNT

        elif query.data == "back_to_menu":
            await self.interface.edit_appointments(
                update, context, context.user_data["id"]
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["on_return_to_menu"],
                reply_markup=self.interface.user_keyboards["main_menu"],
            )
            return USER_MAIN_MENU

    async def select_appointment_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text

        if text == REPLY_USER_BUTTONS["reschedule_or_cancel"]:
            await self.interface.edit_appointments(
                update, context, context.user_data["id"]
            )
            return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=USER_MESSAGES["error_try_again"]
            )

            await self.interface.edit_appointments(
                update, context, context.user_data["id"]
            )
            return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE

    async def appointment_edit_actions(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text

        procedure = context.user_data["procedure_selected"]
        date = format_date_for_client_interface(
            context.user_data["appointment_for_editing"][2]
        )
        time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

        if text == REPLY_USER_BUTTONS["reschedule_appointment"]:
            context.user_data["reschedule"] = True
            await update.message.reply_text(
                text=f"{procedure} - {date} - {time}",
                reply_markup=ReplyKeyboardRemove(),
            )

            await self.interface.months(update)
            return USER_SELECT_MONTH

        if text == REPLY_USER_BUTTONS["cancel_appointment"]:
            context.user_data["reschedule"] = False

            appointment_id = int(context.user_data["appointment_id"])
            appointments = context.bot_data["db"]["appointments"]

            appointment_data = appointments.get_client_data_by_appointment_id(
                appointment_id
            )
            try:
                appointments.delete_appointment(appointment_id)
                db_success = True
            except Exception as e:
                db_success = False
                appointments.logger.error(
                    f"Ошибка при обновлении информации в базе данных: {e}"
                )
            notification_message = (
                f"Клиент {appointment_data[3]} отменил запись на процедуру "
                f'"{appointment_data[0]}"\n'
                f"Дата: {appointment_data[1]}\n"
                f"Время: {appointment_data[2].strftime("%H:%M")}\n"
                f"Телефон: {appointment_data[4]}\n"
            )

            if db_success:
                notification_message += (
                    f"\n{EMOJI['success']} Информация в базе данных обновлена."
                )
            else:
                notification_message += (
                    f"\n{EMOJI['sign'] * 3} Информация а базе данных не обновлена. "
                    "Обратитесь к разработчику или попробуйте удалить запись "
                    "самостоятельно через админ-интерфейс бота."
                )

            await context.bot.send_message(
                chat_id=ID_TO_SEND_NOTIFICATIONS, text=notification_message
            )
            await update.message.reply_text(
                text=USER_MESSAGES["appointment_cancelled"],
                reply_markup=self.interface.user_keyboards["after_edit"],
            )
            return USER_AFTER_EDIT

        if text == REPLY_USER_BUTTONS["to_menu"]:
            context.user_data["reschedule"] = False
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["to_profile"]:
            context.user_data["reschedule"] = False
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["to_my_appointments"]:
            context.user_data["reschedule"] = False
            await self.interface.edit_appointments(
                update, context, context.user_data["id"]
            )
            return USER_SELECT_APPOINTMENT_FOR_CANCEL_OR_RESCHEDULE

        else:
            context.user_data["reschedule"] = False
            await update.message.reply_text(
                text=f"{USER_MESSAGES["error_try_again"]}\n{USER_MESSAGES["cancel_or_reschedule"]}",
                reply_markup=self.interface.user_keyboards["cancel_reschedule"],
            )
        return USER_APPOINTMENT_EDIT_ACTIONS

    async def after_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["visit_tg_channel"]:
            await self.interface.visit_tg_channel_with_profile(update)
            return USER_FINAL_HANDLER

        else:
            await update.message.reply_text(
                text=USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["after_edit"],
            )
            return USER_AFTER_EDIT

    async def select_month(self, update: Update, context: CallbackContext):
        """Хэндлер для выбора месяца."""

        query = update.callback_query
        await query.answer()
        await query.delete_message()
        chat_id = context.user_data["chat_id"]

        if query.data == "back":
            if not context.user_data["reschedule"]:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["select_procedure"],
                    reply_markup=self.interface.general_keyboards["procedures"],
                )
                return USER_SELECT_PROCEDURE
            else:
                procedure = context.user_data["procedure_selected"]
                date = format_date_for_client_interface(
                    context.user_data["appointment_for_editing"][2]
                )
                time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"<b>Вы выбрали</b>: {procedure} - {date} - {time}.\n<b>{USER_MESSAGES["cancel_or_reschedule"]}</b>",
                    parse_mode="HTML",
                    reply_markup=self.interface.user_keyboards["cancel_reschedule"],
                )
            return USER_APPOINTMENT_EDIT_ACTIONS

        elif query.data.startswith("month_"):
            month_str = query.data.replace("month_", "")
            month, year = map(int, month_str.split("_"))
            context.user_data["month_selected"] = (year, month)

            available_dates = context.bot_data["db"]["schedule"].get_available_dates(
                procedure=context.user_data.get("procedure_selected"),
                target_month=context.user_data.get("month_selected"),
            )

            if available_dates:
                keyboard = self.dyn_keyboards.date(year, month, available_dates)
                context.user_data["date_keyboard"] = keyboard
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["select_date"],
                    reply_markup=keyboard,
                )
                return USER_SELECT_DATE

            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["no_dates_available"],
                    reply_markup=self.interface.general_keyboards["months"],
                )
                return USER_SELECT_MONTH

        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["error_try_again"]
                + "\n"
                + USER_MESSAGES["select_month"],
                reply_markup=self.interface.general_keyboards["months"],
            )
            return USER_SELECT_MONTH

    async def select_month_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для обработки непредвиденного ввода при выборе месяца."""

        await update.message.reply_text(
            text=USER_MESSAGES["error_try_again"]
            + "\n"
            + USER_MESSAGES["select_month"],
            reply_markup=self.interface.general_keyboards["months"],
        )
        return USER_SELECT_MONTH

    async def select_date(self, update: Update, context: CallbackContext):
        """Хэндлер для выбора даты."""

        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]

        if query.data == "back_to_months":
            await query.delete_message()
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["select_month"],
                reply_markup=self.interface.general_keyboards["months"],
            )
            return USER_SELECT_MONTH

        elif query.data.startswith("prev_month_") or query.data.startswith(
            "next_month_"
        ):
            _, _, year, month = query.data.split("_")
            year, month = int(year), int(month)

            schedule = context.bot_data["db"].get("schedule")

            available_dates = schedule.get_available_dates(
                procedure=context.user_data.get("procedure_selected"),
                target_month=(year, month),
            )

            context.user_data["month_selected"] = (year, month)

            keyboard = self.dyn_keyboards.date(year, month, available_dates)
            context.user_data["date_keyboard"] = keyboard

            await query.edit_message_reply_markup(reply_markup=keyboard)
            return USER_SELECT_DATE

        elif query.data.startswith("date_"):
            await query.delete_message()
            date_str = query.data.replace("date_", "")
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            context.user_data["date_selected"] = selected_date
            context.user_data["month_selected"] = (
                selected_date.year,
                selected_date.month,
            )

            schedule = context.bot_data["db"].get("schedule")
            available_slots = schedule.get_available_time_slots(
                selected_date, context.user_data.get("procedure_selected")
            )

            if not available_slots:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["no_slots_available"],
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    INLINE_BUTTONS["back"],
                                    callback_data="back_to_dates",
                                )
                            ]
                        ]
                    ),
                )
                return USER_SELECT_DATE

            keyboard = self.dyn_keyboards.time(available_slots, context)
            context.user_data["time_keyboard"] = keyboard
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{format_date_for_client_interface(selected_date)}\n\n{USER_MESSAGES["select_time"]}",
                reply_markup=keyboard,
            )
            return USER_SELECT_TIME

    async def select_date_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для обработки непредвиденного ввода при выборе даты."""

        await update.message.reply_text(
            text=USER_MESSAGES["error_try_again"] + "\n" + USER_MESSAGES["select_date"],
            reply_markup=context.user_data.get("date_keyboard"),
        )
        return USER_SELECT_DATE

    async def select_time(self, update: Update, context: CallbackContext):
        """Хэндлер для выбора времени."""

        query = update.callback_query
        await query.answer()
        await query.delete_message()
        chat_id = context.user_data["chat_id"]

        if query.data == "back_to_dates":
            selected_date = context.user_data.get("date_selected")
            if not selected_date:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["error_try_again"],
                    reply_markup=self.interface.general_keyboards["procedures"],
                )
                return USER_SELECT_PROCEDURE

            await self.interface.dates(update, context)
            return USER_SELECT_DATE

        elif query.data.startswith("time_"):

            time_str = query.data.replace("time_", "")

            try:
                selected_time = datetime.strptime(time_str, "%H:%M:%S").time()
            except ValueError:
                selected_time = datetime.strptime(time_str, "%H:%M").time()

            context.user_data["time_selected"] = selected_time

            await self.interface.enter_name(update, context)
            return USER_ENTER_NAME

    async def select_time_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для обработки непредвиденного ввода при выборе времени."""

        await update.message.reply_text(
            text=USER_MESSAGES["error_try_again"] + "\n" + USER_MESSAGES["select_time"],
            reply_markup=context.user_data.get("time_keyboard"),
        )
        return USER_SELECT_TIME

    async def enter_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для ввода имени."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_time"]:
            await self.interface.back_to_time(update, context)
            return USER_SELECT_TIME

        else:
            name = text
            if len(name) < 2:
                await update.message.reply_text(
                    USER_MESSAGES["name_too_short"],
                )
                return USER_ENTER_NAME
            elif len(name) > 50:
                await update.message.reply_text(
                    USER_MESSAGES["name_too_long"],
                )
                return USER_ENTER_NAME

            context.user_data["name"] = name

            await self.interface.enter_phone(update)
            return USER_ENTER_PHONE

    async def enter_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для ввода телефона."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_name"]:
            await self.interface.enter_name(update, context)
            return USER_ENTER_NAME
        else:
            phone = text
            if not re.match(r"^8\d{10}$", phone):
                await self.interface.invalid_phone_format(update)
                return USER_ENTER_PHONE

            context.user_data["phone"] = phone

            confirmation_message = CONFIRMATION_MESSAGE["booking_details"].format(
                procedure=context.user_data["procedure_selected"],
                date=context.user_data["date_selected"],
                time=context.user_data["time_selected"].strftime("%H:%M"),
                name=context.user_data["name"],
                phone=context.user_data["phone"],
                sparkle=EMOJI["sparkle"],
                calendar=EMOJI["calendar"],
                clock=EMOJI["clock"],
                emoji_name=EMOJI["name"],
                emoji_phone=EMOJI["phone"],
            )

            keyboard = self.interface.general_keyboards["confirmation"]
            context.user_data["confirmation_message"] = confirmation_message

            await update.message.reply_text(
                f"{USER_MESSAGES['confirm_booking']} \n {confirmation_message}",
                reply_markup=keyboard,
            )

            return USER_CONFIRMATION

    async def confirmation(self, update: Update, context: CallbackContext):
        """Хэндлер для подтверждения или отмены записи."""

        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]
        await query.delete_message()

        if query.data == "confirm":
            await context.bot.send_message(
                chat_id=chat_id, text=USER_MESSAGES["booking_success"]
            )
            await self.interface.proceed(update, context)
            if context.user_data["reschedule"]:
                appointments = context.bot_data["db"].get("appointments")
                appointment_id = context.user_data.get("appointment_id")
                appointments.delete_appointment(appointment_id)
                notification_message = (
                    f'Клиент {context.user_data["name"]} перенес запись на процедуру '
                    f'"{context.user_data["procedure_selected"]}".\n'
                    f'Прежняя дата: {context.user_data["appointment_for_editing"][2]} \n'
                    f'Прежнее время: {context.user_data["appointment_for_editing"][3].strftime("%H:%M")} \n'
                    f'Новая дата: {context.user_data["date_selected"]} \n'
                    f'Новое время: {context.user_data["time_selected"].strftime("%H:%M")} \n'
                    f'Телефон: {context.user_data["phone"]}\n'
                )
            else:
                notification_message = (
                    f'Клиент {context.user_data["name"]} записался на процедуру '
                    f'"{context.user_data["procedure_selected"]}".\n'
                    f'Дата: {context.user_data["date_selected"]}, '
                    f'время: {context.user_data["time_selected"].strftime("%H:%M")}.\n'
                    f'Телефон: {context.user_data["phone"]}\n'
                )
            try:
                await create_appointment_from_context(update, context)
                db_success = True
            except Exception as e:
                db_success = False
                appointments.logger.error(f"Ошибка при записи в базу данных: {e}")

            if db_success:
                notification_message += (
                    f"\n{EMOJI['success']} Запись добавлена в базу данных."
                )
            else:
                notification_message += (
                    f"\n{EMOJI['sign'] * 3} Информация не добавлена в базу данных. "
                    "Обратитесь к разработчику или попробуйте добавить запись "
                    "самостоятельно через админ-интерфейс бота."
                )

            await context.bot.send_message(
                chat_id=ID_TO_SEND_NOTIFICATIONS,
                text=notification_message,
            )
            if not context.user_data["reschedule"]:
                return USER_AFTER_CONFIRMATION
            else:
                context.user_data["reschedule"] = False
                return USER_AFTER_EDIT

        elif query.data == "cancel":
            if not context.user_data["reschedule"]:
                await self.interface.booking_cancelled(update, context)
                return USER_AFTER_CONFIRMATION
            else:
                context.user_data["reschedule"] = False
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=USER_MESSAGES["reschedule_interrupted"],
                    reply_markup=self.interface.user_keyboards["after_edit"],
                )
                return USER_AFTER_EDIT

        elif query.data == "back_to_edit":
            await self.interface.back_to_edit(update, context)
            return USER_ENTER_PHONE

    async def confirmation_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для обработки непредвиденного ввода при подтверждении или отмене записи."""

        text = update.message.text
        if text == REPLY_USER_BUTTONS["back_to_phone"]:
            await self.interface.edit_phone(update)
            return USER_ENTER_PHONE

        if text == REPLY_USER_BUTTONS["back_to_name"]:
            await self.interface.enter_name(update, context)
            return USER_ENTER_NAME

        else:
            await context.bot.send_message(
                chat_id=update.message.chat.id, text=USER_MESSAGES["error_try_again"]
            )

            await context.bot.send_message(
                chat_id=context.user_data["chat_id"],
                text=f"{USER_MESSAGES['confirm_booking']} \n {context.user_data['confirmation_message']}",
                reply_markup=self.interface.general_keyboards["confirmation"],
            )
        return USER_CONFIRMATION

    async def after_confirmation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для возврата в главное меню или перехода в тг-канал."""

        text = update.message.text

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["back_to_profile"]:
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["visit_tg_channel"]:
            await self.interface.visit_tg_channel(update)
            return USER_FINAL_HANDLER

        else:
            await update.message.reply_text(
                USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["final"],
            )
            return USER_FINAL_HANDLER

    async def final_handler(self, update: Update, context: CallbackContext):
        """Хэндлер для возврата в главное меню или перехода в тг-канал."""

        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]
        await query.delete_message()

        if query.data == "back_to_menu":
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["on_return_to_menu"],
                reply_markup=self.interface.user_keyboards["main_menu"],
            )
            return USER_MAIN_MENU

        if query.data == "back_to_profile":
            text = USER_MESSAGES["back_to_profile"]
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.interface.user_keyboards["user_account"],
            )
            return USER_CLIENT_ACCOUNT

        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["main_menu"],
            )
            return USER_MAIN_MENU

    async def final_text_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):

        text = update.message.text
        if text == REPLY_USER_BUTTONS["select_procedure"]:
            await self.interface.procedures(update)
            return USER_SELECT_PROCEDURE

        if (
            text == REPLY_USER_BUTTONS["back_to_profile"]
            or text == REPLY_USER_BUTTONS["client_account"]
        ):
            await self.interface.back_to_user_account(update)
            return USER_CLIENT_ACCOUNT

        if text == REPLY_USER_BUTTONS["back_to_menu"]:
            await self.interface.on_return_to_menu(update)
            return USER_MAIN_MENU

        if text == REPLY_USER_BUTTONS["visit_tg_channel"]:
            await self.interface.visit_tg_channel(update)
            return USER_FINAL_HANDLER

        if text == REPLY_USER_BUTTONS["contact_master"]:
            await self.interface.contact_master(update)
            return USER_FINAL_HANDLER

        else:
            await update.message.reply_text(
                USER_MESSAGES["error_try_again"],
                reply_markup=self.interface.user_keyboards["final"],
            )
            return USER_FINAL_HANDLER
