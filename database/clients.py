from logger import setup_logger
from database import Database
from typing import Optional, Tuple


class Clients:
    """Класс для работы с таблицей Clients (клиенты)."""

    def __init__(self, db: Database):
        self.db = db
        self.logger = setup_logger(__name__)

    def add_client(
        self,
        telephone: str,
        tg_id: Optional[str] = None,
        tg_first_name: Optional[str] = None,
        tg_username: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """Добавить или обновить клиента."""

        query = """
            INSERT INTO Clients (telephone, tg_id, tg_first_name, tg_username, name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (telephone) DO UPDATE
            SET
                tg_id = COALESCE(EXCLUDED.tg_id, Clients.tg_id),
                tg_first_name = COALESCE(EXCLUDED.tg_first_name, Clients.tg_first_name),
                tg_username = COALESCE(EXCLUDED.tg_username, Clients.tg_username),
                name = COALESCE(EXCLUDED.name, Clients.name)
        """

        self.db.execute_query(query, telephone, tg_id, tg_first_name, tg_username, name)
        self.logger.debug(f"Клиент с телефоном {telephone} добавлен или обновлен.")

    def get_client_by_telephone(self, telephone: str) -> Optional[Tuple]:
        """Получить данные о клиенте по его номеру телефона."""

        client = self.db.execute_query(
            "SELECT * FROM Clients WHERE telephone = %s", telephone
        )
        self.logger.debug(f"Клиент с телефоном {telephone} найден.")
        return client
