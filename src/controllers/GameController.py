import time
import random
from PySide6.QtCore import Signal, QObject
from src.services.ThreadenTask import ThreadenTask


class GameController(QObject):
    update_signal = Signal(str, dict)  # Señal para comunicar eventos al GameTab

    def __init__(self):
        super().__init__()
        self.game_task = ThreadenTask()  # Instancia de ThreadenTask
        self.running = False
        self.board = [[0 for _ in range(10)] for _ in range(20)]
        self.current_piece = None
        self.drop_speed = 1.0
        self.lines_cleared = 0  # Contador de líneas ganadas

    def start_game(self):
        """Inicia el juego en un hilo separado."""
        if not self.game_task.is_running():
            self.running = True
            self.game_task.start(self.run_game_logic)
            self.update_signal.emit("game_started", {})

    def stop_game(self):
        """Detiene el hilo del juego."""
        self.running = False
        self.game_task.stop()

    def reset_game(self):
        """Reinicia el estado del juego."""
        self.stop_game()
        self.board = [[0 for _ in range(10)] for _ in range(20)]
        self.current_piece = None
        self.running = True
        self.lines_cleared = 0
        self.spawn_piece()

    def run_game_logic(self):
        """Lógica principal del juego ejecutada en un hilo."""
        self.running = True
        self.spawn_piece()
        while self.running:
            time.sleep(self.drop_speed)
            if self.can_move(1, 0):
                self.current_piece["row"] += 1
                self.update_signal.emit("gravity", self.current_piece)
            else:
                self.place_piece()
                self.spawn_piece()

    def spawn_piece(self):
        """Genera una nueva pieza en la parte superior del tablero."""
        shapes = [
            [[1, 1, 1], [0, 1, 0]],  # T-shape
            [[1, 1], [1, 1]],  # Square
            [[1, 1, 1, 1]],  # Line
            [[0, 1, 1], [1, 1, 0]],  # S-shape
            [[1, 1, 0], [0, 1, 1]],  # Z-shape
        ]
        shape = random.choice(shapes)
        start_row = 0
        start_col = (10 - len(shape[0])) // 2

        if not self.can_place(shape, start_row, start_col):
            self.running = False
            self.update_signal.emit("game_over", {})
            return

        self.current_piece = {
            "shape": shape,
            "row": start_row,
            "col": start_col,
        }
        self.update_signal.emit("new_piece", self.current_piece)

    def move_piece(self, direction):
        """Mueve la pieza actual."""
        if direction == "down":
            self.drop_speed = 0.1
        else:
            dcol = -1 if direction == "left" else 1
            if self.can_move(0, dcol):
                self.current_piece["col"] += dcol
                self.update_signal.emit("move", self.current_piece)

    def rotate_piece(self):
        """Rota la pieza actual en el sentido horario."""
        if not self.current_piece:
            return

        shape = self.current_piece["shape"]
        rotated_shape = list(zip(*shape[::-1]))
        row, col = self.current_piece["row"], self.current_piece["col"]

        if self.can_place(rotated_shape, row, col):
            self.current_piece["shape"] = rotated_shape
            self.update_signal.emit("rotate", self.current_piece)

    def place_piece(self):
        """Fija la pieza actual en el tablero y elimina líneas completas."""
        shape = self.current_piece["shape"]
        row = self.current_piece["row"]
        col = self.current_piece["col"]
        for r, line in enumerate(shape):
            for c, block in enumerate(line):
                if block:
                    self.board[row + r][col + c] = 1
        self.clear_lines()

    def clear_lines(self):
        """Elimina las líneas completas del tablero y cuenta las líneas ganadas."""
        initial_rows = len(self.board)
        self.board = [line for line in self.board if any(cell == 0 for cell in line)]
        cleared_lines = initial_rows - len(self.board)

        while len(self.board) < 20:
            self.board.insert(0, [0] * 10)

        self.update_signal.emit("clear_lines", {"lines_cleared": cleared_lines})

    def can_place(self, shape, row, col):
        """Verifica si una pieza puede colocarse en una posición específica."""
        for r, line in enumerate(shape):
            for c, block in enumerate(line):
                if block:
                    if row + r >= 20 or col + c < 0 or col + c >= 10:
                        return False
                    if self.board[row + r][col + c]:
                        return False
        return True

    def can_move(self, drow, dcol):
        """Verifica si la pieza puede moverse en una dirección específica."""
        shape = self.current_piece["shape"]
        row = self.current_piece["row"] + drow
        col = self.current_piece["col"] + dcol
        return self.can_place(shape, row, col)

    def restore_speed(self):
        """Restaura la velocidad normal de caída."""
        self.drop_speed = 1.0
