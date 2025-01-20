from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
from src.controllers.ScrappingController import ScrappingController


class ScrappingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ScrappingController()
        self.init_ui()

        # Conectar señales del controlador con la interfaz
        self.controller.update_links_signal.connect(self.display_links)
        self.controller.scraping_finished_signal.connect(self.on_scraping_finished)

    def init_ui(self):
        """Crea la interfaz gráfica para el scraping."""
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Scrapping Tool")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Entrada de URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Introduce la URL para scrapear")
        layout.addWidget(self.url_input)

        # Botones
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Scrapping")
        self.stop_button = QPushButton("Detener Scrapping")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_scraping)
        self.stop_button.clicked.connect(self.stop_scraping)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # Área de texto para mostrar enlaces
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

    def start_scraping(self):
        """Inicia el scraping."""
        url = self.url_input.text().strip()
        if url:
            self.text_display.clear()
            self.controller.start_scraping(url)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.text_display.append("[ERROR] Por favor, introduce una URL válida.")

    def stop_scraping(self):
        """Detiene el scraping."""
        self.controller.stop_scraping()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def display_links(self, url, links):
        """Muestra los enlaces encontrados en el área de texto."""
        self.text_display.append(f"Enlaces encontrados en {url}:\n")
        for link in links:
            self.text_display.append(f" - {link}")
        self.text_display.append("\n")

    def on_scraping_finished(self):
        """Maneja el evento cuando el scraping ha terminado."""
        self.text_display.append("[INFO] Scrapping finalizado.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
