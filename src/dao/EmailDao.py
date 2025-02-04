import sqlite3
from src.dao.utils.DatabaseConnection import DatabaseConnection
from src.entities.mail.ReceivedMail import ReceivedMail
from src.entities.mail.SentMail import SentMail


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
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read BOOLEAN DEFAULT 0
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

    def save_received_mail(self, email: ReceivedMail):
        """Guarda un correo recibido en la base de datos si no existe."""
        if not self.email_exists(email.message_id):
            insert_query = """
            INSERT INTO received_emails (sender, recipient, subject, body, message_id)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor = self.connection.cursor()
            try:
                cursor.execute(insert_query,
                               (email.sender, email.recipient, email.subject, email.body, email.message_id))
                self.connection.commit()
                print(f"[INFO] Correo recibido guardado: {email.subject}")
            except sqlite3.Error as e:
                print(f"[ERROR] Error al guardar el correo recibido: {e}")
            finally:
                cursor.close()

    def save_sent_mail(self, email: SentMail):
        """Guarda un correo enviado en la base de datos."""
        insert_query = """
        INSERT INTO sent_emails (sender, recipient, subject, body, attachment_path)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, (
                email.sender, email.recipient, email.subject, email.body, email.attachment_path
            ))
            self.connection.commit()
            print(f"[INFO] Correo enviado guardado: {email.subject}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error al guardar el correo enviado: {e}")
        finally:
            cursor.close()

    def fetch_received_emails(self):
        """Recupera todos los correos recibidos desde la base de datos."""
        select_query = """
        SELECT id, sender, recipient, subject, body, message_id, received_at, read 
        FROM received_emails 
        ORDER BY received_at DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                ReceivedMail(
                    id=row[0],
                    sender=row[1],
                    recipient=row[2],
                    subject=row[3],
                    body=row[4],
                    message_id=row[5],
                    received_at=row[6],
                    read=bool(row[7])
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar correos recibidos: {e}")
            return []
        finally:
            cursor.close()

    def fetch_sent_emails(self):
        """Recupera todos los correos enviados desde la base de datos."""
        select_query = """
        SELECT id, sender, recipient, subject, body, attachment_path, sent_at 
        FROM sent_emails 
        ORDER BY sent_at DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                SentMail(
                    id=row[0],
                    sender=row[1],
                    recipient=row[2],
                    subject=row[3],
                    body=row[4],
                    attachment_path=row[5],
                    sent_at=row[6]
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al recuperar correos enviados: {e}")
            return []
        finally:
            cursor.close()

    def mark_email_as_read(self, message_id):
        """Marcar un correo como leído en la base de datos"""
        query = "UPDATE received_emails SET read = 1 WHERE message_id = ?"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (message_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] Error al marcar correo como leido: {e}")
        finally:
            cursor.close()
