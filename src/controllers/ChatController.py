import socket
import threading

from PySide6.QtCore import QObject, Signal
from src.services.ThreadenTask import ThreadenTask
from src.dao.ChatDAO import ChatDAO
from src.entities.chat.ChatMessage import ChatMessage


class ChatController(QObject):
    message_received_signal = Signal(ChatMessage)
    messages_loaded_signal = Signal(list)
    connection_status_signal = Signal(bool)
    users_list_signal = Signal(list)

    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.receive_task = ThreadenTask()
        self.users_task = ThreadenTask()
        self.dao = ChatDAO()
        self.reconnect_timer = None  # Evitar múltiples intentos de reconexión simultáneos

    def connect_to_server(self):
        """Conecta al servidor de chat"""
        try:
            if self.socket:
                self.disconnect_from_server()

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.server_ip, self.server_port))
            self.socket.settimeout(None)
            self.running = True
            self.receive_task.start(self.receive_message)
            self.users_task.start(self.update_users_list)
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
        self.users_task.stop()
        self.connection_status_signal.emit(False)
        if self.reconnect_timer:
            self.reconnect_timer.cancel()
            self.reconnect_timer = None
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

    def update_users_list(self):
        """Solicita periódicamente la lista de usuarios conectados"""
        while self.running:
            try:
                self.socket.sendall("/users".encode("utf-8"))  # Comando para obtener la lista de usuarios
                users_data = self.socket.recv(1024).decode("utf-8")

                # Imprimir la respuesta del servidor para depuración
                print(f"[DEBUG] Respuesta del servidor: {users_data}")

                # Procesar la respuesta para extraer las IPs únicas
                users_list = users_data.split("\n")
                unique_ips = set()
                for user in users_list:
                    if ":" in user:
                        ip = user.split(":")[0]
                        unique_ips.add(ip)

                # Emitir la lista de IPs únicas
                self.users_list_signal.emit(list(unique_ips))
            except Exception as e:
                print(f"[ERROR] Error al actualizar la lista de usuarios: {e}")
            threading.Event().wait(5)
