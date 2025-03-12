from database.clients import Clients
from logger import setup_logger
from database import Database
from typing import Optional, List, Tuple
from datetime import date, time


class Appointments:

    def __init__(self, db: Database, clients: Clients):
        self.db = db
        self.clients = clients
        self.logger = setup_logger(__name__)

    def create_appointment(
        self,
        client_name: str,
        client_telephone: str,
        procedure: str,
        date: date,
        start_time: time,
        end_time: time,
    ):
        """Добавить запись на процедуру."""
        client_id = self.clients.get_client_id_by_telephone(client_telephone)
        query = """
            INSERT INTO Appointments (client_id, procedure, date, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, client_id, procedure, date, start_time, end_time)
        self.logger.debug(
            f"Параметры записи: Процедура: {procedure}, дата: {date}, время начала: {start_time}, клиент: {client_name}, телефон: {client_telephone}"
        )

    def get_appointments_by_date(self, date: date) -> Optional[List[Tuple]]:
        """Получить все записи на конкретную дату."""

        query = """
            SELECT a.id, a.procedure, c.tg_first_name, c.tg_username, c.name, c.telephone, 
                a.start_time, a.end_time, a.comment 
            FROM Appointments a
            JOIN Clients c ON a.client_id = c.id
            WHERE a.date = %s
            ORDER BY a.start_time
        """
        result = self.db.fetch_data(query, date)
        return result

    def get_all_appointments(self) -> Optional[List[Tuple]]:
        """Получить все записи из таблицы Appointments."""

        query = """
            SELECT a.date, a.procedure, c.name, c.telephone, 
            a.start_time, a.end_time 
            FROM Appointments a
            JOIN Clients c ON a.client_id = c.id
            ORDER BY a.date, a.start_time
        """
        result = self.db.fetch_data(query)
        self.logger.debug(
            f"Запрос на получение всех записей из таблицы Appointments выполнен."
        )
        return result

    def client_has_appointments(self, client_id: int) -> bool:
        """Проверить, есть ли у клиента записи."""
        query = """
            SELECT COUNT(*) FROM Appointments WHERE client_id = %s
        """
        result = self.db.fetch_data(query, client_id)
        return result[0][0] > 0

    def get_client_appointments(self, client_id: int) -> Optional[List[Tuple]]:
        """Получить все записи для клиента по ID."""

        query = """
            SELECT a.id, a.procedure, a.date, a.start_time, a.end_time
            FROM Appointments a
            WHERE a.client_id = %s
            ORDER BY a.date, a.start_time
        """
        result = self.db.fetch_data(query, client_id)
        self.logger.debug(f"Записи для клиента с ID {client_id}: {result}.")

        return result

    def delete_appointment(self, appointment_id: int):
        """
        Удалить запись из таблицы Appointments по её ID.

        :param appointment_id: Идентификатор записи.
        :return: True, если запись успешно удалена, иначе False.
        """
        query = """
            DELETE FROM Appointments
            WHERE id = %s
        """
        try:
            self.db.execute_query(query, appointment_id)
            self.logger.debug(f"Запись с ID {appointment_id} успешно удалена.")
        except Exception as e:
            self.logger.error(f"Ошибка при удалении записи с ID {appointment_id}: {e}")

    def get_client_data_by_appointment_id(self, appointment_id: int) -> Tuple:
        """
        Получить данные клиента по идентификатору записи в таблице Appointments.
        """
        query = """
            SELECT a.procedure, a.date, a.start_time, c.tg_username, c.telephone
            FROM Appointments a
            JOIN Clients c ON a.client_id = c.id
            WHERE a.id = %s
        """
        result = self.db.fetch_data(query, appointment_id)[0]
        print(f"RESULT: {result}")
        return result

    def reschedule_appointment(
        self,
        appointment_id: int,
        client_name: str,
        client_telephone: str,
        procedure: str,
        date: date,
        start_time: time,
        end_time: time,
    ):
        """
        Перенести запись на другое время.
        """

        self.delete_appointment(appointment_id)
        self.create_appointment(
            client_name, client_telephone, procedure, date, start_time, end_time
        )
