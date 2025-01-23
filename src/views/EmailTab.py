from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QMessageBox, QFileDialog,
    QListWidgetItem
)
from PySide6.QtCore import Qt
from src.controllers.EmailController import EmailController
from src.views.ComposeEmailDialog import ComposeEmailDialog


class EmailTab(QWidget):
    def __init__(self, email_controller: EmailController):
        super().__init__()
        self.controller = email_controller
        self.init_ui()

        # Conectar señales del controlador con la interfaz
        self.controller.update_received_signal.connect(self.display_received_emails)
        self.controller.update_sent_signal.connect(self.display_sent_emails)
        self.controller.task_finished_signal.connect(self.on_task_finished)

    def init_ui(self):
        """Crea la interfaz gráfica para gestionar correos electrónicos."""
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Gestión de Correos")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Panel para los botones de acción
        button_layout = QHBoxLayout()

        self.fetch_button = QPushButton("Descargar Correos")
        self.send_button = QPushButton("Redactar Correo")
        self.fetch_button.clicked.connect(self.fetch_emails)
        self.send_button.clicked.connect(self.compose_email)

        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.send_button)
        layout.addLayout(button_layout)

        # Panel para mostrar los correos recibidos
        self.received_label = QLabel("Correos Recibidos:")
        self.received_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.received_label)

        self.received_list = QListWidget()
        self.received_list.itemClicked.connect(self.view_received_email)
        layout.addWidget(self.received_list)

        # Panel para mostrar los correos enviados
        self.sent_label = QLabel("Correos Enviados:")
        self.sent_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.sent_label)

        self.sent_list = QListWidget()
        self.sent_list.itemClicked.connect(self.view_sent_email)
        layout.addWidget(self.sent_list)

    def fetch_emails(self):
        """Inicia la tarea para descargar correos."""
        self.controller.fetch_email_async()
        QMessageBox.information(self, "Descarga en Proceso", "Se está descargando la lista de correos.")

    def compose_email(self):
        """Abre un diálogo para redactar y enviar un correo."""
        dialog = ComposeEmailDialog(self.controller)
        dialog.exec()

    def view_received_email(self, item):
        """Muestra el contenido de un correo recibido seleccionado."""
        email_data = item.data(Qt.UserRole)
        QMessageBox.information(
            self,
            f"Correo de {email_data['sender']}",
            f"Asunto: {email_data['subject']}\n\n{email_data['body']}"
        )

    def view_sent_email(self, item):
        """Muestra el contenido de un correo enviado seleccionado."""
        email_data = item.data(Qt.UserRole)
        QMessageBox.information(
            self,
            f"Correo a {email_data['recipient']}",
            f"Asunto: {email_data['subject']}\n\n{email_data['body']}"
        )

    def display_received_emails(self, emails):
        """Actualiza la lista de correos recibidos en la interfaz."""
        self.received_list.clear()
        for email in emails:
            item = QListWidgetItem(email["subject"])
            item.setData(Qt.UserRole, email)
            self.received_list.addItem(item)

    def display_sent_emails(self, emails):
        """Actualiza la lista de correos enviados en la interfaz."""
        self.sent_list.clear()
        for email in emails:
            item = QListWidgetItem(email["subject"])
            item.setData(Qt.UserRole, email)
            self.sent_list.addItem(item)

    def on_task_finished(self, task_name):
        """Maneja la finalización de tareas."""
        if task_name == "fetch_emails":
            QMessageBox.information(self, "Descarga Completa", "La descarga de correos ha finalizado.")
        elif task_name == "send_email":
            QMessageBox.information(self, "Envío Completo", "El correo ha sido enviado correctamente.")