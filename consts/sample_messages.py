"""Сообщения, тексты кнопок, эмодзи."""

EMOJI = {"back": "⬅️", "blocked": "🚫", "schedule": "📋", "sparkle": "✨"}

# Сообщения для пользователя
USER_MESSAGES = {
    "SELECT_PROCEDURE": f"{EMOJI['sparkle']} Выберите процедуру:",
}

REPLY_USER_BUTTONS = {
    "BACK_TO_MENU": f"{EMOJI['back']} Вернуться в меню",
}
# Сообщения для администратора
ADMIN_MESSAGES = {
    "NOT_AUTHORIZED": f"{EMOJI['blocked']} У вас нет прав администратора.",
}

REPLY_ADMIN_BUTTONS = {
    "ADD_RECORD": f"{EMOJI['schedule']} Добавить запись",
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

INLINE_BUTTONS = {"edit_booking": f"Изменить {EMOJI['schedule']}"}
