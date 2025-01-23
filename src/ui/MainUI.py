from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTabWidget, QLabel,
                               QStatusBar)

from src.views.GameTab import GameTab
from src.views.RadioTab import RadioTab
from src.views.SystemTab import SystemTab
from src.views.ScrappingTab import ScrappingTab
from src.views.EmailTab import EmailTab
from src.controllers.GameController import GameController
from src.controllers.EmailController import EmailController
from src.managers.ThreadsManager import ThreadsManager
from src.managers.ProcessesManager import ProcessManager
from src.services.ThreadenTask import ThreadenTask
from src.services.RadioPlayer import RadioPlayer


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiService App")
        self.setGeometry(100, 100, 1200, 800)

        # Inicializar ThreadsManager y ProcessManager
        self.threads_manager = ThreadsManager()
        self.process_manager = ProcessManager(self)
        self.radio_player = RadioPlayer()
        self.email_controller = EmailController(
            pop_server="192.168.120.103",
            smtp_server="192.168.120.103",
            email="dennis@psp.ieslamar.org",
            password="1234"
        )

        # Hilos para las pestañas
        self.tab_threads = {
            "system_tab": ThreadenTask(),
        }

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left Panel
        self.left_panel = QVBoxLayout()
        main_layout.addLayout(self.left_panel, 1)

        # Tabs Area
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 4)

        # Initialize Tabs and Status Bar
        self.init_tabs()
        self.init_left_panel()
        self.init_status_bar()

        # Iniciar tareas globales (hilos)
        self.threads_manager.start_global_task("time", self.threads_manager.update_time, self)
        self.threads_manager.start_global_task("temperature", self.threads_manager.update_temperature, self)
        self.threads_manager.start_global_task("emails", self.threads_manager.update_emails, self)

    def init_tabs(self):
        """Create and add tabs to the tab widget."""
        self.game_controller = GameController()
        self.radio_tab = RadioTab(radio_player=self.radio_player)
        self.system_tab = SystemTab()
        self.game_tab = GameTab(controller=self.game_controller)
        self.scrapping_tab = ScrappingTab()
        self.email_tab = EmailTab(email_controller=self.email_controller)

        self.tabs.addTab(self.radio_tab, "Radio")
        self.tabs.addTab(self.system_tab, "Sistema")
        self.tabs.addTab(self.game_tab, "Juego")
        self.tabs.addTab(self.scrapping_tab, "Scrapping")
        self.tabs.addTab(self.email_tab, "Correo")

        # Iniciar cada pestaña en un hilo separado
        self.tab_threads["system_tab"].start(self.system_tab.controller.start)

        self.tabs.currentChanged.connect(self.handle_tab_change)

    def handle_tab_change(self, index):
        """Redirige el foco a la pestaña activa."""
        current_widget = self.tabs.widget(index)
        if isinstance(current_widget, GameTab):
            current_widget.setFocus()
            current_widget.graphics_view.setFocus()

    def init_left_panel(self):
        """Create buttons to switch between tabs and open applications."""
        # Crear título para la sección de tabs
        tabs_label = QLabel("Tabs:")
        tabs_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.left_panel.addWidget(tabs_label)

        # Botones para las pestañas
        tabs_buttons = [
            ("Radio", lambda: self.tabs.setCurrentWidget(self.radio_tab)),
            ("Sistema", lambda: self.tabs.setCurrentWidget(self.system_tab)),
            ("Juego", lambda: self.tabs.setCurrentWidget(self.game_tab)),
            ("Scrapping", lambda: self.tabs.setCurrentWidget(self.scrapping_tab)),
            ("Correo", lambda: self.tabs.setCurrentWidget(self.email_tab)),
        ]
        for text, command in tabs_buttons:
            button = QPushButton(text)
            button.clicked.connect(command)
            button.setFixedHeight(40)
            self.left_panel.addWidget(button)

        # Separador entre secciones
        self.left_panel.addSpacing(20)

        # Crear título para la sección de procesos
        processes_label = QLabel("Procesos:")
        processes_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.left_panel.addWidget(processes_label)

        # Botones para los procesos
        processes_buttons = [
            ("Abrir Chrome", lambda: self.process_manager.open_resource(
                "browser", "https://google.com", "No se pudo abrir Chrome.")),
            ("Visual Studio Code", lambda: self.process_manager.open_resource(
                "program", r"C:\Program Files\Microsoft VS Code\Code.exe", "No se encontró Visual Studio Code.")),
            ("Explorador de Windows", lambda: self.process_manager.open_resource(
                "program", "explorer.exe", "No se pudo abrir el Explorador de Windows.")),
            ("Notepad++", lambda: self.process_manager.open_resource(
                "program", r"C:\Program Files\Notepad++\notepad++.exe", "No se encontró Notepad++.exe.")),
        ]
        for text, command in processes_buttons:
            button = QPushButton(text)
            button.clicked.connect(command)
            button.setFixedHeight(40)
            self.left_panel.addWidget(button)

        # Separador entre secciones
        self.left_panel.addStretch()

        # Botón para cerrar la aplicación
        close_button = QPushButton("Cerrar App")
        close_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        close_button.clicked.connect(self.close)
        close_button.setFixedHeight(40)
        self.left_panel.addWidget(close_button)

    def init_status_bar(self):
        """Create a status bar to display dynamic data."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Labels to show dynamic data
        self.status_labels = {
            "hora": QLabel("Hora: --:--:--"),
            "fecha": QLabel("Fecha: ----/--/--"),
            "temperatura": QLabel("Temperatura: --°C"),
            "emails": QLabel("Correos sin leer: 0")
        }

        # Add labels to the status bar
        for label in self.status_labels.values():
            self.status_bar.addWidget(label)

    def update_status_data(self, data):
        """Update the status bar with new data."""
        for key, value in data.items():
            if key in self.status_labels:
                self.status_labels[key].setText(f"{key.capitalize()}: {value}")

    def closeEvent(self, event):
        """Stop all threads when the application is closed."""
        # Detener hilos de las pestañas
        for name, task in self.tab_threads.items():
            task.stop()

        # Detener hilos globales
        self.threads_manager.stop_all_threads()

        # Detener el hilo del GameTab
        if hasattr(self, "game_tab") and hasattr(self.game_tab, "game_thread"):
            if self.game_tab.game_thread.is_running():
                self.game_tab.game_thread.stop()
                print("[DEBUG] Hilo de GameTab detenido.")

        if hasattr(self.system_tab, "controller"):
            self.system_tab.controller.stop()

        if hasattr(self, "scrapping_tab") and self.scrapping_tab.controller:
            self.scrapping_tab.controller.stop_scraping()

        if hasattr(self.email_controller, "fetch_task"):
            self.email_controller.fetch_task.stop()
        if hasattr(self.email_controller, "send_task"):
            self.email_controller.send_task.stop()

        super().closeEvent(event)
