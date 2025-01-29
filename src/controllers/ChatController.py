import socket
from PySide6.QtCore import QObject, Signal
from src.services.ThreadenTask import ThreadenTask
from src.dao.ChatDAO import ChatDAO
from src.entities.chat.ChatMessage import ChatMessage


class ChatController(QObject):
    message_received_signal = Signal(ChatMessage)
    messages_loaded_signal = Signal(list)
    connection_status_signal = Signal(bool)

    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.receive_task = ThreadenTask()
        self.dao = ChatDAO()

    def connect_to_server(self):
        """Conecta al servidor de chat"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            self.running = True
            self.receive_task.start(self.receive_message)
            self.connection_status_signal.emit(True)
            print("[INFO] Conectado al servidor de chat")
        except Exception as e:
            print(f"[ERROR] Error conectando al servidor de chat: {e}")
            self.connection_status_signal.emit(False)

    def disconnect_from_server(self):
        """Desconecta del servidor de chat"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        self.receive_task.stop()
        self.connection_status_signal.emit(False)
        print("[INFO] Desconectado del servidor chat")

    def send_message(self, message):
        """Permite enviar un mensaje al servidor"""
        if self.socket and self.running:
            try:
                self.socket.sendall(message.encode("utf-8"))
                chat_message = ChatMessage(sender="Yo", message=message)
                self.dao.save_chat_message(chat_message)
                self.message_received_signal.emit(chat_message)
            except Exception as e:
                print(f"[ERROR] No se pudo enviar el mensaje: {e}")

    def receive_message(self):
        """Recibe el mensaje del servidor en un hilo separado"""
        while self.running:
            try:
                message = self.socket.recv(1024).decode("utf-8")
                if message:
                    chat_message = ChatMessage(sender="Otro", message=message)
                    self.dao.save_chat_message(chat_message)
                    self.message_received_signal.emit(chat_message)
            except Exception as e:
                print(f"[ERROR] Error al recibir mensaje: {e}")
                self.disconnect_from_server()
                break

    def load_messages(self):
        """Carga todos los mensajes desde la base de datos y emite una señal a la UI"""
        messages = self.dao.fetch_all_messages()
        self.messages_loaded_signal.emit(messages)
