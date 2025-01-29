import sqlite3

from nbclient.client import timestamp

from src.dao.utils.DatabaseConnection import DatabaseConnection
from src.entities.chat import ChatMessage


class ChatDAO:
    def __init__(self):
        """Inicializa el DAO de chat y crea la tabla en la base de datos"""
        self.connection = DatabaseConnection().get_connection()
        self._create_table()

    def _create_table(self):
        """Crea la tabla para almacenar mensajes de chat si no existe"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(create_table_query)
            self.connection.commit()
            print("[DEBUG] La tabla se ha creado correctamente")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al crear la tabla de mensajes de chat: {e}")
        finally:
            cursor.close()

    def save_chat_message(self, chat_message: ChatMessage):
        """Guarda el mensaje del chat en la base de datos"""
        insert_query = """
        INSERT INTO chat_messages (sender, message, timestamp) VALUES (?,?,?);
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, (chat_message.sender, chat_message.message, chat_message.timestamp))
            self.connection.commit()
            print(f"[INFO] Mensaje guardado: {chat_message}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al guardar el mensaje: {e}")
        finally:
            cursor.close()

    def fetch_all_messages(self):
        """Recupera todos los mensajes de chat desde la base de datos"""
        select_query = """
        SELECT id, sender, message, timestamp FROM chat_messages ORDER BY timestamp ASC;
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                ChatMessage(
                    id=row["id"],
                    sender=row["sender"],
                    message=row["message"],
                    timestamp=row["timestamp"]
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar los mensajes: {e}")
            return []
        finally:
            cursor.close()
