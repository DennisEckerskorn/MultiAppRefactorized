from src.services.ThreadenTask import ThreadenTask
import datetime
import time
import requests


class ThreadsManager:
    def __init__(self):
        self.threads = {}  # Diccionario para almacenar los hilos por nombre
        self.global_tasks = {}  # Diccionario para tareas globales (hora, temperatura, etc.)

    def start_tab_thread(self, name, task_function):
        """Inicia un hilo para una pestaña específica."""
        if name in self.threads and self.threads[name].is_running():
            print(f"[DEBUG] Hilo '{name}' ya está en ejecución.")
            return

        if not callable(task_function):
            print(f"[ERROR] La función para el hilo '{name}' no es válida.")
            return

        thread_task = ThreadenTask()
        thread_task.start(task_function)
        self.threads[name] = thread_task
        print(f"[DEBUG] Hilo '{name}' iniciado.")

    def stop_tab_thread(self, name):
        """Detiene un hilo específico de una pestaña."""
        if name in self.threads and self.threads[name].is_running():
            self.threads[name].stop()
            print(f"[DEBUG] Hilo '{name}' detenido.")
        else:
            print(f"[DEBUG] Hilo '{name}' no está en ejecución o no existe.")

    def start_global_task(self, name, task_function, *args, **kwargs):
        """Inicia una tarea global en un hilo."""
        if name in self.global_tasks and self.global_tasks[name].is_running():
            print(f"[DEBUG] Tarea global '{name}' ya está en ejecución.")
            return

        if not callable(task_function):
            print(f"[ERROR] La función para la tarea global '{name}' no es válida.")
            return

        thread_task = ThreadenTask()
        thread_task.start(task_function, *args, **kwargs)
        self.global_tasks[name] = thread_task
        print(f"[DEBUG] Tarea global '{name}' iniciada.")

    def stop_global_task(self, name):
        """Detiene una tarea global específica."""
        if name in self.global_tasks and self.global_tasks[name].is_running():
            self.global_tasks[name].stop()
            print(f"[DEBUG] Tarea global '{name}' detenida.")
        else:
            print(f"[DEBUG] Tarea global '{name}' no está en ejecución o no existe.")

    def stop_all_threads(self):
        """Detiene todos los hilos (pestañas y tareas globales)."""
        for name, thread_task in {**self.threads, **self.global_tasks}.items():
            if thread_task.is_running():
                thread_task.stop()
                print(f"[DEBUG] Hilo/Tarea '{name}' detenido.")
        print("[DEBUG] Todos los hilos y tareas detenidos.")

    def update_time(self, ui_instance):
        """Actualiza la hora y fecha cada segundo."""
        task_name = "time"
        while self.global_tasks.get(task_name) and self.global_tasks[task_name].is_running():
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            current_date = datetime.datetime.now().strftime('%d/%m/%Y')
            ui_instance.update_status_data({"hora": current_time, "fecha": current_date})
            for _ in range(10):
                if not self.global_tasks[task_name].is_running():
                    return
            time.sleep(0.1)

    def update_temperature(self, ui_instance):
        """Actualiza la temperatura cada 10 minutos."""
        task_name = "temperature"
        API_KEY = "4ba2b87d7fa32934530b5b4a5a83ebf7"
        CITY = "Madrid"
        while self.global_tasks.get(task_name) and self.global_tasks[task_name].is_running():
            try:
                temperature = self.get_real_temperature(API_KEY, CITY)
                if temperature is not None:
                    ui_instance.update_status_data({"temperatura": f"{temperature}°C"})
            except Exception as e:
                print(f"[DEBUG] Error al obtener la temperatura: {e}")
            for _ in range(600):
                if not self.global_tasks[task_name].is_running():
                    return
                time.sleep(1)

    def get_real_temperature(self, api_key, city):
        """Obtiene la temperatura actual desde OpenWeatherMap."""
        try:
            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            )
            response.raise_for_status()
            data = response.json()
            return data['main']['temp']
        except Exception as e:
            print(f"[DEBUG] Error al obtener la temperatura: {e}")
            return None

    def update_emails(self, ui_instance):
        """Actualiza la cantidad de correos no leídos cada minuto."""
        task_name = "emails"
        while self.global_tasks.get(task_name) and self.global_tasks[task_name].is_running():
            try:
                unread_count = 5  # Simula una consulta real
                ui_instance.update_status_data({"emails": unread_count})
            except Exception as e:
                print(f"[DEBUG] Error en el hilo de correos: {e}")
            for _ in range(60):
                if not self.global_tasks[task_name].is_running():
                    return
                time.sleep(1)
