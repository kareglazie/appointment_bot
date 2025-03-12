from database import Database
from database.clients import Clients
from database.blocked_slots import BlockedSlots
from database.appointments import Appointments
from database.schedule import Schedule


def setup_database():
    """Настроить базу данных."""
    db = Database()
    db.connect()

    clients = Clients(db)
    blocked_slots = BlockedSlots(db)
    appointments = Appointments(db, clients)
    schedule = Schedule(db, blocked_slots)

    return {
        "db": db,
        "clients": clients,
        "blocked_slots": blocked_slots,
        "appointments": appointments,
        "schedule": schedule,
    }
