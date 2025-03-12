from psycopg2 import pool
import config
from logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """Класс для работы с базой данных."""

    def __init__(self):
        self.connection_pool = None

    def connect(self):
        """Установить соединение с базой данных и создать пул соединений."""

        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1, maxconn=10, **config.DB_CONFIG
            )
            logger.debug("Соединение с базой данных установлено.")
            self.create_tables()
        except Exception as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")
            raise

    def close(self):
        """Закрыть соединение с базой данных."""

        if self.connection_pool:
            self.connection_pool.closeall()
            logger.debug("Соединение с базой данных закрыто.")

    def create_tables(self):
        """Создать таблицы в базе данных."""

        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Clients (
                    id SERIAL PRIMARY KEY,
                    telephone TEXT NOT NULL,
                    tg_id INTEGER UNIQUE,
                    tg_first_name TEXT,
                    tg_username TEXT,
                    name TEXT
);
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Appointments (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES Clients(id) ON DELETE CASCADE,
                    procedure TEXT,
                    date DATE,
                    start_time TIME,
                    end_time TIME
                );
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS BlockedSlots (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        start_time TIME NOT NULL,
                        end_time TIME NOT NULL
                    )
                """
                )

            conn.commit()
            logger.debug(
                "Созданы (при необходимости) таблицы: Clients, Appointments, BlockedSlots."
            )

        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def fetch_data(self, query, *args):
        """Выполнить SELECT-запрос и вернуть результат."""

        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                result = cursor.fetchall()
                logger.debug(f"Запрос SELECT выполнен. Результат запроса: {result}")
                return result
        except Exception as e:
            logger.error(
                f"Ошибка при выполнении запроса: {e} \n Запрос: {query} \n Параметры: {args}"
            )
            return None
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def execute_query(self, query, *args):
        """Выполнить INSERT, UPDATE или DELETE запрос."""

        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                conn.commit()
                logger.debug("Запрос выполнен.")
        except Exception as e:
            logger.error(
                f"Ошибка при выполнении запроса: {e} \n Запрос: {query} \n Параметры: {args}"
            )
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.connection_pool.putconn(conn)
