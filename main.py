from PySide6.QtWidgets import QApplication
from src.ui.MainUI import MainUI
import sys

def main():
    try:
        # Crear la aplicación
        app = QApplication(sys.argv)

        # Crear la ventana principal
        main_window = MainUI()

        # Mostrar la ventana principal
        main_window.show()

        # Ejecutar el evento de la aplicación
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error al iniciar la app: {e}")

if __name__ == "__main__":
    main()
