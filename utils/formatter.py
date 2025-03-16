from datetime import datetime


def format_date_for_keyboard(date):
    """Форматировать дату для клавиатуры."""

    days = {
        "понедельник": "ПН",
        "вторник": "ВТ",
        "среда": "СР",
        "четверг": "ЧТ",
        "пятница": "ПТ",
        "суббота": "СБ",
        "воскресенье": "ВС",
    }

    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }

    day_of_week = days[date.strftime("%A")]
    day = date.day
    month = months[date.month]

    formatted_date = f"{day_of_week}, {day} {month}"

    return formatted_date


def format_date_for_client_interface(date):
    """Форматировать дату для клиентского интерфейса."""

    months = {
        "Январь": "января",
        "Февраль": "февраля",
        "Март": "марта",
        "Апрель": "апреля",
        "Май": "мая",
        "Июнь": "июня",
        "Июль": "июля",
        "Август": "августа",
        "Сентябрь": "сентября",
        "Октябрь": "октября",
        "Ноябрь": "ноября",
        "Декабрь": "декабря",
    }
    day_of_week = date.strftime("%A").capitalize()
    day = date.day
    month = months[date.strftime("%B")]

    formatted_date = f"{day_of_week}, {day} {month}"

    return formatted_date


def format_date_for_db(date):
    """Форматировать дату для базы данных."""

    months = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }
    year = datetime.now().year
    month = months[date.split(",")[1].strip().split()[1]]
    day = int(date.split(",")[1].strip().split()[0])

    return datetime(year, month, day)


def format_date_for_db_admin(date):
    """Форматировать дату для базы данных из панели администратора."""

    return datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
