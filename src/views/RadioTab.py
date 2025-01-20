from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt


class RadioTab(QWidget):
    def __init__(self, radio_player):
        super().__init__()
        self.radio_player = radio_player
        self.init_ui()

    def init_ui(self):
        """Crea la interfaz gráfica para gestionar las emisoras de radio."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Título
        title_label = QLabel("Seleccione una emisora de radio")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Espaciador superior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Selector de emisoras
        self.station_selector = QComboBox()
        self.station_selector.addItems(self.radio_player.get_stations().keys())
        self.station_selector.setStyleSheet("font-size: 14px;")
        self.station_selector.setFixedWidth(300)

        combo_layout = QHBoxLayout()
        combo_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        combo_layout.addWidget(self.station_selector)
        combo_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(combo_layout)

        # Espaciador entre selector y botones
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botones de control
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("Reproducir")
        self.play_button.setStyleSheet("font-size: 14px;")
        self.play_button.setFixedSize(120, 40)
        button_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Detener")
        self.stop_button.setStyleSheet("font-size: 14px;")
        self.stop_button.setFixedSize(120, 40)
        button_layout.addWidget(self.stop_button)

        # Contenedor para centrar botones
        button_container = QHBoxLayout()
        button_container.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_container.addLayout(button_layout)
        button_container.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(button_container)

        # Espaciador inferior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Conexión de botones
        self.play_button.clicked.connect(self.start_radio)
        self.stop_button.clicked.connect(self.stop_radio)

    def start_radio(self):
        """Inicia la reproducción de la emisora seleccionada."""
        station_name = self.station_selector.currentText()
        if station_name:
            self.radio_player.play_station(station_name)
            print(f"[DEBUG] Reproducción de '{station_name}' iniciada.")
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una emisora válida.")

    def stop_radio(self):
        """Detiene la reproducción de la emisora."""
        if self.radio_player.running:
            self.radio_player.stop()
            print("[DEBUG] Reproducción de radio detenida.")
        else:
            print("[DEBUG] No hay una emisora en reproducción.")
