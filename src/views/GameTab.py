from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QLabel, \
    QMessageBox
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt, QEvent, Slot
from src.services.ThreadenTask import ThreadenTask


class GameTab(QWidget):
    COLORS = {
        "cyan": QColor(0, 255, 255),
        "blue": QColor(0, 0, 255),
        "red": QColor(255, 0, 0),
        "green": QColor(0, 255, 0),
        "yellow": QColor(255, 255, 0),
    }

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.game_thread = ThreadenTask()  # Hilo para la lógica del juego
        self.controller.update_signal.connect(self.update_game_view)
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus)
        self.installEventFilter(self)

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Panel izquierdo para los botones y el tablero
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel)

        # Botones de control
        self.start_button = QPushButton("Start Game")
        self.pause_button = QPushButton("Pause Game")
        self.reset_button = QPushButton("Reset Game")
        self.stop_button = QPushButton("Stop Game")

        self.start_button.clicked.connect(self.start_game)
        self.pause_button.clicked.connect(self.pause_game)
        self.reset_button.clicked.connect(self.reset_game)
        self.stop_button.clicked.connect(self.stop_game)

        left_panel.addWidget(self.start_button)
        left_panel.addWidget(self.pause_button)
        left_panel.addWidget(self.reset_button)
        left_panel.addWidget(self.stop_button)

        # Área de juego
        self.graphics_view = QGraphicsView()
        self.graphics_view.setFocusPolicy(Qt.NoFocus)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)

        # Dibujar el borde del área de juego (solo una vez)
        self.border_rect = self.graphics_scene.addRect(0, 0, 200, 400)
        border_pen = QPen(QColor(0,255,255))
        border_pen.setWidth(2)
        self.border_rect.setPen(border_pen)
        self.border_rect.setZValue(-1)  # Mantén el borde detrás de las piezas

        left_panel.addWidget(self.graphics_view)

        # Etiqueta de estado
        self.status_label = QLabel("Estado: Juego no iniciado")
        left_panel.addWidget(self.status_label)

        # Panel derecho para el contador de líneas ganadas
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel)

        # Contador de líneas ganadas
        self.lines_label = QLabel("Líneas ganadas: 0")
        right_panel.addWidget(self.lines_label)
        right_panel.addStretch()  # Agregar espacio flexible

    @Slot()
    def start_game(self):
        """Inicia el hilo del juego."""
        if not self.game_thread.is_running():
            self.game_thread.start(self.controller.run_game_logic)
            self.status_label.setText("Estado: Juego iniciado")
            print("[DEBUG] Juego iniciado en un hilo.")
        else:
            print("[DEBUG] El hilo del juego ya está en ejecución.")

    @Slot()
    def pause_game(self):
        """Pausa el juego y detiene el hilo."""
        if self.game_thread.is_running():
            self.game_thread.stop()
            self.controller.stop_game()
            self.status_label.setText("Estado: Juego en pausa")
            print("[DEBUG] Juego pausado.")
        else:
            print("[DEBUG] No hay un hilo de juego en ejecución.")

    @Slot()
    def reset_game(self, manual_reset=True):
        """Reinicia el estado del juego."""
        self.controller.reset_game()
        self.status_label.setText("Estado: Juego reiniciado")
        if manual_reset:
            self.lines_label.setText("Líneas ganadas: 0")
        print("[DEBUG] Juego reiniciado.")
        self.setFocus()

    @Slot()
    def stop_game(self):
        """Detiene el juego completamente."""
        if self.game_thread.is_running():
            self.game_thread.stop()
            self.controller.stop_game()
            self.status_label.setText("Estado: Juego detenido")
            print("[DEBUG] Juego detenido.")
        else:
            print("[DEBUG] El juego ya está detenido.")

    @Slot(str, dict)
    def update_game_view(self, event, data):
        # Limpia solo las piezas dinámicas
        for item in self.graphics_scene.items():
            if item != self.border_rect:  # No borres el borde
                self.graphics_scene.removeItem(item)

        if event in {"new_piece", "gravity", "move", "rotate"}:
            self.draw_board(self.controller.board)
            self.draw_piece(self.controller.current_piece)
        elif event == "clear_lines":
            # Actualiza el tablero y el contador de líneas
            self.draw_board(self.controller.board)
            lines_cleared = data.get("lines_cleared", 0)
            current_lines = int(self.lines_label.text().split(": ")[1])
            self.lines_label.setText(f"Líneas ganadas: {current_lines + lines_cleared}")
        elif event == "game_over":
            if self.status_label.text() != "Estado: Juego terminado":
                self.status_label.setText("Estado: Juego terminado")
                result = QMessageBox.question(self, "Game Over", "¡Has perdido! ¿Quieres volver a intentar?",
                                              QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    self.reset_game(manual_reset=True)

    def draw_board(self, board):
        for r, row in enumerate(board):
            for c, block in enumerate(row):
                if block:
                    self.draw_cell(r, c, "blue")

    def draw_piece(self, piece):
        shape = piece["shape"]
        row = piece["row"]
        col = piece["col"]
        for r, line in enumerate(shape):
            for c, block in enumerate(line):
                if block:
                    self.draw_cell(row + r, col + c, "cyan")

    def draw_cell(self, row, col, color):
        size = 20
        rect = self.graphics_scene.addRect(col * size, row * size, size, size)
        rect.setBrush(self.COLORS.get(color, QColor("white")))

    def showEvent(self, event):
        """Asegura que el foco permanezca en el área de juego cuando se muestra el tab."""
        self.setFocus()
        super().showEvent(event)

    def focusInEvent(self, event):
        """Asegura que el foco se mantenga en el GameTab para capturar teclas."""
        print("GameTab recibió el foco.")  # Depuración
        super().focusInEvent(event)

    def eventFilter(self, obj, event):
        """Filtro de eventos para capturar las teclas."""
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)  # Llama a keyPressEvent para manejar las teclas
            return True  # Indica que el evento fue manejado
        return super().eventFilter(obj, event)  # Propaga otros eventos

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.controller.move_piece("left")
        elif key == Qt.Key_Right:
            self.controller.move_piece("right")
        elif key == Qt.Key_Down:
            self.controller.move_piece("down")
        elif key == Qt.Key_Up:
            self.controller.rotate_piece()  # Llama a la rotación
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Detecta cuando se sueltan las teclas."""
        if event.key() == Qt.Key_Down:
            self.controller.restore_speed()
        super().keyReleaseEvent(event)
