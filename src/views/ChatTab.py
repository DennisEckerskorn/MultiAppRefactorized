from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt
from src.controllers.ChatController import ChatController


class ChatTab(QWidget):
    def __init__(self, chat_controller: ChatController):
        super().__init__()
        self.controller = chat_controller
        self.init_ui()

        # Conectar señales del controlador con la interfaz
        self.controller.message_received_signal.connect(self.display_message)
        self.controller.messages_loaded_signal.connect(self.load_message)
        self.controller.connection_status_signal.connect(self.update_connection_status)

        # Cargar los mensajes al principio
        self.controller.load_messages()

    def init_ui(self):
        """Crea la interfaz gráfica del chat"""
        layout = QVBoxLayout(self)

        # Titulo
        title_label = QLabel("Chat en Vivo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Área de mensajes
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Campo de entrada de mensajes
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe tu mensaje aqui...")
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Estado de conexión

        self.connection_status = QLabel("Estado: Desconectado")
        self.connection_status.setAlignment(Qt.AlignRight)
        layout.addWidget(self.connection_status)

    def send_message(self):
        """Envia un mensaje al servidor"""
        message = self.message_input.text().strip()
        if message:
            self.controller.send_message(message)
            self.message_input.clear()

    def display_message(self, chat_message):
        """Muestra un mensaje en el área de chat"""
        self.chat_display.append(f"{chat_message.sender}: {chat_message.message}")

    def load_message(self, messages):
        """Carga mensajes desde la base de datos en el área de chat"""
        self.chat_display.clear()
        for message in messages:
            self.display_message(message)

    def update_connection_status(self, connected):
        """Actualiza el estado de conexión de la interfaz"""
        status = "Conectado" if connected else "Desconectado"
        self.connection_status.setText(f"Estado: {status}")
