import requests
import threading
from PySide6.QtCore import QObject, Signal
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue

from src.dao.ScrappingDAO import ScrappingDAO
from src.services.ThreadenTask import ThreadenTask


class ScrappingController(QObject):
    update_links_signal = Signal(str, list)  # Señal para actualizar enlaces encontrados en la UI
    scraping_finished_signal = Signal()  # Señal para indicar que el scraping ha terminado

    def __init__(self):
        super().__init__()
        self.running = False
        self.visited_links = set()
        self.link_queue = Queue()
        self.lock = threading.Lock()

        # Tareas para scraping
        self.scraping_task = ThreadenTask()
        self.dao = ScrappingDAO()


    def start_scraping(self, url):
        """Inicia el proceso de scraping."""
        if self.running:
            print("[INFO] El scraping ya está en ejecución.")
            return

        self.running = True
        self.visited_links.clear()
        self.link_queue.queue.clear()

        if url:
            print(f"[INFO] Iniciando scraping en: {url}")
            self.dao.start_insertion_task()
            self.scraping_task.start(self.scrape_page, url)
        else:
            print("[ERROR] No se proporcionó una URL válida.")

    def stop_scraping(self):
        """Detiene el proceso de scraping."""
        print("[INFO] Deteniendo el proceso de scraping.")
        self.running = False
        self.scraping_task.stop()
        self.dao.stop_insertion_task()
        self.scraping_finished_signal.emit()

    def scrape_page(self, url):
        """Scrapea una página y busca enlaces."""
        if not self.running or url in self.visited_links:
            return

        with self.lock:
            self.visited_links.add(url)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                links = [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)]

                if self.running:
                    self.update_links_signal.emit(url, links)

                for link in links:
                    if not self.running:
                        break
                    self.link_queue.put((url, link))
                    self.dao.insert_link_async(link, url)
                    self.scrape_page(link)
            else:
                print(f"[ERROR] Error al acceder a {url}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error al scrapear {url}: {e}")
