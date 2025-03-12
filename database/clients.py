from logger import setup_logger
from database import Database
from typing import Optional, Tuple


class Clients:

    def __init__(self, db: Database):
        self.db = db
        self.logger = setup_logger(__name__)

    def add_client(
        self,
        tg_id: int,
        telephone: str,
        tg_first_name: Optional[str] = None,
        tg_username: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Добавить или обновить клиента."""
        query = """
            INSERT INTO Clients (telephone, tg_id, tg_first_name, tg_username, name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (tg_id) DO UPDATE
            SET
                telephone = EXCLUDED.telephone,
                tg_first_name = EXCLUDED.tg_first_name,
                tg_username = EXCLUDED.tg_username,
                name = EXCLUDED.name
        """

        try:
            self.db.execute_query(
                query, telephone, tg_id, tg_first_name, tg_username, name
            )
            self.logger.debug(f"Клиент с tg_id {tg_id} добавлен или обновлен.")
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении клиента: {e}")

    def get_client_by_telephone(self, telephone: str) -> Optional[Tuple]:
        """Получить данные о клиенте по его номеру телефона."""
        if not self.client_is_registered_by_phone(telephone):
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return None

        client = self.db.fetch_data(
            "SELECT * FROM Clients WHERE telephone = %s", telephone
        )
        return client[0] if client else None

    def get_client_id_by_telephone(self, telephone: str) -> Optional[int]:
        """Получить ID клиента по его номеру телефона."""
        if not self.client_is_registered_by_phone(telephone):
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return None

        client_id = self.db.fetch_data(
            "SELECT id FROM Clients WHERE telephone = %s", telephone
        )
        return client_id[0][0] if client_id else None

    def get_client_id_by_tg_id(self, tg_id: int) -> Optional[int]:
        """Получить ID клиента по его tg_id."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return None

        client_id = self.db.fetch_data("SELECT id FROM Clients WHERE tg_id = %s", tg_id)
        return client_id[0][0] if client_id else None

    def update_client_phone_by_phone(self, old_telephone: str, new_telephone: str):
        """Обновить телефон клиента (получение данных по номеру телефона)."""
        if not self.client_is_registered_by_phone(old_telephone):
            self.logger.debug(f"Клиент с телефоном {old_telephone} не найден.")
            return

        query = "UPDATE Clients SET telephone = %s WHERE telephone = %s"
        self.db.execute_query(query, new_telephone, old_telephone)
        self.logger.debug(
            f"Телефон клиента изменен с {old_telephone} на {new_telephone}."
        )

    def update_client_phone_by_tg_id(self, tg_id: int, new_telephone: str):
        """Обновить телефон клиента (получение данных по tg id)."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return

        query = "UPDATE Clients SET telephone = %s WHERE tg_id= %s"
        self.db.execute_query(query, new_telephone, tg_id)
        self.logger.debug(
            f"Телефон клиента с tg id {tg_id} изменен на {new_telephone}."
        )

    def update_client_name_by_phone(self, telephone: str, new_name: str):
        """Обновить имя клиента (получение данных по номеру телефона)."""
        if not self.client_is_registered_by_phone(telephone):
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return

        query = "UPDATE Clients SET name = %s WHERE telephone = %s"
        self.db.execute_query(query, new_name, telephone)
        self.logger.debug(
            f"Имя клиента с телефоном {telephone} изменено на {new_name}."
        )

    def update_client_name_by_tg_id(self, tg_id: int, new_name: str):
        """Обновить имя клиента (получение данных по tg_id)."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return

        query = "UPDATE Clients SET name = %s WHERE tg_id = %s"
        self.db.execute_query(query, new_name, tg_id)
        self.logger.debug(f"Имя клиента с tg id {tg_id} изменено на {new_name}.")

    def get_client_name_by_tg_id(self, tg_id: int) -> Optional[str]:
        """Получить имя клиента по его tg_id."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return None
        client = self.db.fetch_data("SELECT name FROM Clients WHERE tg_id = %s", tg_id)

        self.logger.debug(f"Имя клиента с tg_id {tg_id}: {client[0][0]}.")
        return client[0][0]

    def get_client_phone_by_tg_id(self, tg_id: int) -> str:
        """Получить телефон клиента по его tg_id."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return None
        phone = self.db.fetch_data(
            "SELECT telephone FROM Clients WHERE tg_id = %s", tg_id
        )
        self.logger.debug(f"Телефон клиента с tg_id {tg_id}: {phone[0][0]}.")
        return phone[0][0]

    def get_client_name_by_telephone(self, telephone: str) -> Optional[str]:
        """Получить имя клиента по его телефону."""
        if not self.client_is_registered(telephone):
            return None

        client = self.db.fetch_data(
            "SELECT name FROM Clients WHERE telephone = %s", telephone
        )
        return client[0][0] if client else None

    # def update_client_data(
    #     self, id: int, telephone: Optional[str] = None, tg_id: Optional[str] = None, tg_first_name: Optional[str] = None, tg_username: Optional[str] = None
    # ):
    #     """Обновить tg_id, tg_first_name и tg_username клиента."""
    #     if not self.client_is_registered_by_phone(telephone):
    #         return

    #     query = "UPDATE Clients SET tg_id = %s, tg_first_name = %s, tg_username = %s, telephone = %s WHERE id = %s"
    #     self.db.execute_query(query, tg_id, tg_first_name, tg_username, telephone, id)
    #     self.logger.debug(
    #         f"tg_id, tg_first_name и tg_username клиента с телефоном {telephone} изменены на {tg_id}, {tg_first_name} и {tg_username}."
    #     )

    def client_is_registered_by_phone(self, telephone: str) -> bool:
        """Проверить, существует ли в базе данных клиент с таким телефоном."""
        query = "SELECT EXISTS(SELECT 1 FROM Clients WHERE telephone = %s)"
        result = self.db.fetch_data(query, telephone)
        if result and result[0][0]:
            return True
        else:
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return False

    def client_is_registered_by_tg_id(self, tg_id: int) -> bool:
        """Проверить, существует ли в базе данных клиент с таким tg_id."""
        query = "SELECT EXISTS(SELECT 1 FROM Clients WHERE tg_id = %s)"
        result = self.db.fetch_data(query, tg_id)
        if result and result[0][0]:
            return True
        else:
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return False
