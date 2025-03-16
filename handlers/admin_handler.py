from datetime import datetime
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
    CallbackContext,
    filters,
    CallbackQueryHandler,
)

from consts.constants import DATE_RANGE_PATTERN, SINGLE_DATE_PATTERN, TIME_PATTERN
from consts.messages import ADMIN_MESSAGES
from keyboards.admin_keyboards import *
from keyboards.general_keyboards import *
from states import *
from utils.formatter import (
    format_date_for_client_interface,
    format_date_for_keyboard,
    format_date_for_db,
    format_date_for_db_admin,
)
from utils.utils import create_appointment_from_context


class AdminHandler:
    def __init__(self, interface, dyn_keyboards):
        self.interface = interface
        self.dyn_keyboards = dyn_keyboards
        self.user_data = {}

    def get_handlers(self):
        return {
            ADMIN_MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.main_menu)
            ],
            ADMIN_DATES_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.dates_menu)
            ],
            ADMIN_CLIENTS_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.clients_menu)
            ],
            ADMIN_APPOINTMENTS_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.appointments_menu)
            ],
            ADMIN_CLIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.client)
            ],
            SELECT_CLIENT_FROM_MULTIPLE: [
                CallbackQueryHandler(self.select_client),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.select_client_unexpected_input
                ),
            ],
            ADMIN_VIEW_DATES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.view_dates)
            ],
            ADMIN_SELECT_PROCEDURE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_procedure)
            ],
            ADMIN_SELECT_MONTH: [
                CallbackQueryHandler(self.select_month),
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.view_dates),
            ],
            ADMIN_SELECT_DATE: [
                CallbackQueryHandler(self.select_date),
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.view_dates),
            ],
            ADMIN_SELECT_TIME: [
                CallbackQueryHandler(self.select_time),
            ],
            ADMIN_CONFIRMATION: [
                CallbackQueryHandler(self.confirmation),
            ],
            ADMIN_AFTER_TIME_VIEW: [
                CallbackQueryHandler(self.after_time_view),
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.view_dates),
            ],
            ADMIN_VIEW_APPOINTMENTS: [
                CallbackQueryHandler(self.view_client_appointments),
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.client),
            ],
            ADMIN_APPOINTMENT_EDIT_ACTIONS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.appointment_edit_actions
                )
            ],
            ADMIN_DELETE_CLIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.delete_client)
            ],
            ADMIN_BLOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.block)],
            ADMIN_BLOCK_DAY_OR_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.block_day_or_time)
            ],
            ADMIN_BLOCK_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.block_time)
            ],
        }

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["dates"]:
            await self.interface.dates_menu(update)
            return ADMIN_DATES_MENU
        if text == REPLY_ADMIN_BUTTONS["clients"]:
            await self.interface.clients_menu(update)
            return ADMIN_CLIENTS_MENU
        if text == REPLY_ADMIN_BUTTONS["appointments"]:
            await self.interface.appointments_menu(update)
            return ADMIN_APPOINTMENTS_MENU
        else:
            await update.message.reply_text(
                ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.interface.admin_keyboards["main_menu"],
            )
            return ADMIN_MAIN_MENU

    async def dates_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["view_available_dates"]:
            await self.interface.view_dates(update)
            return ADMIN_VIEW_DATES
        if text == REPLY_ADMIN_BUTTONS["block_day_or_time"]:
            await self.interface.enter_block_days(update)
            return ADMIN_BLOCK
        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        else:
            await update.message.reply_text(
                ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.interface.admin_keyboards["dates_menu"],
            )
            return ADMIN_DATES_MENU

    @staticmethod
    def is_date_valid(input_date: date) -> tuple[bool, str]:
        """
        Проверяет, находится ли дата в допустимом диапазоне.
        Возвращает кортеж (bool, str):
        - True, если дата допустима.
        - False и сообщение об ошибке, если дата недопустима.
        """
        today = date.today()
        six_months_later = today + timedelta(days=180)

        if input_date < today:
            return False, ADMIN_MESSAGES["day_too_far_past"]
        elif input_date > six_months_later:
            return False, ADMIN_MESSAGES["day_too_far_future"]
        else:
            return True, ""

    @staticmethod
    def is_date_correct(input_date: date) -> bool:
        """
        Проверяет, является ли дата корректной:
        - Проверяет количество дней в месяце.
        - Проверяет високосные годы для 29 февраля.
        Возвращает True, если дата корректна, иначе False.
        """
        try:
            input_date.replace(day=input_date.day)
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_date(date_str: str) -> date:
        """
        Преобразует строку в объект date.
        Поддерживает форматы: ДД.ММ.ГГГГ и ДД/ММ/ГГГГ.
        """
        date = date_str.replace(" ", "")
        date = date_str.replace("/", ".")

        return datetime.strptime(date, "%d.%m.%Y").date()

    @staticmethod
    def parse_time(time_str: str) -> time:
        """
        Преобразует строку в объект time.
        Формат: HH:MM.
        """
        time = time_str.replace(" ", "")
        start_time, end_time = time.split("-")
        try:
            return (
                datetime.strptime(start_time, "%H:%M").time(),
                datetime.strptime(end_time, "%H:%M").time(),
            )
        except ValueError:
            raise ValueError("Неверный формат времени. Используйте HH:MM.")

    async def block(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для обработки ввода даты или дат для блокировки."""
        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        if DATE_RANGE_PATTERN.match(text):
            text = text.replace(" ", "")
            text = text.replace("/", ".")
            start_date_str, end_date_str = text.split("-")
            logger = context.bot_data["db"]["blocked_slots"].logger

            try:
                print(text)
                start_date = self.parse_date(start_date_str)
                end_date = self.parse_date(end_date_str)
            except ValueError:
                print("error")
                await self.interface.invalid_date_format(update)
                return ADMIN_BLOCK

            if not self.is_date_correct(start_date):
                await self.interface.error_back_to_menu(
                    update, f"Некорректная дата: {start_date_str}"
                )
                return ADMIN_BLOCK

            if start_date > end_date:
                await self.interface.error_back_to_menu(
                    update, ADMIN_MESSAGES["invalid_date_range"]
                )
                return ADMIN_BLOCK

            start_is_valid, start_error_message = self.is_date_valid(start_date)
            end_is_valid, end_error_message = self.is_date_valid(end_date)

            if not start_is_valid or not end_is_valid:
                error_message = (
                    start_error_message if not start_is_valid else end_error_message
                )
                if error_message == ADMIN_MESSAGES["day_too_far_past"]:
                    error_message = ADMIN_MESSAGES["days_too_far_past"]
                else:
                    error_message = ADMIN_MESSAGES["days_too_far_future"]
                await self.interface.error_back_to_menu(update, error_message)
                return ADMIN_BLOCK

            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() == 6:
                    logger.debug(
                        f"Пропуск воскресенья: {current_date.strftime('%d.%m.%Y')}"
                    )
                    current_date += timedelta(days=1)
                    continue

                if context.bot_data["db"]["blocked_slots"].is_day_blocked(current_date):
                    logger.debug(
                        f"День {current_date.strftime('%d.%m.%Y')} уже заблокирован."
                    )
                    current_date += timedelta(days=1)
                    continue

                success = context.bot_data["db"]["blocked_slots"].block_day(
                    current_date
                )
                if not success:
                    await self.interface.error_back_to_menu(
                        update,
                        f"Ошибка при блокировке дня {current_date.strftime('%d.%m.%Y')}.",
                    )
                    return ADMIN_BLOCK

                logger.debug(f"День {current_date.strftime('%d.%m.%Y')} заблокирован.")
                current_date += timedelta(days=1)

            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES['days_blocked']}\n{start_date_str}-{end_date_str}"
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        elif SINGLE_DATE_PATTERN.match(text):
            try:
                date = self.parse_date(text)
            except ValueError:
                await self.interface.invalid_date_format(update)
                return ADMIN_BLOCK

            if not self.is_date_correct(date):
                await self.interface.error_back_to_menu(
                    update, f"Некорректная дата: {text}"
                )
                return ADMIN_BLOCK

            is_valid, error_message = self.is_date_valid(date)
            if not is_valid:
                await self.interface.error_back_to_menu(update, error_message)
                return ADMIN_BLOCK

            if date.weekday() == 6:
                await self.interface.day_is_sunday(update, date=text)
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU

            is_day_blocked = context.bot_data["db"]["blocked_slots"].is_day_blocked(
                date
            )
            if is_day_blocked:
                await self.interface.day_already_blocked(update, text)
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU

            context.user_data["single_date"] = text
            context.user_data["date_obj"] = date

            await self.interface.block_day_or_time(update)
            return ADMIN_BLOCK_DAY_OR_TIME

        else:
            await self.interface.invalid_date_format(update)
            return ADMIN_BLOCK

    async def block_day_or_time(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text
        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        if text == REPLY_ADMIN_BUTTONS["block_whole_day"]:
            date = context.user_data["date_obj"]
            blocked_slots = context.bot_data["db"]["blocked_slots"]
            if blocked_slots.block_day(date):
                await update.message.reply_text(
                    text=f"День {context.user_data['single_date']} заблокирован."
                )
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU
            else:
                await update.message.reply_text(text=ADMIN_MESSAGES["db_error"])
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU

        if text == REPLY_ADMIN_BUTTONS["select_time"]:
            date = context.user_data["date_obj"]
            available_slots = context.bot_data["db"][
                "schedule"
            ].get_available_time_slots(date)

            if not available_slots:
                await update.message.reply_text(text=ADMIN_MESSAGES["all_day_occupied"])
                await self.interface.block_day_or_time(update)
                return ADMIN_BLOCK

            message = f"<b>{context.user_data['single_date']}\n{ADMIN_MESSAGES["available_slots"]}</b>\n"
            slots_list = []
            for start_time, end_time in available_slots:
                slot_text = (
                    f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
                )
                slots_list.append(slot_text)

            message += "\n".join(slots_list)

            keyboard = [[REPLY_ADMIN_BUTTONS["back_to_menu"]]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                text=f"{message}\n\n{ADMIN_MESSAGES['enter_time_for_block']}",
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return ADMIN_BLOCK_TIME

        else:
            await update.message.reply_text(ADMIN_MESSAGES["error_try_again"])
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

    async def block_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хендлер для блокировки временного слота."""

        text = update.message.text
        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        if TIME_PATTERN.match(text):
            try:
                start_time, end_time = self.parse_time(text)

                if not (0 <= start_time.hour <= 23 and 0 <= start_time.minute <= 59):
                    await self.interface.invalid_time_format(update)
                    return ADMIN_BLOCK_TIME

                if start_time >= end_time:
                    await update.message.reply_text(
                        text=f"{ADMIN_MESSAGES['invalid_time_range']}\n\n{ADMIN_MESSAGES['enter_time_for_block']}",
                        parse_mode="HTML",
                    )
                    return ADMIN_BLOCK_TIME

                context.user_data["time_to_display"] = text.replace(" ", "")
                context.user_data["time_to_block"] = (start_time, end_time)

                date = context.user_data["date_obj"]

                if context.bot_data["db"]["blocked_slots"].block_time_slot(
                    date, start_time, end_time
                ):
                    await update.message.reply_text(
                        text=f"{ADMIN_MESSAGES['time_blocked']}\n{context.user_data['single_date']}\n{context.user_data['time_to_display']}"
                    )
                    await self.interface.main_menu(update)
                    return ADMIN_MAIN_MENU
                else:
                    await update.message.reply_text(text=ADMIN_MESSAGES["db_error"])
                    await self.interface.main_menu(update)
                    return ADMIN_MAIN_MENU

            except Exception as e:
                self.logger.error(f"Ошибка при блокировке временного слота: {e}")
                await update.message.reply_text(
                    text=f"{ADMIN_MESSAGES['invalid_time_format_or_digit']}\n\n{ADMIN_MESSAGES['enter_time_for_block']}",
                    parse_mode="HTML",
                )
                return ADMIN_BLOCK_TIME

        else:
            await self.interface.invalid_time_format(update)
            return ADMIN_BLOCK_TIME

    async def view_dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для выбора варианта просмотра доступных дат - все даты или с учетом длительности процедуры."""
        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        if text == REPLY_ADMIN_BUTTONS["select_procedure"]:
            await self.interface.procedures(update)
            return ADMIN_SELECT_PROCEDURE
        if text == REPLY_ADMIN_BUTTONS["view_all_dates"]:
            context.user_data["procedure_selected"] = None
            await self.interface.months(update)
            return ADMIN_SELECT_MONTH
        else:
            await update.message.reply_text(
                ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.interface.admin_keyboards["view_dates"],
            )
            return ADMIN_VIEW_DATES

    async def select_procedure(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Хэндлер для выбора процедуры."""

        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        elif text in self.dyn_keyboards.procedures_buttons():
            procedure_name = " ".join(text.split()[1:])
            context.user_data["procedure_selected"] = procedure_name
            context.user_data["reschedule"] = False

            await update.message.reply_text(
                text=text, reply_markup=ReplyKeyboardRemove()
            )

            await self.interface.months(update)
            return ADMIN_SELECT_MONTH
        else:
            await update.message.reply_text(
                ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.interface.general_keyboards["procedures"],
            )
            return USER_SELECT_PROCEDURE

    async def select_month(self, update: Update, context: CallbackContext):
        """Хэндлер для выбора месяца."""

        query = update.callback_query
        await query.answer()
        await query.delete_message()
        chat_id = context.user_data["chat_id"]
        procedure = context.user_data["procedure_selected"]
        if procedure:
            if query.data == "back":
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=ADMIN_MESSAGES["select_procedure"],
                    reply_markup=self.interface.general_keyboards["procedures"],
                )
                return ADMIN_SELECT_PROCEDURE
        else:
            if query.data == "back":
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=ADMIN_MESSAGES["view_dates"],
                    reply_markup=self.interface.admin_keyboards["view_dates"],
                )
                return ADMIN_VIEW_DATES

        if query.data.startswith("month_"):
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
                    text=ADMIN_MESSAGES["select_date"],
                    reply_markup=keyboard,
                )
                return ADMIN_SELECT_DATE

            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=ADMIN_MESSAGES["no_dates_available"],
                    reply_markup=self.interface.general_keyboards["months"],
                )
                return ADMIN_SELECT_MONTH

        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["error_try_again"]
                + "\n"
                + ADMIN_MESSAGES["select_month"],
                reply_markup=self.interface.general_keyboards["months"],
            )
            return ADMIN_SELECT_MONTH

    async def select_date(self, update: Update, context: CallbackContext):
        """Хэндлер для выбора даты."""

        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]

        if query.data == "back_to_months":
            await query.delete_message()
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["select_month"],
                reply_markup=self.interface.general_keyboards["months"],
            )
            return ADMIN_SELECT_MONTH

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
            return ADMIN_SELECT_DATE

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
                    text=ADMIN_MESSAGES["no_slots_available"],
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
                return ADMIN_SELECT_DATE

            keyboard = self.dyn_keyboards.time(available_slots, context)
            context.user_data["time_keyboard"] = keyboard
            if not context.user_data["reschedule"]:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{format_date_for_keyboard(selected_date)}\n\n{ADMIN_MESSAGES["available_slots"]}",
                    reply_markup=keyboard,
                )
                return ADMIN_AFTER_TIME_VIEW
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{format_date_for_keyboard(selected_date)}\n\n{ADMIN_MESSAGES["select_time"]}",
                    reply_markup=keyboard,
                )
                return ADMIN_SELECT_TIME

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
                    text=ADMIN_MESSAGES["error_try_again"],
                    reply_markup=self.interface.admin_keyboards["main_menu"],
                )
                return ADMIN_MAIN_MENU

            await self.interface.dates(update, context)
            return ADMIN_SELECT_DATE

        elif query.data.startswith("time_"):

            time_str = query.data.replace("time_", "")

            try:
                selected_time = datetime.strptime(time_str, "%H:%M:%S").time()
            except ValueError:
                selected_time = datetime.strptime(time_str, "%H:%M").time()

            context.user_data["time_selected"] = selected_time

            confirmation_message = f"{EMOJI["sparkle"]} {context.user_data["procedure_selected"]}\n{EMOJI["calendar"]} {context.user_data["date_selected"]}\n{EMOJI["clock"]} {context.user_data["time_selected"].strftime("%H:%M")}"
            keyboard = self.interface.general_keyboards["confirmation"]
            context.user_data["confirmation_message"] = confirmation_message

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{ADMIN_MESSAGES['confirm_booking']}\n\n{confirmation_message}",
                reply_markup=keyboard,
            )
            return ADMIN_CONFIRMATION

    async def confirmation(self, update: Update, context: CallbackContext):
        """Хэндлер для подтверждения или отмены записи."""

        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]
        await query.delete_message()

        if query.data == "confirm":
            if context.user_data["reschedule"]:
                appointments = context.bot_data["db"].get("appointments")
                appointment_id = context.user_data.get("appointment_id")
                appointments.delete_appointment(appointment_id)

            try:
                await create_appointment_from_context(update, context)
                db_success = True
            except Exception as e:
                db_success = False
                appointments.logger.error(f"Ошибка при записи в базу данных: {e}")

            if db_success:
                if context.user_data["reschedule"]:
                    notification_message = ADMIN_MESSAGES["appointment_updated"]
                else:
                    notification_message = ADMIN_MESSAGES["appointment_added"]
            else:
                notification_message = ADMIN_MESSAGES["db_error"]

            context.user_data["reschedule"] = False
            await context.bot.send_message(
                chat_id=chat_id,
                text=notification_message,
                reply_markup=ReplyKeyboardRemove(),
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        elif query.data == "cancel":
            context.user_data["reschedule"] = False
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["process_interrupted"],
                reply_markup=ReplyKeyboardRemove(),
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        elif query.data == "back_to_edit":
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["select_time"],
                reply_markup=context.user_data["time_keyboard"],
            )
            return ADMIN_SELECT_TIME

    async def after_time_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = context.user_data["chat_id"]
        if query.data == "back_to_admin_menu":
            await query.delete_message()
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["hello_admin"],
                reply_markup=self.interface.admin_keyboards["main_menu"],
            )
            return ADMIN_MAIN_MENU
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.user_data["time_keyboard"],
            )
        return ADMIN_AFTER_TIME_VIEW

    async def clients_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Хэндлер для меню работы с разделом 'Клиенты'."""
        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        else:
            clients = context.bot_data["db"]["clients"]
            if clients.client_is_registered_by_phone(text):
                client_data = clients.get_client_by_telephone(text)

                if client_data:
                    if len(client_data) > 1:
                        message = ADMIN_MESSAGES["contact_developer"]
                        message += (
                            f"\n\n<b>{ADMIN_MESSAGES["multiple_clients_found"]}</b>"
                        )
                        keyboard = []
                        for client in client_data:
                            button_text = f"{client[5]} (username: {client[3]})"
                            callback_data = f"select_client_{client[0]}"
                            keyboard.append(
                                [
                                    InlineKeyboardButton(
                                        button_text, callback_data=callback_data
                                    )
                                ]
                            )

                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(
                            message, parse_mode="HTML", reply_markup=reply_markup
                        )
                        return SELECT_CLIENT_FROM_MULTIPLE
                    else:
                        client_id = client_data[0][0]
                        context.user_data["client_id"] = client_id
                        clients = context.bot_data["db"]["clients"]
                        client = clients.get_client_by_id(int(client_id))[0]
                        context.user_data["client"] = client

                        if len(client) == 4:
                            message = (
                                "<b>Данные клиента:</b>\n"
                                f"{EMOJI['user']} <i>Имя:</i> {client[1]}\n"
                                f"{EMOJI['phone']} <i>Телефон:</i> {client[2]}\n"
                                f"{EMOJI['star']} <i>Username:</i> {client[3]}\n"
                            )
                        else:
                            message = (
                                "<b>Данные клиента:</b>\n"
                                f"{EMOJI['user']} <i>Имя:</i> {client[1]}\n"
                                f"{EMOJI['phone']} <i>Телефон:</i> {client[2]}\n"
                            )
                        await update.message.reply_text(
                            message,
                            parse_mode="HTML",
                            reply_markup=self.interface.admin_keyboards["client"],
                        )
                        return ADMIN_CLIENT
                else:
                    await update.message.reply_text(ADMIN_MESSAGES["client_error"])
            else:
                await update.message.reply_text(
                    text=ADMIN_MESSAGES["client_not_found"],
                    reply_markup=ReplyKeyboardRemove(),
                )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

    async def select_client(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        await query.delete_message()

        if query.data.startswith("select_client"):
            client_id = query.data.split("_")[2]

            context.user_data["client_id"] = client_id
            clients = context.bot_data["db"]["clients"]
            client = clients.get_client_by_id(int(client_id))[0]
            context.user_data["client"] = client
            if len(client) == 4:
                message = (
                    "<b>Данные клиента:</b>\n"
                    f"{EMOJI['user']} <i>Имя:</i> {client[1]}\n"
                    f"{EMOJI['phone']} <i>Телефон:</i> {client[2]}\n"
                    f"{EMOJI['star']} <i>Username:</i> {client[3]}\n"
                )
            else:
                message = (
                    "<b>Данные клиента:</b>\n"
                    f"{EMOJI['user']} <i>Имя:</i> {client[1]}\n"
                    f"{EMOJI['phone']} <i>Телефон:</i> {client[2]}\n"
                )
            chat_id = context.user_data["chat_id"]
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                reply_markup=self.interface.admin_keyboards["client"],
            )
            return ADMIN_CLIENT
        else:
            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES["error_try_again"]}",
                reply_markup=ReplyKeyboardRemove(),
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

    async def select_client_unexpected_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text
        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        else:
            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES["error_try_again"]}",
                reply_markup=ReplyKeyboardRemove(),
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

    async def client(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        client_id = context.user_data["client_id"]

        if text == REPLY_ADMIN_BUTTONS["view_client_appointments"]:
            if context.bot_data["db"]["appointments"].client_has_appointments(
                int(client_id)
            ):
                await self.interface.view_appointments(update, context, int(client_id))
                return ADMIN_VIEW_APPOINTMENTS

            else:
                await update.message.reply_text(
                    text=f"{ADMIN_MESSAGES["client_has_no_appointments"]}",
                    reply_markup=ReplyKeyboardRemove(),
                )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        if text == REPLY_ADMIN_BUTTONS["delete_client"]:
            client = context.user_data["client"]
            message = (
                f"{EMOJI['sign']}Удалить клиента {client[1]} с телефоном {client[2]}?"
            )
            await update.message.reply_text(
                text=message,
                reply_markup=self.interface.admin_keyboards["delete_client"],
            )
            return ADMIN_DELETE_CLIENT

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        else:
            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES["error_try_again"]}",
                reply_markup=ReplyKeyboardRemove(),
            )
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

    async def delete_client(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        if text == REPLY_ADMIN_BUTTONS["delete"]:
            client_id = context.user_data["client_id"]
            if context.bot_data["db"]["clients"].delete_client_by_id(int(client_id)):
                await update.message.reply_text(
                    text=f"{ADMIN_MESSAGES["client_deleted"]}",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU
            else:
                await update.message.reply_text(
                    text=f"{ADMIN_MESSAGES["db_error"]}",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await self.interface.main_menu(update)
                return ADMIN_MAIN_MENU

        elif text == REPLY_ADMIN_BUTTONS["dont_delete_back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        elif text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        else:
            client = context.user_data["client"]
            message = (
                f"{EMOJI['sign']} Удалить клиента {client[1]} с телефоном {client[2]}?"
            )
            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES["error_try_again"]}\n\n{message}",
                reply_markup=self.interface.admin_keyboards["delete_client"],
            )
            return ADMIN_DELETE_CLIENT

    async def view_client_appointments(self, update: Update, context: CallbackContext):
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
            date = format_date_for_keyboard(
                context.user_data["appointment_for_editing"][2]
            )
            time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"<b>Выбранная запись</b>: {procedure} - {date} - {time}.\n",
                parse_mode="HTML",
                reply_markup=self.interface.admin_keyboards["appointments_actions"],
            )
            return ADMIN_APPOINTMENT_EDIT_ACTIONS

        if query.data == "back_to_menu":
            text = ADMIN_MESSAGES["hello_admin"]
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.interface.admin_keyboards["main_menu"],
            )
            return ADMIN_MAIN_MENU

    async def appointment_edit_actions(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text
        id = context.user_data["client_id"]

        procedure = context.user_data["procedure_selected"]
        date = format_date_for_keyboard(context.user_data["appointment_for_editing"][2])
        time = context.user_data["appointment_for_editing"][3].strftime("%H:%M")

        if text == REPLY_ADMIN_BUTTONS["reschedule_appointment"]:
            context.user_data["reschedule"] = True
            await update.message.reply_text(
                text=f"{procedure} - {date} - {time}",
                reply_markup=ReplyKeyboardRemove(),
            )

            await self.interface.months(update)
            return ADMIN_SELECT_MONTH

        if text == REPLY_ADMIN_BUTTONS["delete_appointment"]:
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
                f"{ADMIN_MESSAGES['appointment_removed']}"
                f"{appointment_data[0]}\n"
                f"Дата: {appointment_data[1]}\n"
                f"Время: {appointment_data[2].strftime("%H:%M")}\n"
                f"Телефон: {appointment_data[4]}\n\n"
            )

            if db_success:
                notification_message += ADMIN_MESSAGES["db_success"]
            else:
                notification_message += ADMIN_MESSAGES["db_error"]

            await update.message.reply_text(
                text=notification_message,
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])]],
                    resize_keyboard=True,
                ),
            )
            return ADMIN_VIEW_DATES

        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            context.user_data["reschedule"] = False
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU

        if text == REPLY_ADMIN_BUTTONS["back_to_appointments"]:
            context.user_data["reschedule"] = False
            if context.bot_data["db"]["appointments"].client_has_appointments(int(id)):
                await self.interface.view_appointments(update, context, int(id))
                return ADMIN_VIEW_APPOINTMENTS
            else:
                await update.message.reply_text(
                    text=f"{ADMIN_MESSAGES["client_has_no_appointments"]}",
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(REPLY_ADMIN_BUTTONS["back_to_menu"])]],
                        resize_keyboard=True,
                    ),
                )
            return ADMIN_VIEW_DATES

        else:
            context.user_data["reschedule"] = False
            await update.message.reply_text(
                text=f"{ADMIN_MESSAGES["error_try_again"]}",
                reply_markup=self.interface.admin_keyboards["appointments_actions"],
            )
            return ADMIN_APPOINTMENT_EDIT_ACTIONS

    async def appointments_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):

        text = update.message.text

        if text == REPLY_ADMIN_BUTTONS["view_appointments"]:
            pass
        if text == REPLY_ADMIN_BUTTONS["add_appointment"]:
            pass
        if text == REPLY_ADMIN_BUTTONS["reschedule_appointment"]:
            pass
        if text == REPLY_ADMIN_BUTTONS["delete_appointment"]:
            pass
        if text == REPLY_ADMIN_BUTTONS["back_to_menu"]:
            await self.interface.main_menu(update)
            return ADMIN_MAIN_MENU
        else:
            await update.message.reply_text(
                ADMIN_MESSAGES["error_try_again"],
                reply_markup=self.interface.admin_keyboards["appointments_menu"],
            )
            return ADMIN_APPOINTMENTS_MENU

    #     elif text == "Заблокировать день":
    #         await update.message.reply_text(
    #             "Введите дату для блокировки в формате **ДД.ММ.ГГГГ** (например, **28.02.2025**):"
    #         )
    #         return ADMIN_BLOCK_DAY

    #     elif text == "Заблокировать несколько дней":
    #         await update.message.reply_text(
    #             "Введите дату начала блокировки и продолжительность в днях в формате **ДД.ММ.ГГГГ ДНИ** (например, **28.02.2025 3**):"
    #         )
    #         return ADMIN_BLOCK_SEVERAL_DAYS

    #     elif text == "Заблокировать время":
    #         await update.message.reply_text(
    #             "Введите дату и временной промежуток для блокировки в формате **ДД.ММ.ГГГГ ЧЧ:ММ-ЧЧ:ММ** (например, **28.02.2025 10:00-12:00**):"
    #         )
    #         return ADMIN_BLOCK_TIME

    #     elif text == "Добавить процедуру":
    #         await update.message.reply_text(
    #             "Введите название и продолжительность новой процедуры в формате **Название (мин)**, например **Окрашивание ресниц (60)**:",
    #         )
    #         return ADMIN_ADD_PROCEDURE

    #     elif text == "Сделать процедуру неактивной":
    #         await update.message.reply_text(
    #             "Выберите процедуру:",
    #             reply_markup=context.bot_data["procedures_keyboard"],
    #         )
    #         return ADMIN_DEACTIVATE_PROCEDURE

    #     else:
    #         await update.message.reply_text(
    #             "Неизвестная команда. Пожалуйста, выберите действие из меню."
    #         )
    #         return ADMIN_ACTIONS

    # async def handle_admin_procedure_selection(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     text = update.message.text
    #     if text == "⬅️ Вернуться в меню":
    #         await update.message.reply_text(
    #             "Пожалуйста, выберите действие",
    #             reply_markup=context.bot_data["admin_main_menu_keyboard"],
    #         )
    #         return ADMIN_ACTIONS
    #     else:
    #         user_data["procedure_selected"] = " ".join(text.split()[1:])
    #         await update.message.reply_text(
    #             f"Вы выбрали процедуру: {text}. Теперь выберите дату.",
    #             reply_markup=date_keyboard(context),
    #         )
    #         return ADMIN_SELECT_DATE

    # async def handle_admin_date_selection(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     text = update.message.text

    #     if text == "Вернуться к выбору процедуры":
    #         await update.message.reply_text(
    #             "Пожалуйста, выберите процедуру",
    #             reply_markup=context.bot_data["procedures_keyboard"],
    #         )
    #         return ADMIN_SELECT_PROCEDURE

    #     else:
    #         date = text
    #         formatted_date = format_date_for_db(date)
    #         user_data["date_selected"] = date
    #         user_data["date_formatted"] = formatted_date
    #         keyboard, message = time_keyboard(
    #             context, formatted_date, user_data["procedure_id"]
    #         )

    #     if message:
    #         await update.message.reply_text(
    #             message,
    #             reply_markup=keyboard,
    #         )
    #     else:
    #         await update.message.reply_text(
    #             f"Вы выбрали дату: {date}. Теперь выберите время.",
    #             reply_markup=keyboard,
    #         )
    #     return ADMIN_SELECT_TIME

    # async def handle_admin_time_selection(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     text = update.message.text

    #     if text == "Назад" or text == "Вернуться к выбору даты":
    #         await update.message.reply_text(
    #             "Пожалуйста, выберите дату.",
    #             reply_markup=date_keyboard(context),
    #         )
    #         return ADMIN_SELECT_DATE

    #     else:
    #         time = text
    #         time_obj = datetime.strptime(time, "%H:%M").time()

    #         user_data["time_selected"] = time
    #         user_data["time_formatted"] = time_obj

    #         await update.message.reply_text(
    #             f"Вы выбрали время: {time}. Пожалуйста, введите имя клиента.",
    #             reply_markup=ReplyKeyboardRemove(),
    #         )

    #         return ADMIN_ENTER_CLIENT_NAME

    # async def handle_admin_enter_client_name(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):

    #     name = update.message.text

    #     if len(name) < 2:
    #         await update.message.reply_text(
    #             "Имя должно содержать не менее двух символов. Пожалуйста, введите имя клиента."
    #         )
    #         return ADMIN_ENTER_CLIENT_NAME

    #     user_data["name"] = name
    #     await update.message.reply_text(
    #         "Пожалуйста, введите телефон клиента в формате +7XXXXXXXXXX."
    #     )
    #     return ADMIN_ENTER_CLIENT_PHONE

    # async def handle_admin_enter_client_phone(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):

    #     phone = update.message.text

    #     if not re.match(r"^\+7\d{10}$", phone):
    #         await update.message.reply_text(
    #             "Пожалуйста, введите телефон в формате **+7XXXXXXXXXX**."
    #         )
    #         return ADMIN_ENTER_CLIENT_PHONE
    #     else:

    #         user_data["phone"] = phone

    #         await update.message.reply_text(
    #             "Если у вас есть комментарий к записи, введите его. Если нет, нажмите 'Пропустить'.",
    #             reply_markup=InlineKeyboardMarkup(
    #                 [[InlineKeyboardButton("Пропустить", callback_data="skip")]]
    #             ),
    #         )

    #         return ADMIN_ENTER_COMMENT

    # async def handle_admin_text_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     comment = update.message.text

    #     user_data["comment"] = comment

    #     confirmation_message = (
    #         f"Пожалуйста, подтвердите запись:\n"
    #         f"Процедура: {user_data['procedure_selected']}\n"
    #         f"Дата: {user_data['date_selected']}\n"
    #         f"Время: {user_data['time_selected']}\n"
    #         f"Имя: {user_data['name']}\n"
    #         f"Телефон: {user_data['phone']}\n"
    #         f"Комментарий: {user_data.get('comment', 'нет комментария')}"
    #     )
    #     await update.message.reply_text(
    #         confirmation_message, reply_markup=context.bot_data["confirmation_keyboard"]
    #     )
    #     return ADMIN_CONFIRMATION

    # async def handle_admin_skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     await query.answer()

    #     user_data["comment"] = "нет комментария"

    #     confirmation_message = (
    #         f"Пожалуйста, подтвердите запись:\n"
    #         f"Процедура: {user_data['procedure_selected']}\n"
    #         f"Дата: {user_data['date_selected']}\n"
    #         f"Время: {user_data['time_selected']}\n"
    #         f"Имя: {user_data['name']}\n"
    #         f"Телефон: {user_data['phone']}\n"
    #         f"Комментарий: нет"
    #     )
    #     await query.edit_message_text(
    #         confirmation_message, reply_markup=context.bot_data["confirmation_keyboard"]
    #     )
    #     return ADMIN_CONFIRMATION

    # async def handle_admin_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #     query = update.callback_query
    #     await query.answer()

    #     if query.data == "confirm":
    #         create_appointment_from_context(update, context)
    #         await query.edit_message_text(
    #             "Запись подтверждена✅ Что вы хотите сделать дальше?",
    #             reply_markup=context.bot_data["admin_final_keyboard"],
    #         )

    #     elif query.data == "cancel":
    #         await query.edit_message_text(
    #             "Запись отменена❌ Что вы хотите сделать дальше?",
    #             reply_markup=context.bot_data["admin_final_keyboard"],
    #         )

    #         return ADMIN_AFTER_CONFIRMATION

    # async def handle_admin_after_confirmation(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     text = update.message.text

    #     if text == "Вернуться в главное меню":
    #         return ADMIN_ACTIONS

    # async def handle_block_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     date_str = update.message.text
    #     try:
    #         formatted_date = format_date_for_db_admin(date_str)
    #         blocked_slots = context.bot_data["blocked_slots"]
    #         blocked_slots.block_day(formatted_date)
    #         await update.message.reply_text(f"День {date_str} успешно заблокирован.")
    #         return ADMIN_ACTIONS
    #     except ValueError:
    #         await update.message.reply_text(
    #             "Неверный формат даты. Используйте **ДД.ММ.ГГГГ** (например, **28.02.2025**)."
    #         )
    #         return ADMIN_BLOCK_DAY

    # async def handle_block_several_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     date_str, days_str = update.message.text.split()
    #     try:
    #         start_date = format_date_for_db_admin(date_str)
    #         days = int(days_str)
    #         blocked_slots = context.bot_data["blocked_slots"]
    #         blocked_slots.block_several_days(start_date, days)
    #         day_form, verb_form = (
    #             "день" if days == 1 else "дня" if days in [2, 3, 4] else "дней"
    #         ), ("заблокирован" if days == 1 else "заблокированы")
    #         await update.message.reply_text(
    #             f"{days} {day_form}, начиная с {date_str}, {verb_form}."
    #         )
    #     except ValueError:
    #         await update.message.reply_text(
    #             "Неверный формат. Используйте **ДД.ММ.ГГГГ ДНИ** (например, **28.02.2025 3**)."
    #         )
    #     return ADMIN_ACTIONS

    # async def handle_block_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     input_text = update.message.text
    #     try:
    #         date_str, time_range = input_text.split()
    #         start_time_str, end_time_str = time_range.split("-")
    #         date = datetime.strptime(date_str, "%Y-%m-%d").date()
    #         start_time = datetime.strptime(start_time_str, "%H:%M").time()
    #         end_time = datetime.strptime(end_time_str, "%H:%M").time()
    #         blocked_slots = context.bot_data["blocked_slots"]
    #         blocked_slots.block_time_slot(date, start_time, end_time)
    #         await update.message.reply_text(
    #             f"Временной промежуток {time_range} на {date_str} успешно заблокирован."
    #         )
    #     except ValueError:
    #         await update.message.reply_text(
    #             "Неверный формат. Используйте **ДД.ММ.ГГГГ ЧЧ:ММ-ЧЧ:ММ** (например, **28.02.2025 10:00-12:00**)."
    #         )
    #     return ADMIN_ACTIONS

    # async def handle_admin_add_appointment(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):

    #     telephone = update.message.text

    #     client = await handle_admin_find_client(update, context, telephone)

    #     if client:
    #         pass
    #         # client_id, client_telephone, client_name = client
    #         # appointments.create_appointment(client_id, procedure, appointment_date, appointment_time)

    #         await update.message.reply_text("Запись на процедуру добавлена.")
    #     else:
    #         await update.message.reply_text(
    #             "Клиент не найден. В таблицу Clients будет добавлен новый клиент."
    #         )

    # async def handle_admin_find_client(
    #     update: Update, context: ContextTypes.DEFAULT_TYPE, telephone: str
    # ):

    #     client = context.bot_data["clients"].get_client_by_telephone(telephone)

    #     if client:
    #         return client

    #     else:
    #         await update.message.reply_text("Клиент не найден.")
