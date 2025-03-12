from datetime import time, timedelta

MONTHS_LOOKAHEAD = 6
DAYS_LOOKAHEAD = timedelta(days=30)
STEP = timedelta(minutes=15)
MON_WED_FRI_START = time(9, 0)
MON_WED_FRI_END = time(16, 0)
TUE_THU_SAT_START = time(13, 30)
TUE_THU_SAT_END = time(20, 30)

PROCEDURES = {
    "Процедура 1": 180,
    "Процедура 2": 240,
    "Процедура 3": 90,
    "Процедура 4": 30,
    "Процедура 5": 15,
}
