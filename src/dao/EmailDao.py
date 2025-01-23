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
            message_id TEXT UNIQUE NOT NULL,
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

    def email_exists(self, message_id):
        """Verifica si un correo con un determinado `message_id` ya existe."""
        query = "SELECT COUNT(1) FROM received_emails WHERE message_id = ?;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (message_id,))
            return cursor.fetchone()[0] > 0
        except sqlite3.Error as e:
            print(f"[ERROR] Error al verificar el correo: {e}")
            return False
        finally:
            cursor.close()

    def save_email(self, sender, recipient, subject, body, message_id):
        """Guarda un correo recibido en la base de datos si no existe."""
        if not self.email_exists(message_id):
            insert_query = """
            INSERT INTO received_emails (sender, recipient, subject, body, message_id)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor = self.connection.cursor()
            try:
                cursor.execute(insert_query, (sender, recipient, subject, body, message_id))
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
        select_query = """
        SELECT sender, recipient, subject, body, received_at 
        FROM received_emails 
        ORDER BY received_at DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                {"sender": row[0], "recipient": row[1], "subject": row[2], "body": row[3], "received_at": row[4]}
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar los correos recibidos: {e}")
            return []
        finally:
            cursor.close()

    def fetch_sent_emails(self):
        """Recupera todos los correos enviados desde la base de datos."""
        select_query = """
        SELECT sender, recipient, subject, body, attachment_path, sent_at 
        FROM sent_emails 
        ORDER BY sent_at DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                {
                    "sender": row[0],
                    "recipient": row[1],
                    "subject": row[2],
                    "body": row[3],
                    "attachment_path": row[4],
                    "sent_at": row[5],
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar los correos enviados: {e}")
            return []
        finally:
            cursor.close()
