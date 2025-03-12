from telegram import KeyboardButton, ReplyKeyboardMarkup

from messages import REPLY_ADMIN_BUTTONS


def admin_main_menu_keyboard():
    keyboard = [
        [KeyboardButton(REPLY_ADMIN_BUTTONS["ADD_RECORD"])],
        [KeyboardButton(REPLY_ADMIN_BUTTONS["DELETE_RECORD"])],
        [KeyboardButton(REPLY_ADMIN_BUTTONS["VIEW_RECORDS"])],
        [KeyboardButton(REPLY_ADMIN_BUTTONS["VIEW_SLOTS"])],
        [KeyboardButton(REPLY_ADMIN_BUTTONS["EXIT"])],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# def admin_procedures_keyboard(procedures):
#     buttons = [[proc[1]] for proc in procedures]
#     return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# def admin_dates_keyboard(dates):
#     buttons = [[date.strftime("%Y-%m-%d")] for date in dates]
#     return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# def admin_times_keyboard(times):
#     buttons = [[time.strftime("%H:%M")] for time in times]
#     return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def admin_final_keyboard():

    return ReplyKeyboardMarkup(
        [[REPLY_ADMIN_BUTTONS["BACK_TO_MENU"]]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
