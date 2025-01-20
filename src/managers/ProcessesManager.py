import subprocess
import webbrowser
from PySide6.QtWidgets import QMessageBox


class ProcessManager:
    def __init__(self, ui_instance):
        """
        Inicializa el ProcessManager con la instancia de la UI principal.

        Args:
            ui_instance (QMainWindow): Instancia de la interfaz principal para mostrar mensajes.
        """
        self.ui_instance = ui_instance

    def open_resource(self, resource_type, path_or_url, fallback_message="Resource not found"):
        """
        Método genérico para abrir programas, archivos o URLs.

        Args:
            resource_type (str): Tipo de recurso ("program" para programas/archivos o "browser" para URLs).
            path_or_url (str): Ruta del programa/archivo o URL a abrir.
            fallback_message (str): Mensaje a mostrar en caso de error. Por defecto, "Resource not found".
        """
        try:
            if resource_type == "program":
                subprocess.Popen([path_or_url])  # Intenta abrir el programa o archivo
            elif resource_type == "browser":
                webbrowser.get("chrome").open(path_or_url)  # Intenta abrir con Chrome
            else:
                raise ValueError("Tipo de recurso desconocido.")
            print(f"[DEBUG] {resource_type.capitalize()} '{path_or_url}' opened successfully.")
        except FileNotFoundError:
            self.show_error_message(f"{fallback_message} (Ruta: {path_or_url})")
        except webbrowser.Error:
            # Si Chrome falla, intenta con el navegador por defecto
            webbrowser.open(path_or_url)
            print(f"[WARNING] Chrome no disponible. Abierto con el navegador por defecto: {path_or_url}")
        except Exception as e:
            self.show_error_message(f"Error al abrir {resource_type}: {fallback_message}. Detalles: {e}")

    def show_error_message(self, message):
        """
        Muestra un mensaje de error usando QMessageBox.

        Args:
            message (str): Mensaje a mostrar en el cuadro de diálogo.
        """
        QMessageBox.critical(self.ui_instance, "Error", message)
