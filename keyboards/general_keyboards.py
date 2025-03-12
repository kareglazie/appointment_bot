from datetime import date, datetime, time, timedelta
import locale
from typing import List, Tuple
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from messages import EMOJI, INLINE_BUTTONS, REPLY_USER_BUTTONS
from constants import MONTHS_LOOKAHEAD, PROCEDURES_KEYBOARD


def month_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора месяца."""
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    today = date.today()
    keyboard = []
    row = []

    for i in range(MONTHS_LOOKAHEAD):
        year_offset = (today.month + i - 1) // 12
        month = (today.month + i - 1) % 12 + 1
        current_year = today.year + year_offset

        month_name = date(current_year, month, 1).strftime("%B")
        row.append(
            InlineKeyboardButton(
                month_name.capitalize(),
                callback_data=f"month_{month}_{current_year}",
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append(
        [InlineKeyboardButton(INLINE_BUTTONS["BACK"], callback_data="back")]
    )

    return InlineKeyboardMarkup(keyboard)


def date_keyboard(
    year: int, month: int, available_dates: List[date]
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора даты в указанном месяце."""
    keyboard = []
    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    header = []
    today = date.today()

    start_month = today.month
    start_year = today.year
    end_month = (start_month + MONTHS_LOOKAHEAD - 1) % 12
    end_year = start_year + (start_month + MONTHS_LOOKAHEAD - 1) // 12

    if not (month == start_month and year == start_year):
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        header.append(
            InlineKeyboardButton(
                EMOJI["BACK"], callback_data=f"prev_month_{prev_year}_{prev_month}"
            )
        )

    header.append(
        InlineKeyboardButton(first_day.strftime("%B %Y"), callback_data="ignore")
    )

    if not (month == end_month and year == end_year):
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        header.append(
            InlineKeyboardButton(
                EMOJI["FORWARD"],
                callback_data=f"next_month_{next_year}_{next_month}",
            )
        )

    keyboard.append(header)

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append(
        [InlineKeyboardButton(day, callback_data="ignore") for day in weekdays]
    )

    row = []
    start_day = 1

    first_weekday = first_day.weekday()

    for _ in range(first_weekday):
        row.append(InlineKeyboardButton(" ", callback_data="ignore"))

    for day in range(start_day, last_day.day + 1):
        current_date = datetime(year, month, day).date()

        if current_date <= today:
            row.append(InlineKeyboardButton(EMOJI["LOCK"], callback_data="ignore"))
        elif current_date in available_dates:
            row.append(
                InlineKeyboardButton(str(day), callback_data=f"date_{current_date}")
            )
        else:
            row.append(InlineKeyboardButton(EMOJI["LOCK"], callback_data="ignore"))

        if len(row) == 7:
            keyboard.append(row)
            row = []

    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["BACK_TO_MONTHS"], callback_data="back_to_months"
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def time_keyboard(available_slots: List[Tuple[time, time]]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора времени."""
    keyboard = []

    total_slots = len(available_slots)

    max_columns = 7

    if total_slots <= max_columns:
        columns = total_slots
        rows = 1
    else:
        columns = max_columns
        rows = (total_slots + columns - 1) // columns

    for row_index in range(rows):
        row = []
        for col_index in range(columns):
            slot_index = row_index * columns + col_index
            if slot_index < total_slots:
                start_time, _ = available_slots[slot_index]
                button_text = start_time.strftime("%H:%M")
                row.append(
                    InlineKeyboardButton(
                        button_text, callback_data=f"time_{start_time}"
                    )
                )
            else:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["BACK_TO_DATES"], callback_data="back_to_dates"
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def procedures_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для выбора процедуры."""
    keyboard = PROCEDURES_KEYBOARD

    keyboard.append([KeyboardButton(REPLY_USER_BUTTONS["BACK_TO_MENU"])])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def confirmation_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения или отмены записи."""
    keyboard = [
        [
            InlineKeyboardButton(
                INLINE_BUTTONS["CONFIRM_BOOKING"], callback_data="confirm"
            ),
            InlineKeyboardButton(
                INLINE_BUTTONS["CANCEL_BOOKING"], callback_data="cancel"
            ),
            InlineKeyboardButton(
                INLINE_BUTTONS["EDIT_BOOKING"], callback_data="back_to_edit"
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
