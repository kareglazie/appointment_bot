from logger import setup_logger
from database import Database
from typing import Optional, List, Tuple
from datetime import date, time


class Appointments:
    """Класс для работы с таблицей Appointments (записи клиентов)."""

    def __init__(self, db: Database):
        self.db = db
        self.logger = setup_logger(__name__)

    def create_appointment(
        self,
        procedure: str,
        client_phone: str,
        date: date,
        start_time: time,
        end_time: time,
    ) -> None:
        """Создать запись в таблице Appointments."""

        query = """
            INSERT INTO Appointments 
            (procedure, client_phone, date, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            query,
            procedure,
            client_phone,
            date,
            start_time,
            end_time,
        )
        self.logger.debug("Запись в таблице Appointments создана")
        self.logger.debug(
            f"Параметры записи: Процедура: {procedure}, телефон: {client_phone}, дата: {date}, время начала: {start_time}, время окончания: {end_time}"
        )

    def get_appointments_by_date(self, date: date) -> Optional[List[Tuple]]:
        """Получить все записи на конкретную дату."""

        query = """
            SELECT a.id, a.procedure, c.tg_first_name, c.tg_username, c.name, c.telephone, 
                a.start_time, a.end_time, a.comment 
            FROM Appointments a
            JOIN Clients c ON a.client_phone = c.telephone
            WHERE a.date = %s
            ORDER BY a.start_time
        """
        result = self.db.execute_query(
            query,
            date,
        )
        return result

    def get_all_appointments(self) -> Optional[List[Tuple]]:
        """Получить все записи из таблицы Appointments."""

        query = """
            SELECT a.date, a.procedure, c.name, c.telephone, 
            a.start_time, a.end_time 
            FROM Appointments a
            JOIN Clients c ON a.client_phone = c.telephone
            ORDER BY a.date, a.start_time
        """
        result = self.db.execute_query(query)
        self.logger.debug(
            f"Запрос на получение всех записей из таблицы Appointments выполнен."
        )
        return result
