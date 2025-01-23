from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt


class ComposeEmailDialog(QDialog):
    def __init__(self, email_controller):
        super().__init__()
        self.controller = email_controller
        self.setWindowTitle("Redactar Correo")
        self.setMinimumSize(500, 400)
        self.attachment_path = None
        self.init_ui()

    def init_ui(self):
        """Crea la interfaz gráfica para redactar correos."""
        layout = QVBoxLayout(self)

        # Campo de destinatario
        recipient_label = QLabel("Destinatario:")
        layout.addWidget(recipient_label)

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Introduce la dirección de correo del destinatario")
        layout.addWidget(self.recipient_input)

        # Campo de asunto
        subject_label = QLabel("Asunto:")
        layout.addWidget(subject_label)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Introduce el asunto del correo")
        layout.addWidget(self.subject_input)

        # Campo de cuerpo del correo
        body_label = QLabel("Mensaje:")
        layout.addWidget(body_label)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Escribe tu mensaje aquí...")
        layout.addWidget(self.body_input)

        # Botones para adjuntar archivos y enviar
        button_layout = QHBoxLayout()

        self.attach_button = QPushButton("Adjuntar Archivo")
        self.attach_button.clicked.connect(self.attach_file)
        button_layout.addWidget(self.attach_button)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_email)
        button_layout.addWidget(self.send_button)

        layout.addLayout(button_layout)

    def attach_file(self):
        """Abre un diálogo para seleccionar un archivo adjunto."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            self.attachment_path = file_dialog.selectedFiles()[0]
            QMessageBox.information(self, "Archivo Adjunto", f"Archivo seleccionado: {self.attachment_path}")

    def send_email(self):
        """Envía el correo utilizando el controlador."""
        recipient = self.recipient_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()

        if not recipient or not subject or not body:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos antes de enviar.")
            return

        self.controller.send_email_async(recipient, subject, body, self.attachment_path)
        QMessageBox.information(self, "Envío en Proceso", "El correo se está enviando.")
        self.close()
