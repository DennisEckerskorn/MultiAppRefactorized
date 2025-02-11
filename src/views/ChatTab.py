from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt
from src.controllers.ChatController import ChatController
#from src.managers.ChatServer import ChatServer


class ChatTab(QWidget):
    def __init__(self, chat_controller: ChatController):
        super().__init__()
        self.controller = chat_controller
        #self.server = ChatServer()
        self.init_ui()

        # Conectar señales del controlador con la interfaz
        self.controller.message_received_signal.connect(self.display_message)
        self.controller.messages_loaded_signal.connect(self.load_message)
        self.controller.connection_status_signal.connect(self.update_connection_status)
        self.controller.users_list_signal.connect(self.update_users_list)

        # Cargar los mensajes al principio
        self.controller.load_messages()

    def init_ui(self):
        """Crea la interfaz gráfica del chat"""
        # Diseño principal horizontal
        main_layout = QHBoxLayout(self)

        # Sección izquierda: Área de chat
        chat_layout = QVBoxLayout()

        # Título y botones de conexión
        header_layout = QHBoxLayout()
        title_label = QLabel("Chat en Vivo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        self.connect_button = QPushButton("Iniciar Servidor")
        self.connect_button.clicked.connect(self.start_server)
        header_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Detener Servidor")
        self.disconnect_button.clicked.connect(self.stop_server)
        self.disconnect_button.setEnabled(False)  # Deshabilitado inicialmente
        header_layout.addWidget(self.disconnect_button)

        chat_layout.addLayout(header_layout)

        # Área de mensajes
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)

        # Campo de entrada de mensajes y botón de enviar
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe tu mensaje aquí...")
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setEnabled(False)  # Deshabilitado inicialmente
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)

        # Estado de conexión
        self.connection_status = QLabel("Estado: Desconectado")
        self.connection_status.setAlignment(Qt.AlignRight)
        chat_layout.addWidget(self.connection_status)

        # Añadir la sección izquierda al diseño principal
        main_layout.addLayout(chat_layout, 3)  # Peso 3 para que ocupe más espacio

        # Sección derecha: Panel lateral
        side_panel = QVBoxLayout()

        # Información de la red
        self.network_info = QLabel(f"Servidor: {self.controller.server_ip}:{self.controller.server_port}")
        self.network_info.setStyleSheet("font-size: 14px; font-weight: bold;")
        side_panel.addWidget(self.network_info)

        # Lista de usuarios conectados
        side_panel.addWidget(QLabel("Usuarios conectados:"))
        self.users_list = QTextEdit()
        self.users_list.setReadOnly(True)
        side_panel.addWidget(self.users_list)

        # Añadir la sección derecha al diseño principal
        main_layout.addLayout(side_panel, 1)  # Peso 1 para que ocupe menos espacio

    def start_server(self):
        """Inicia el servidor de chat"""
        #self.server.start_server()
        self.controller.connect_to_server()
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        print("[INFO] Servidor iniciado desde la interfaz")

    def stop_server(self):
        """Detiene el servidor de chat"""
        #self.server.stop_server()
        self.controller.disconnect_from_server()
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        print("[INFO] Servidor detenido desde la interfaz")

    def send_message(self):
        """Envía un mensaje al servidor"""
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
        self.message_input.setEnabled(connected)
        self.send_button.setEnabled(connected)

    def update_users_list(self, users):
        """Actualiza la lista de usuarios conectados"""
        self.users_list.clear()
        self.users_list.append("\n".join(users))