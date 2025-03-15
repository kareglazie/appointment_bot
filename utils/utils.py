from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from consts.constants import PROCEDURES


async def basic_context_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновить контекст с основными данными пользователя."""
    tg_id = update.effective_user.id
    context.user_data["tg_id"] = tg_id
    chat_id = update.effective_chat.id
    context.user_data["chat_id"] = chat_id
    tg_username = update.effective_user.username
    context.user_data["tg_username"] = tg_username
    tg_first_name = update.effective_user.first_name
    context.user_data["tg_first_name"] = tg_first_name


async def create_appointment_from_context(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Создать запись на основе данных из контекста."""

    tg_id = int(context.user_data["tg_id"])
    tg_username = context.user_data["tg_username"]
    tg_first_name = context.user_data["tg_first_name"]
    procedure_name = context.user_data["procedure_selected"]
    date_selected = context.user_data["date_selected"]
    time_selected = context.user_data["time_selected"]
    name = context.user_data["name"]
    phone = context.user_data["phone"]

    clients = context.bot_data["db"]["clients"]
    appointments = context.bot_data["db"]["appointments"]

    clients.add_client(
        tg_id=tg_id,
        tg_first_name=tg_first_name,
        tg_username=tg_username,
        name=name,
        telephone=phone,
    )

    procedure_duration = timedelta(minutes=PROCEDURES.get(procedure_name))
    end_time = datetime.combine(date_selected, time_selected) + procedure_duration

    appointments.create_appointment(
        tg_id=tg_id,
        client_name=name,
        client_telephone=phone,
        procedure=procedure_name,
        date=date_selected,
        start_time=time_selected,
        end_time=end_time.time(),
    )
