import socket
import threading


class ChatServer:
    def __init__(self, host='127.0.0.1', port=3333):
        self.host = host
        self.port = port
        self.server = None
        self.clients = {}
        self.running = False

    def start_server(self):
        """Inicia el servidor en un hilo separado"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.running = True
        print(f"[INICIO] Servidor escuchando en {self.host}:{self.port}")

        # Aceptar conexiones en un hilo separado
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """Acepta nuevas conexiones de clientes"""
        while self.running:
            try:
                client_socket, client_address = self.server.accept()
                self.clients.append(client_socket)
                print(f"[CONECTADO] Nueva conexión desde {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except OSError:
                # Esto ocurre cuando el socket se cierra mientras espera conexiones
                print("[INFO] El servidor ha sido detenido.")
                break
            except Exception as e:
                print(f"[ERROR] Error aceptando clientes: {e}")

    def handle_client(self, client_socket):
        """Maneja la comunicación con un cliente"""
        client_address = client_socket.getpeername()  # Obtener la dirección del cliente
        print(f"[NUEVO CLIENTE] {client_address} conectado.")
        while self.running:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f"[{client_address}] {message.decode('utf-8')}")
                self.broadcast(message, client_socket)
            except Exception as e:
                print(f"[DESCONECTADO] {client_address} se ha desconectado: {e}")
                break
        self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message, sender_socket):
        """Retransmite un mensaje a todos los clientes conectados"""
        for client in self.clients.keys():
            if client != sender_socket:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"[ERROR] No se pudo enviar el mensaje: {e}")
                    self.clients.pop(client, None)

    def stop_server(self):
        """Detiene el servidor y cierra todas las conexiones"""
        self.running = False
        if self.server:
            self.server.close()
        for client in self.clients.keys():
            client.close()
        self.clients = {}
        print("[INFO] Servidor detenido")
