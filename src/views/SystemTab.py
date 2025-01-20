from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Slot, Qt
import pyqtgraph as pg
from src.controllers.SystemController import SystemController

class SystemTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Crear e iniciar el controlador de métricas
        self.controller = SystemController()
        self.controller.metrics_signal.connect(self.update_metrics)
        self.controller.start()

    def init_ui(self):
        """Crear componentes de interfaz gráfica para las métricas del sistema."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Título
        title_label = QLabel("Métricas del Sistema")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Espaciador superior
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Etiquetas de métricas
        self.labels = {
            "cpu": QLabel("CPU: --%"),
            "ram": QLabel("RAM: --%"),
            "disk": QLabel("Disco: --%"),
            "network": QLabel("Red: -- KB/s"),
            "uptime": QLabel("Tiempo Activo: --:--:--")
        }

        grid_layout = QGridLayout()
        row = 0
        for key, label in self.labels.items():
            key_label = QLabel(key.capitalize() + ":")
            key_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            label.setStyleSheet("font-size: 14px;")
            grid_layout.addWidget(key_label, row, 0, alignment=Qt.AlignRight)
            grid_layout.addWidget(label, row, 1, alignment=Qt.AlignLeft)
            row += 1

        main_layout.addLayout(grid_layout)

        # Espaciador entre etiquetas y gráfico
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Gráfico para uso de CPU
        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setTitle("Uso de CPU", color="w", size="12pt")
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.showGrid(x=True, y=True)
        self.cpu_graph.getAxis("left").setLabel("% Uso", color="white", size="10pt")
        self.cpu_graph.getAxis("bottom").setLabel("Tiempo", color="white", size="10pt")
        self.cpu_data = []
        self.cpu_curve = self.cpu_graph.plot(pen=pg.mkPen("cyan", width=2))
        main_layout.addWidget(self.cpu_graph)

        # Espaciador inferior
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    @Slot(dict)
    def update_metrics(self, metrics):
        """Actualizar la interfaz con los valores de métricas."""
        for key, value in metrics.items():
            if key == "network":
                self.labels[key].setText(f"{value:.2f} KB/s")
            elif key == "uptime":
                self.labels[key].setText(value)
            else:
                self.labels[key].setText(f"{value:.2f}%")

        # Actualizar gráfico de CPU
        self.cpu_data.append(metrics["cpu"])
        if len(self.cpu_data) > 50:
            self.cpu_data.pop(0)
        self.cpu_curve.setData(self.cpu_data)

    def closeEvent(self, event):
        """Detener el controlador cuando se cierra la pestaña."""
        self.controller.stop()
        super().closeEvent(event)
