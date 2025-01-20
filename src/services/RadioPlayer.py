import vlc
import time
from src.services.ThreadenTask import ThreadenTask


class RadioPlayer:
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.thread_task = ThreadenTask()
        self.running = False
        self.current_url = None
        self.stations = {
            "Box Radio UK": "http://uk2.internet-radio.com:8024/",
            "Jazz Radio": "http://us2.internet-radio.com:8443/",
            "Deep House Radio": "http://uk7.internet-radio.com:8000/",
        }

    def get_stations(self):
        """Devuelve el diccionario de emisoras."""
        return self.stations

    def play_station(self, station_name):
        """Inicia la reproducción de una emisora por su nombre."""
        if station_name in self.stations:
            url = self.stations[station_name]
            print(f"[INFO] Iniciando reproducción: {station_name}")
            self.play(url)  # Llama al método general de reproducción
        else:
            print(f"[ERROR] La emisora '{station_name}' no existe.")

    def play(self, url):
        """Inicia la reproducción de una emisora por URL."""
        try:
            if self.running and self.current_url == url:
                print("[INFO] Ya se está reproduciendo esta emisora.")
                return

            if self.running:
                self.stop()

            self.current_url = url
            self.thread_task.start(self._play_radio, url)
            self.running = True
        except Exception as e:
            print(f"Error al reproducir la emisora: {e}")

    def _play_radio(self, url):
        """Maneja la reproducción en un hilo separado."""
        try:
            self.player.set_media(vlc.Media(url))
            self.player.play()
            while self.thread_task.is_running():
                time.sleep(0.1)  # Mantener el hilo vivo mientras se reproduce
        except Exception as e:
            print(f"Error en la reproducción de la radio: {e}")

    def stop(self):
        """Detiene la reproducción de la emisora."""
        try:
            if self.running:
                self.thread_task.stop()
                self.player.stop()
                self.running = False
                self.current_url = None
                print("[INFO] Reproducción detenida.")
        except Exception as e:
            print(f"Error al detener la reproducción: {e}")

    def run_radio_logic(self):
        """Lógica en segundo plano para actualizar el estado de la radio."""
        while True:
            if self.running and self.current_url:
                print(f"[INFO] Reproduciendo: {self.current_url}")
            else:
                print("[INFO] No hay emisora reproduciéndose actualmente.")
            time.sleep(30)  # Actualiza cada 30 segundos
