from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from src.controllers.EmailController import EmailController
from src.views.ComposeEmailDialog import ComposeEmailDialog


class EmailTab(QWidget):
    def __init__(self, email_controller: EmailController, main_window):
        super().__init__()
        self.controller = email_controller
        self.main_window = main_window
        self.is_message_box_open = False
        self.init_ui()
        self.auto_update_timer = QTimer()

        # Conectar señales del controlador con la interfaz
        self.controller.update_received_signal.connect(self.display_received_emails)
        self.controller.update_sent_signal.connect(self.display_sent_emails)
        self.controller.task_finished_signal.connect(self.on_task_finished)

        # Configurar la actualización automática
        self.auto_update_timer.timeout.connect(lambda: self.fetch_emails(manual=False))
        self.auto_update_timer.start(60000)

        # Mostrar correos almacenados al cargar la pestaña
        self.display_received_emails(self.controller.dao.fetch_received_emails())
        self.display_sent_emails(self.controller.dao.fetch_sent_emails())

    def init_ui(self):
        """Inicializa la interfaz gráfica de la pestaña."""
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Gestión de Correos")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Botones
        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Descargar Correos")
        self.send_button = QPushButton("Redactar Correo")
        self.fetch_button.clicked.connect(self.fetch_emails)
        self.send_button.clicked.connect(self.compose_email)

        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.send_button)
        layout.addLayout(button_layout)

        # Tabla de correos recibidos
        self.received_label = QLabel("Correos Recibidos:")
        layout.addWidget(self.received_label)
        self.received_table = QTableWidget(0, 2)
        self.received_table.setHorizontalHeaderLabels(["Remitente", "Asunto"])
        self.received_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.received_table.cellDoubleClicked.connect(self.view_received_email)
        layout.addWidget(self.received_table)

        # Tabla de correos enviados
        self.sent_label = QLabel("Correos Enviados:")
        layout.addWidget(self.sent_label)
        self.sent_table = QTableWidget(0, 2)
        self.sent_table.setHorizontalHeaderLabels(["Destinatario", "Asunto"])
        self.sent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sent_table.cellDoubleClicked.connect(self.view_sent_email)
        layout.addWidget(self.sent_table)

    def fetch_emails(self, manual=True):
        """Inicia la descarga de correos."""
        if not self.controller.task_manager.fetch_task.is_running():
            self.fetch_button.setEnabled(False)
            self.controller.fetch_email_async(manual=manual)

    def compose_email(self):
        """Abre un diálogo para redactar y enviar un correo."""
        dialog = ComposeEmailDialog(self.controller)
        dialog.exec()

    def display_received_emails(self, emails):
        """Actualiza la tabla de correos recibidos."""
        self.received_table.setRowCount(0)
        self.received_table.setColumnCount(4)
        self.received_table.setHorizontalHeaderLabels(["Remitente", "Asunto", "Leído", "Fecha / Hora"])
        for email in emails:
            row = self.received_table.rowCount()
            self.received_table.insertRow(row)
            self.received_table.setItem(row, 0, QTableWidgetItem(email.sender))
            self.received_table.setItem(row, 1, QTableWidgetItem(email.subject))
            self.received_table.setItem(row, 2, QTableWidgetItem("Sí" if email.read else "No"))
            self.received_table.setItem(row, 3, QTableWidgetItem(email.date))
        self.received_table.resizeColumnsToContents()

    def display_sent_emails(self, emails):
        """Actualiza la tabla de correos enviados."""
        self.sent_table.setRowCount(0)
        self.sent_table.setColumnCount(3)
        self.sent_table.setHorizontalHeaderLabels(["Remitente", "Asunto", "Fecha / Hora"])
        for email in emails:
            row = self.sent_table.rowCount()
            self.sent_table.insertRow(row)
            self.sent_table.setItem(row, 0, QTableWidgetItem(email.recipient))
            self.sent_table.setItem(row, 1, QTableWidgetItem(email.subject))
            self.sent_table.setItem(row, 2, QTableWidgetItem(email.date))
        self.sent_table.resizeColumnsToContents()

    def view_received_email(self, row, column):
        """Muestra el contenido de un correo recibido seleccionado."""
        email = self.controller.dao.fetch_received_emails()[row]
        self.controller.dao.mark_email_as_read(email.message_id)
        QMessageBox.information(
            self,
            f"Correo de {email.sender}",
            f"Asunto: {email.subject}\n\n{email.body}"
        )
        self.display_received_emails(self.controller.dao.fetch_received_emails())

    def view_sent_email(self, row, column):
        """Muestra el contenido de un correo enviado seleccionado."""
        email = self.controller.dao.fetch_sent_emails()[row]
        QMessageBox.information(
            self,
            f"Correo a {email.recipient}",
            f"Asunto: {email.subject}\n\n{email.body}"
        )

    def on_task_finished(self, task_name):
        """Maneja la finalización de tareas asincrónicas."""
        self.fetch_button.setEnabled(True)
        if task_name == "fetch_emails":
            self.display_received_emails(self.controller.dao.fetch_received_emails())
            QMessageBox.information(self, "Descarga Completa", "La descarga de correos ha finalizado.")
        elif task_name == "send_email":
            self.display_sent_emails(self.controller.dao.fetch_sent_emails())
            QMessageBox.information(self, "Envío Completo", "El correo ha sido enviado correctamente.")
        elif task_name == "fetch_emails_auto":
            self.display_received_emails(self.controller.dao.fetch_received_emails())
            # Mostrar mensaje en la barra de estado
            self.main_window.status_bar.showMessage("Descarga automática de correos completada.", 5000)
