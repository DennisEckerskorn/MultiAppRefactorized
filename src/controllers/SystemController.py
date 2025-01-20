from PySide6.QtCore import QObject, Signal
from src.services.ThreadenTask import ThreadenTask
import psutil
import time


class SystemController(QObject):
    metrics_signal = Signal(dict)  # Señal para emitir las métricas

    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.running = False
        self.monitoring_task = ThreadenTask()  # Hilo para manejar la lógica de monitoreo

    def start(self):
        """Inicia el monitoreo del sistema en un hilo."""
        if not self.monitoring_task.is_running():
            self.running = True
            self.monitoring_task.start(self._run_monitoring)
            print("[INFO] Monitoreo del sistema iniciado.")

    def stop(self):
        """Detiene el monitoreo del sistema."""
        if self.monitoring_task.is_running():
            self.running = False
            self.monitoring_task.stop()
            print("[INFO] Monitoreo del sistema detenido.")

    def _run_monitoring(self):
        """Lógica principal de monitoreo del sistema."""
        while self.running:
            metrics = {
                "cpu": psutil.cpu_percent(interval=None),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "network": self.get_network_speed(),
                "uptime": self.get_uptime()
            }
            self.metrics_signal.emit(metrics)  # Emitir las métricas mediante la señal
            time.sleep(self.interval)

    @staticmethod
    def get_network_speed():
        """Calcula la velocidad de red en tiempo real (KB/s)."""
        net1 = psutil.net_io_counters()
        time.sleep(0.1)
        net2 = psutil.net_io_counters()
        return (net2.bytes_sent + net2.bytes_recv - net1.bytes_sent - net1.bytes_recv) / 1024

    @staticmethod
    def get_uptime():
        """Calcula el tiempo de actividad del sistema."""
        uptime_seconds = time.time() - psutil.boot_time()
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
