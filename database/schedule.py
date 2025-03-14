from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple
import config
from consts.constants import *
from database import Database
from logger import setup_logger
from database.blocked_slots import BlockedSlots


class Schedule:

    def __init__(
        self,
        db: Database,
        blocked_slots: BlockedSlots,
    ):
        self.db = db
        self.blocked_slots = blocked_slots
        self.logger = setup_logger(__name__)

    def get_working_hours(self, date_obj: date) -> Optional[Tuple[time, time]]:
        """Получить рабочие часы для даты."""

        if self.blocked_slots.is_day_blocked(date_obj):
            self.logger.debug(f"День {date_obj} полностью заблокирован.")
            return None

        if date_obj.weekday() == 6:
            self.logger.debug(f"{date_obj} — выходной день (воскресенье).")
            return None

        if date_obj.weekday() in [0, 2, 4]:
            base_start_time = MON_WED_FRI_START
            base_end_time = MON_WED_FRI_END
        elif date_obj.weekday() in [1, 3, 5]:
            base_start_time = TUE_THU_SAT_START
            base_end_time = TUE_THU_SAT_END
        else:
            self.logger.warning(f"Не удалось определить рабочие часы для {date_obj}.")
            return None

        blocked_intervals = self.blocked_slots.get_blocked_slots(date_obj)

        if not blocked_intervals:
            self.logger.debug(
                f"Рабочие часы для {date_obj}: {base_start_time} - {base_end_time}"
            )
            return (base_start_time, base_end_time)

        start_time = base_start_time
        end_time = base_end_time

        for block_start, block_end in blocked_intervals:
            if block_start <= start_time and block_end >= end_time:
                self.logger.debug(
                    f"Рабочие часы для {date_obj} полностью заблокированы: {block_start} - {block_end}"
                )
                return None

            if block_start <= start_time < block_end:
                start_time = block_end
            elif block_start < end_time <= block_end:
                end_time = block_start

        if start_time >= end_time:
            self.logger.debug(
                f"Рабочие часы для {date_obj} стали некорректными после блокировок."
            )
            return None

        self.logger.debug(
            f"Рабочие часы для {date_obj} с учетом блокировок: {start_time} - {end_time}"
        )
        return (start_time, end_time)

    def get_available_dates(
        self,
        procedure: Optional[str] = None,
        target_month: Optional[Tuple[int, int]] = None,
    ) -> List[date]:
        """Получить список доступных дат, исключая воскресенья.

        Если указан target_month, возвращает доступные даты только для этого месяца,
        если месяц не указан, возвращает даты на ближайшее количество дней по умолчанию (DAYS_LOOKAHEAD).

        Если не указана процедура, возвращает доступные даты, где есть хотя бы один слот любого размера,
        если процедура указана, возвращаются только те даты, где есть слоты для этой процедуры.
        """

        today = datetime.now().date()
        available_dates = []

        if target_month:
            year, month = target_month
            first_day_of_month = date(year, month, 1)
            last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(
                day=1
            ) - timedelta(days=1)
            start_date = max(today + timedelta(days=1), first_day_of_month)
            end_date = last_day_of_month
        else:
            start_date = today
            end_date = today + DAYS_LOOKAHEAD

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            working_hours = self.get_working_hours(current_date)
            if not working_hours:
                current_date += timedelta(days=1)
                continue

            if procedure is None:
                available_dates.append(current_date)
                current_date += timedelta(days=1)
                continue

            time_slots = self.get_available_time_slots(current_date, procedure)
            if time_slots:
                available_dates.append(current_date)

            current_date += timedelta(days=1)

        return available_dates

    def get_available_time_slots(
        self, date: date, procedure: Optional[str] = None
    ) -> List[Tuple[time, time]]:
        """Получить доступные слоты для даты.

        Если указана процедура, возвращается список слотов для этой процедуры,
        если процедура не указана, возвращается список всех доступных слотов."""

        working_hours = self.get_working_hours(date)
        if not working_hours:
            return []

        work_start, work_end = working_hours

        occupied = self._get_occupied_slots(date)
        self.logger.debug(f"Найдено занятых слотов для даты {date}: {len(occupied)}")

        work_start_dt = datetime.combine(date, work_start)
        work_end_dt = datetime.combine(date, work_end)

        free_intervals = self._calculate_free_intervals(
            work_start_dt, work_end_dt, occupied
        )
        self.logger.debug(f"Свободные интервалы для даты {date}: {free_intervals}")

        if procedure:
            duration = PROCEDURES.get(procedure)
            if not duration:
                return []
            duration_timedelta = timedelta(minutes=duration)
            return self._generate_procedure_slots(free_intervals, duration_timedelta)

        return self._convert_to_time(free_intervals)

    def _calculate_free_intervals(
        self,
        work_start: datetime,
        work_end: datetime,
        occupied: List[Tuple[datetime, datetime]],
    ) -> List[Tuple[datetime, datetime]]:
        """Вычислить свободные интервалы в переданном диапазоне. Если занятых слотов нет, возвращается весь диапазон."""

        if not occupied:
            return [(work_start, work_end)]

        free_intervals = []
        prev_end = work_start

        for start, end in sorted(occupied, key=lambda x: x[0]):
            if start > prev_end:
                free_intervals.append((prev_end, start))
            prev_end = max(prev_end, end)

        if prev_end < work_end:
            free_intervals.append((prev_end, work_end))

        self.logger.debug(f"Свободные интервалы для даты {date}: {free_intervals}")
        return free_intervals

    def _get_occupied_slots(self, date_obj: date) -> List[Tuple[datetime, datetime]]:
        """Получить занятые слоты для даты."""

        result = self.db.fetch_data(
            """
            SELECT start_time, end_time 
            FROM BlockedSlots 
            WHERE date = %s
            UNION ALL
            SELECT start_time, end_time 
            FROM Appointments 
            WHERE date = %s
            ORDER BY start_time;
            """,
            date_obj,
            date_obj,
        )

        self.logger.debug(f"Найдено занятых слотов для даты {date_obj}: {result}")

        if not result:
            return []

        return [
            (self._safe_combine(date_obj, start), self._safe_combine(date_obj, end))
            for start, end in result
            if start and end
        ]

    def _has_available_slot(self, date_obj: date, duration: timedelta) -> bool:
        """Проверить наличие доступного слота для процедуры."""

        try:
            time_slots = self.get_available_time_slots(date_obj)
            for start_time, end_time in time_slots:
                start_dt = self._safe_combine(date_obj, start_time)
                end_dt = self._safe_combine(date_obj, end_time)

                if not start_dt or not end_dt:
                    continue

                if (end_dt - start_dt) >= duration:
                    return True
            return False

        except Exception as e:
            self.logger.error(
                f"Ошибка при проверке доступности для даты {date_obj}: {e}"
            )
            return False

    @staticmethod
    def _generate_procedure_slots(
        free_intervals: List[Tuple[datetime, datetime]], duration: timedelta
    ) -> List[Tuple[time, time]]:
        """Сгенерировать слоты определенной длительности.
        Возвращает список кортежей с временными интервалами.
        Начало интервала - с шагом по умолчанию (STEP)."""

        if not free_intervals or not isinstance(duration, timedelta):
            return []

        slots = []

        for interval_start, interval_end in free_intervals:
            if not isinstance(interval_start, datetime) or not isinstance(
                interval_end, datetime
            ):
                continue

            current = interval_start
            while current + duration <= interval_end:
                slots.append((current.time(), (current + duration).time()))
                current += STEP

        return sorted(list({tuple(slot) for slot in slots}), key=lambda x: x[0])

    @staticmethod
    def _safe_combine(date_obj: date, time_obj: time) -> Optional[datetime]:
        """Безопасное объединение date и time."""

        try:
            return datetime.combine(date_obj, time_obj)
        except (TypeError, ValueError) as e:
            return None

    @staticmethod
    def _convert_to_time(
        intervals: List[Tuple[datetime, datetime]],
    ) -> List[Tuple[time, time]]:
        """Конвертация с проверкой типов."""

        return [
            (start.time(), end.time())
            for start, end in intervals
            if isinstance(start, datetime) and isinstance(end, datetime)
        ]
