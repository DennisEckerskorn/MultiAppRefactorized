from PySide6.QtCore import QObject, Signal
import poplib
import smtplib
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default
from src.dao.EmailDao import EmailDao
from src.entities.mail.ReceivedMail import ReceivedMail
from src.entities.mail.SentMail import SentMail
from src.managers.EmailTaskManager import EmailTaskManager


class EmailController(QObject):
    update_received_signal = Signal(list)
    update_sent_signal = Signal(list)
    task_finished_signal = Signal(str)

    def __init__(self, pop_server, smtp_server, email, password, pop_port=110, smtp_port=25):
        super().__init__()
        self.pop_server = pop_server
        self.smtp_server = smtp_server
        self.email = email
        self.password = password
        self.pop_port = pop_port
        self.smtp_port = smtp_port
        self.dao = EmailDao()

        # Inicializa el administrador de tareas
        self.task_manager = EmailTaskManager(self)

    def fetch_email_async(self):
        """Inicia la descarga de correos en un hilo."""
        if not self.task_manager.fetch_task.is_running():
            self.task_manager.start_fetch()
        else:
            print("[INFO] La tarea de descarga ya está en ejecución.")

    def send_email_async(self, recipient, subject, body, attachment_path=None):
        """Envía correos en un hilo separado."""
        if not self.task_manager.send_task.is_running():
            self.task_manager.send_task.start(self._send_email, recipient, subject, body, attachment_path)
        else:
            print("[INFO] La tarea de envío de correos ya está en ejecución.")

    def _fetch_emails(self):
        """Lógica de obtención de correos."""
        try:
            # Usar POP3_SSL si el servidor requiere SSL
            if self.pop_port == 995:
                pop_conn = poplib.POP3_SSL(self.pop_server, self.pop_port)
            else:
                pop_conn = poplib.POP3(self.pop_server, self.pop_port)

            # Habilitar depuración para ver los comandos enviados y las respuestas del servidor
            pop_conn.set_debuglevel(2)

            # Autenticación
            pop_conn.user(self.email)
            pop_conn.pass_(self.password)

            print("[INFO] Conexión POP3 establecida.")

            # Intentar recuperar correos directamente con RETR
            i = 1
            while True:
                try:
                    # Recuperar el correo con RETR
                    response, lines, octets = pop_conn.retr(i)
                    message = BytesParser(policy=default).parsebytes(b"\n".join(lines))

                    # Crear objeto ReceivedMail
                    email = ReceivedMail(
                        sender=message["From"],
                        recipient=self.email,
                        subject=message["Subject"],
                        body=message.get_body(preferencelist=("plain",)).get_content(),
                        message_id=message["Message-ID"]
                    )

                    # Guardar el correo en la base de datos si no existe
                    if not self.dao.email_exists(email.message_id):
                        self.dao.save_received_mail(email)
                        print(f"[INFO] Correo nuevo guardado: {email.subject}")
                    else:
                        print(f"[INFO] Correo ya existente: {email.subject}")

                    i += 1  # Incrementar el índice para el siguiente correo
                except poplib.error_proto as e:
                    # Si el servidor devuelve un error, asumimos que no hay más correos
                    print(f"[INFO] No hay más correos para recuperar: {e}")
                    break

            pop_conn.quit()

            # Emitir señal para actualizar la UI
            self.update_received_signal.emit(self.dao.fetch_received_emails())
        except Exception as e:
            print(f"[ERROR] Error al recibir correos: {e}")
        finally:
            # Detener la tarea de descarga y emitir señal de finalización
            self.task_manager.fetch_task.stop()
            self.task_finished_signal.emit("fetch_emails")

    def _send_email(self, recipient, subject, body, attachment_path=None):
        """Lógica para enviar un correo usando SMTP."""
        try:
            msg = EmailMessage()
            msg["From"] = self.email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(body)

            if attachment_path:
                with open(attachment_path, "rb") as f:
                    file_data = f.read()
                    file_name = attachment_path.split("/")[-1]
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.email, self.password)
                smtp.send_message(msg)

            email = SentMail(
                sender=self.email,
                recipient=recipient,
                subject=subject,
                body=body,
                attachment_path=attachment_path
            )

            # Guardar en la base de datos
            self.dao.save_sent_mail(email)

            # Emitir señal para actualizar la UI
            self.update_sent_signal.emit(self.dao.fetch_sent_emails())
        except Exception as e:
            print(f"[ERROR] Error al enviar correo: {e}")
        finally:
            self.task_manager.send_task.stop()
            self.task_finished_signal.emit("send_email")
