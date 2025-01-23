from src.services.ThreadenTask import ThreadenTask


class EmailTaskManager:
    def __init__(self, controller):
        self.controller = controller
        self.fetch_task = ThreadenTask()
        self.send_task = ThreadenTask()

    def start_fetch(self):
        """Inicia la tarea para obtener correos."""
        if not self.fetch_task.is_running():
            self.fetch_task.start(self.controller._fetch_emails)
        else:
            print("[INFO] Tarea de obtención ya está en ejecución.")

    def start_send(self, recipient, subject, body, attachment_path):
        """Inicia la tarea para enviar un correo."""
        if not self.send_task.is_running():
            self.send_task.start(self.controller._send_email, recipient, subject, body, attachment_path)
        else:
            print("[INFO] Tarea de envío ya está en ejecución.")

    def stop_all_tasks(self):
        """Detiene todas las tareas activas."""
        if self.fetch_task.is_running():
            self.fetch_task.stop()
        if self.send_task.is_running():
            self.send_task.stop()
