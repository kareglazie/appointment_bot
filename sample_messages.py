"""Сообщения для бота."""

EMOJI = {"BACK": "⬅️", "BLOCKED": "🚫", "SCHEDULE": "📋", "SPARKLE": "✨"}

# Сообщения для пользователей
USER_MESSAGES = {
    "SELECT_PROCEDURE": f"{EMOJI['SPARKLE']} Выберите процедуру:",
}

REPLY_USER_BUTTONS = {
    "BACK_TO_MENU": f"{EMOJI['BACK']} Вернуться в меню",
}
# Сообщения для администратора
ADMIN_MESSAGES = {
    "NOT_AUTHORIZED": f"{EMOJI['BLOCKED']} У вас нет прав администратора.",
}

REPLY_ADMIN_BUTTONS = {
    "ADD_RECORD": f"{EMOJI['SCHEDULE']} Добавить запись",
}

CONFIRMATION_MESSAGE = {
    "BOOKING_DETAILS": (
        """
Процедура: {procedure}
Дата: {date}
Время: {time}
Имя: {name}
Телефон: {phone}
"""
    )
}

INLINE_BUTTONS = {"EDIT_BOOKING": f"Изменить {EMOJI['SCHEDULE']}"}
