from datetime import date, time
from typing import List, Tuple
from logger import setup_logger
from database import Database


class BlockedSlots:

    def __init__(self, db: Database):
        self.db = db
        self.logger = setup_logger(__name__)

    def block_day(self, block_date: date) -> bool:
        """Блокировать весь день."""
        try:
            self.db.execute_query(
                """
                    DELETE FROM BlockedSlots WHERE date = %s;
                """,
                block_date,
            )

            self.db.execute_query(
                """
                    INSERT INTO BlockedSlots (date, start_time, end_time)
                    VALUES (%s, '00:00:00', '23:59:59');
                """,
                block_date,
            )
            self.logger.debug(f"День {block_date.strftime('%d.%m.%Y')} заблокирован.")
            return True
        except:
            self.logger.debug(
                f"Ошибка при блокировке дня {block_date.strftime('%d.%m.%Y')}."
            )
            return False

    def block_time_slot(
        self, block_date: date, start_time: time, end_time: time
    ) -> bool:
        """Блокировать временной слот, объединяя при необходимости существующие слоты.

        Возвращает:
            True — если слот успешно заблокирован.
            False — если произошла ошибка.
        """
        try:
            existing_slots = self.db.execute_query(
                """
                    SELECT * FROM BlockedSlots 
                WHERE date = %s AND (
                    (start_time < %s AND end_time > %s) OR
                    (start_time < %s AND end_time > %s) OR
                    (start_time >= %s AND end_time <= %s)
                );
                """,
                block_date,
                end_time,
                end_time,
                start_time,
                start_time,
                start_time,
                end_time,
            )

            if existing_slots:
                new_start_time = min(
                    start_time, min(slot["start_time"] for slot in existing_slots)
                )
                new_end_time = max(
                    end_time, max(slot["end_time"] for slot in existing_slots)
                )

                for slot in existing_slots:
                    self.db.execute_query(
                        """
                            DELETE FROM BlockedSlots WHERE id = %s;
                        """,
                        slot["id"],
                    )

                self.db.execute_query(
                    """
                        INSERT INTO BlockedSlots (date, start_time, end_time)
                        VALUES (%s, %s, %s);
                    """,
                    block_date,
                    new_start_time,
                    new_end_time,
                )

                self.logger.debug(
                    f"Слот {block_date.strftime('%d.%m.%Y')} {new_start_time.strftime('%H:%M')} - {new_end_time.strftime('%H:%M')} заблокирован (объединено)."
                )
            else:
                self.db.execute_query(
                    """
                        INSERT INTO BlockedSlots (date, start_time, end_time)
                        VALUES (%s, %s, %s);
                    """,
                    block_date,
                    start_time,
                    end_time,
                )

                self.logger.debug(
                    f"Слот {block_date.strftime('%d.%m.%Y')} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} заблокирован (пересечений не было, новый слот)."
                )

            return True

        except Exception as e:
            # Логируем ошибку
            self.logger.error(
                f"Ошибка при блокировке слота {block_date.strftime('%d.%m.%Y')} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}: {e}"
            )
            return False

    def delete_blocked_slot(self, slot_id: int):
        """Удалить заблокированный слот."""

        slot = self.db.execute_query(
            """
                SELECT id FROM BlockedSlots WHERE id = %s;
            """,
            slot_id,
        )
        if not slot:
            self.logger.warning(f"Запись с id={slot_id} не найдена.")
            return

        self.db.execute_query(
            """
                DELETE FROM BlockedSlots WHERE id = %s;
            """,
            slot_id,
        )
        self.logger.debug(f"Запись с id={slot_id} удалена.")

    def get_blocked_slots(self, date: date) -> List[Tuple[date, time, time]]:
        """Получить все заблокированные слоты для даты."""
        query = """
            SELECT start_time, end_time 
            FROM BlockedSlots 
            WHERE date = %s 
            ORDER BY start_time;
        """
        blocked_intervals = self.db.fetch_data(query, date)
        return blocked_intervals

    def is_day_blocked(self, date_obj: date) -> bool:
        """Проверить, заблокирован ли день."""
        query = """
            SELECT start_time, end_time 
            FROM BlockedSlots 
            WHERE date = %s AND start_time = '00:00:00' AND end_time = '23:59:59';
        """
        blocked_slots = self.db.fetch_data(query, date_obj)
        return bool(blocked_slots)
