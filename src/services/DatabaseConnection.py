import os
import sqlite3
from threading import Lock


class DatabaseConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_path="resources/db/database.db"):
        """Implementación del patrón Singleton para gestionar la conexión."""
        with cls._lock:
            if cls._instance is None:
                # Asegúrate de que el directorio existe
                directory = os.path.dirname(db_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    print(f"Directorio creado: {directory}")

                # Crear la instancia de conexión
                cls._instance = super().__new__(cls)
                cls._instance._connection = sqlite3.connect(db_path, check_same_thread=False)
                cls._instance._connection.row_factory = sqlite3.Row
            return cls._instance

    def get_connection(self):
        """Devuelve la conexión activa."""
        return self._connection

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        if self._connection:
            self._connection.close()
            DatabaseConnection._instance = None
