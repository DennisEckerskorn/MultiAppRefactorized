import sqlite3
from queue import Queue

from src.dao.utils.DatabaseConnection import DatabaseConnection
from src.services.ThreadenTask import ThreadenTask


class ScrappingDAO:
    def __init__(self):
        self.connection = DatabaseConnection().get_connection()
        self._create_table()
        self.task_queue = Queue()
        self.insertion_task = ThreadenTask()

    def _create_table(self):
        """Crea la tabla para la inserción de los enlaces si no existe"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scraped_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            parent_url TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(create_table_query)
        self.connection.commit()

    def insert_link(self, url, parent_url):
        """Inserta enlaces en la base de datos"""
        insert_query = """
        INSERT INTO scraped_links(url, parent_url) VALUES (?, ?);
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, (url, parent_url))
            self.connection.commit()
            print(f"[INFO] Enlace insertado: {url}, Parent: {parent_url}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al insertar el enlace en la base de datos: {e}")
        finally:
            cursor.close()

    def insert_link_async(self, url, parent_url):
        """Coloca una tarea de insercion en la cola"""
        self.task_queue.put((url, parent_url))

    def start_insertion_task(self):
        """Inicia el hilo para procesar tareas de inserción"""
        if not self.insertion_task.is_running():
            self.insertion_task.start(self._process_insertions)
            print("[INFO] Tarea de inserción iniciada")

    def stop_insertion_task(self):
        """Detiene el hilo de inserción."""
        if self.insertion_task.is_running():
            self.insertion_task.stop()
            self.task_queue.put(None)
            print("[INFO] Tarea de inserción detenida")

    def _process_insertions(self):
        """Procesa las tareas de inserción en la cola"""
        while self.insertion_task.is_running():
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                url, parent_url = task
                self.insert_link(url, parent_url)
            except Exception as e:
                print(f"[ERROR] Error al procesar la inserción: {e}")
