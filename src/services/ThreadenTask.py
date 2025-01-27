import threading
import time


class ThreadenTask:
    def __init__(self):
        self.thread = None
        self.running = False

    def start(self, target, *args, **kwargs):
        """Inicia un hilo con el target dado."""
        if self.running:
            print("El hilo ya está en ejecución.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._wrapper, args=(target, *args), kwargs=kwargs)
        self.thread.start()

    def _wrapper(self, target, *args, **kwargs):
        """Envuelve la ejecución del target para gestionar el estado."""
        try:
            while self.running:
                if target:  # Verifica que target no sea None
                    target(*args, **kwargs)
                time.sleep(0.1)  # Evita un bucle intenso
        finally:
            self.running = False

    def stop(self):
        """Detiene el hilo."""
        self.running = False
        if self.thread and self.thread.is_alive():
            if threading.current_thread() != self.thread:  # Evita `join` desde el mismo hilo
                self.thread.join(timeout=1)

    def is_running(self):
        """Devuelve si el hilo está en ejecución."""
        return self.running
