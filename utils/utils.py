from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from constants import PROCEDURES


async def basic_context_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновить контекст с основными данными пользователя."""
    user_id = update.effective_user.id
    context.user_data["user_id"] = user_id
    user_tg_username = update.effective_user.username
    context.user_data["user_tg_username"] = user_tg_username
    user_tg_first_name = update.effective_user.first_name
    context.user_data["user_tg_first_name"] = user_tg_first_name


async def create_appointment_from_context(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Создать запись на основе данных из контекста."""

    user_id = context.user_data["user_id"]
    user_tg_username = context.user_data["user_tg_username"]
    user_tg_first_name = context.user_data["user_tg_first_name"]
    procedure_name = context.user_data["procedure_selected"]
    date_selected = context.user_data["date_selected"]
    time_selected = context.user_data["time_selected"]
    name = context.user_data["name"]
    phone = context.user_data["phone"]

    clients = context.bot_data["clients"]
    appointments = context.bot_data["appointments"]

    clients.add_client(
        tg_id=user_id,
        tg_first_name=user_tg_first_name,
        tg_username=user_tg_username,
        name=name,
        telephone=phone,
    )

    procedure_duration = timedelta(minutes=PROCEDURES.get(procedure_name))
    end_time = datetime.combine(date_selected, time_selected) + procedure_duration

    appointments.create_appointment(
        procedure=procedure_name,
        client_phone=phone,
        date=date_selected,
        start_time=time_selected,
        end_time=end_time.time(),
    )
