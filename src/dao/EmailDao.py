import sqlite3

from src.dao.utils.DatabaseConnection import DatabaseConnection


class EmailDao:
    def __init__(self):
        """Inicializa el DAO de correos electrónicos y crea las tablas necesarias."""
        self.connection = DatabaseConnection().get_connection()
        self._create_tables()

    def _create_tables(self):
        """Crea las tablas necesarias para almacenar correos electrónicos si no existen."""
        create_received_table_query = """
        CREATE TABLE IF NOT EXISTS received_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        create_sent_table_query = """
        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            attachment_path TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(create_received_table_query)
            cursor.execute(create_sent_table_query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] Error al crear las tablas: {e}")
        finally:
            cursor.close()

    def save_email(self, sender, recipient, subject, body):
        """Guarda un correo recibido en la base de datos."""
        insert_query = """
        INSERT INTO received_emails (sender, recipient, subject, body)
        VALUES (?, ?, ?, ?);
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, (sender, recipient, subject, body))
            self.connection.commit()
            print(f"[INFO] Correo recibido guardado: {subject}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al guardar el correo recibido: {e}")
        finally:
            cursor.close()

    def save_sent_email(self, sender, recipient, subject, body, attachment_path=None):
        """Guarda un correo enviado en la base de datos."""
        insert_query = """
        INSERT INTO sent_emails (sender, recipient, subject, body, attachment_path)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, (sender, recipient, subject, body, attachment_path))
            self.connection.commit()
            print(f"[INFO] Correo enviado guardado: {subject}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al guardar el correo enviado: {e}")
        finally:
            cursor.close()

    def fetch_received_emails(self):
        """Recupera todos los correos recibidos desde la base de datos."""
        select_query = "SELECT * FROM received_emails ORDER BY received_at DESC;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar los correos recibidos: {e}")
            return []
        finally:
            cursor.close()

    def fetch_sent_emails(self):
        """Recupera todos los correos enviados desde la base de datos."""
        select_query = "SELECT * FROM sent_emails ORDER BY sent_at DESC;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar los correos enviados: {e}")
            return []
        finally:
            cursor.close()

    def delete_received_email(self, email_id):
        """Elimina un correo recibido de la base de datos."""
        delete_query = "DELETE FROM received_emails WHERE id = ?;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(delete_query, (email_id,))
            self.connection.commit()
            print(f"[INFO] Correo recibido eliminado: ID {email_id}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al eliminar el correo recibido: {e}")
        finally:
            cursor.close()

    def delete_sent_email(self, email_id):
        """Elimina un correo enviado de la base de datos."""
        delete_query = "DELETE FROM sent_emails WHERE id = ?;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(delete_query, (email_id,))
            self.connection.commit()
            print(f"[INFO] Correo enviado eliminado: ID {email_id}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al eliminar el correo enviado: {e}")
        finally:
            cursor.close()
