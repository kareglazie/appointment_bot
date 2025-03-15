from logger import setup_logger
from database import Database
from typing import List, Optional, Tuple


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

    def get_client_by_telephone(self, telephone: str) -> Optional[List[Tuple]]:
        """Получить данные о клиенте по его номеру телефона."""
        query = "SELECT * FROM Clients WHERE telephone = %s"
        clients = self.db.fetch_data(query, telephone)
        if clients:
            self.logger.debug(
                f"Найдено клиентов с телефоном {telephone}: {len(clients)}"
            )
            return clients
        else:
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return None

    def get_client_by_id(self, id: int) -> Optional[List[Tuple]]:
        """Получить данные о клиенте по его ID."""
        query = "SELECT id, name, telephone, tg_username FROM Clients WHERE id = %s"
        clients = self.db.fetch_data(query, id)
        if clients:
            self.logger.debug(f"Найдено клиентов с ID {id}: {len(clients)}")
            return clients
        else:
            self.logger.debug(f"Клиент с ID {id} не найден.")
            return None

    def get_client_id_by_telephone(self, telephone: str) -> Optional[int]:
        """Получить ID клиента по его номеру телефона."""
        query = "SELECT id FROM Clients WHERE telephone = %s"
        client_ids = self.db.fetch_data(query, telephone)
        if client_ids:
            if len(client_ids) > 1:
                self.logger.warning(
                    f"Найдено несколько клиентов с телефоном {telephone}. "
                    "Используйте tg_id для однозначной идентификации."
                )
            return client_ids[0][0]  # Возвращаем ID первого клиента
        else:
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return None

    def get_client_id_by_tg_id(self, tg_id: int) -> Optional[int]:
        """Получить ID клиента по его tg_id."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return None

        client_id = self.db.fetch_data("SELECT id FROM Clients WHERE tg_id = %s", tg_id)
        return client_id[0][0] if client_id else None

    def update_client_phone_by_phone(self, old_telephone: str, new_telephone: str):
        """Обновить телефон клиента (получение данных по номеру телефона)."""
        query = "SELECT id FROM Clients WHERE telephone = %s"
        client_ids = self.db.fetch_data(query, old_telephone)

        if not client_ids:
            self.logger.debug(f"Клиент с телефоном {old_telephone} не найден.")
            return
        elif len(client_ids) > 1:
            self.logger.warning(
                f"Найдено несколько клиентов с телефоном {old_telephone}. "
                "Обновление телефона не выполнено."
            )
            return

    def update_client_phone_by_tg_id(self, tg_id: int, new_telephone: str):
        """Обновить телефон клиента (получение данных по tg id)."""
        if not self.client_is_registered_by_tg_id(tg_id):
            self.logger.debug(f"Клиент с tg_id {tg_id} не найден.")
            return

        query = "UPDATE Clients SET telephone = %s WHERE tg_id = %s"
        self.db.execute_query(query, new_telephone, tg_id)
        self.logger.debug(
            f"Телефон клиента с tg id {tg_id} изменен на {new_telephone}."
        )

    def update_client_name_by_phone(self, telephone: str, new_name: str):
        """Обновить имя клиента (получение данных по номеру телефона)."""
        query = "SELECT id FROM Clients WHERE telephone = %s"
        client_ids = self.db.fetch_data(query, telephone)

        if not client_ids:
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return
        elif len(client_ids) > 1:
            self.logger.warning(
                f"Найдено несколько клиентов с телефоном {telephone}. "
                "Обновление имени не выполнено."
            )
            return

        # Обновляем имя для одного клиента
        query = "UPDATE Clients SET name = %s WHERE id = %s"
        self.db.execute_query(query, new_name, client_ids[0][0])
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
        query = "SELECT name FROM Clients WHERE telephone = %s"
        clients = self.db.fetch_data(query, telephone)
        if clients:
            if len(clients) > 1:
                self.logger.warning(
                    f"Найдено несколько клиентов с телефоном {telephone}. "
                    "Используйте tg_id для однозначной идентификации."
                )
            return clients[0][0]  # Возвращаем имя первого клиента
        else:
            self.logger.debug(f"Клиент с телефоном {telephone} не найден.")
            return None

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

    def get_client_name_by_id(self, id: int) -> Optional[str]:
        """Получить имя клиента по его ID."""
        query = "SELECT name FROM Clients WHERE id = %s"
        client = self.db.fetch_data(query, id)
        if client:
            return client[0]
        else:
            self.logger.debug(f"Клиент с ID {id} не найден.")
            return None

    def get_client_phone_by_id(self, id: int) -> Optional[str]:
        """Получить телефон клиента по его ID."""
        query = "SELECT telephone FROM Clients WHERE id = %s"
        client = self.db.fetch_data(query, id)
        if client:
            return client[0]
        else:
            self.logger.debug(f"Клиент с ID {id} не найден.")
            return None
