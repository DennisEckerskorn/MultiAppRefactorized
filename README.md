# **MultiService App**

### **Resumen**

MultiService App es una aplicación multifuncional desarrollada en Python utilizando el framework **PySide6** para la interfaz gráfica y **SQLite** como base de datos. La aplicación integra múltiples servicios, como chat en vivo, gestión de correos electrónicos, monitoreo del sistema, scraping web y un juego interactivo. Cada funcionalidad está organizada en pestañas dentro de una interfaz gráfica intuitiva y modular.

Este proyecto fue desarrollado por **Dennis Eckerskorn** como parte de la asignatura **Servicios y Procesos de Desarrollo de Aplicaciones Multiplataforma**.

---

### **Características**

- **Interfaz gráfica moderna**: Basada en PySide6, con pestañas para cada funcionalidad.
- **Gestión de hilos**: Uso extensivo de hilos para ejecutar tareas en segundo plano sin bloquear la interfaz gráfica.
- **Persistencia de datos**: Almacenamiento de datos en una base de datos SQLite para chat, correos y scraping.
- **Modularidad**: Cada funcionalidad está encapsulada en controladores, vistas y servicios independientes.
- **Multifuncionalidad**:
  - Chat en vivo con almacenamiento de mensajes.
  - Gestión de correos electrónicos (envío y recepción).
  - Monitoreo del sistema en tiempo real.
  - Scraping web con almacenamiento de enlaces.
  - Juego interactivo basado en un tablero.

---

### **Procesos Utilizados en la Aplicación**

La aplicación utiliza múltiples procesos y técnicas para gestionar tareas complejas de manera eficiente. A continuación, se describen los principales procesos:

1. **Gestión de Hilos**:
   - Todas las tareas intensivas, como la recepción de mensajes, el scraping web, el monitoreo del sistema y la lógica del juego, se ejecutan en hilos separados utilizando la clase `ThreadenTask`.
   - Esto asegura que la interfaz gráfica permanezca fluida y receptiva, incluso durante operaciones intensivas.

2. **Sockets (Chat en Vivo)**:
   - La funcionalidad de chat utiliza **sockets TCP** para conectarse a un servidor de chat.
   - **Proceso de conexión**:
     - El cliente (aplicación) se conecta al servidor mediante un socket.
     - Una vez conectado, el cliente puede enviar y recibir mensajes en tiempo real.
   - **Recepción de mensajes**:
     - Se ejecuta en un hilo separado que escucha continuamente los mensajes entrantes del servidor.
   - **Actualización de usuarios**:
     - El cliente envía comandos al servidor para solicitar la lista de usuarios conectados, que se actualiza periódicamente.

3. **Gestión de Correos Electrónicos**:
   - La aplicación utiliza los protocolos **POP3** y **SMTP** para la recepción y envío de correos electrónicos, respectivamente.
   - **Recepción de correos (POP3)**:
     - Se conecta al servidor de correo mediante el protocolo POP3.
     - Descarga los correos en un hilo separado y los guarda en la base de datos SQLite.
     - Verifica si un correo ya existe en la base de datos antes de almacenarlo.
   - **Envío de correos (SMTP)**:
     - Utiliza el protocolo SMTP para enviar correos electrónicos.
     - Soporta el envío de archivos adjuntos, que se codifican y se envían junto con el mensaje.
     - El proceso de envío se ejecuta en un hilo separado para evitar bloquear la interfaz gráfica.

4. **Scraping Web**:
   - Realiza solicitudes HTTP para obtener el contenido de páginas web.
   - Analiza el contenido HTML utilizando `BeautifulSoup` para extraer enlaces.
   - Los enlaces encontrados se almacenan en la base de datos SQLite.
   - La navegación recursiva por los enlaces se gestiona en un hilo separado.

5. **Monitoreo del Sistema**:
   - Recopila métricas del sistema, como el uso de CPU, RAM, disco, velocidad de red y tiempo de actividad.
   - Estas métricas se recopilan en un hilo separado y se emiten a la interfaz gráfica en tiempo real.

6. **Juego Interactivo (Tetris)**:
   - La lógica del juego, como la caída automática de piezas, la detección de colisiones y la eliminación de líneas, se ejecuta en un hilo separado.
   - Esto permite que el jugador interactúe con la interfaz gráfica sin interrupciones.

---

### **Uso de Hilos**

El uso de hilos es una característica clave de la aplicación, ya que permite ejecutar tareas intensivas en segundo plano sin bloquear la interfaz gráfica. Esto se logra mediante la clase `ThreadenTask`, que encapsula la lógica de ejecución en hilos separados.

#### **Tareas que usan hilos separados**

1. **Chat en Vivo**:
   - **Recepción de mensajes**: Escucha mensajes del servidor en tiempo real.
   - **Actualización de la lista de usuarios**: Solicita periódicamente la lista de usuarios conectados al servidor.

2. **Gestión de Correos Electrónicos**:
   - **Recepción de correos**: Descarga correos desde el servidor POP3 en un hilo separado.
   - **Envío de correos**: Envía correos mediante SMTP en segundo plano, incluyendo el manejo de archivos adjuntos.

3. **Monitoreo del Sistema**:
   - **Recopilación de métricas**: Ejecuta la lógica de monitoreo (CPU, RAM, disco, red, uptime) en un hilo separado, emitiendo actualizaciones periódicas a la UI.

4. **Scraping Web**:
   - **Extracción de enlaces**: Realiza solicitudes HTTP y analiza el contenido HTML en un hilo separado.
   - **Navegación recursiva**: Procesa los enlaces encontrados de manera asíncrona.

5. **Juego Interactivo (Tetris)**:
   - **Lógica principal del juego**: La caída automática de las piezas y la detección de colisiones se ejecutan en un hilo separado.
   - **Eventos del juego**:
     - Generación de nuevas piezas.
     - Movimiento de las piezas hacia abajo (gravedad).
     - Eliminación de líneas completas.
     - Detección del fin del juego.

#### **Uso de hilos en el Tetris**

El juego tipo Tetris utiliza un hilo separado para ejecutar su lógica principal, lo que permite que las piezas caigan automáticamente mientras el jugador interactúa con la interfaz gráfica. A continuación, se detallan las tareas específicas que se ejecutan en el hilo:

- **Caída automática de piezas**:
  - La pieza actual desciende una fila a intervalos regulares, controlados por la variable `drop_speed`.
  - Si la pieza no puede descender más, se fija en el tablero y se genera una nueva pieza.

- **Detección de colisiones**:
  - Verifica si la pieza puede moverse o rotar sin chocar con otras piezas o los bordes del tablero.

- **Eliminación de líneas completas**:
  - Identifica y elimina filas completas del tablero, desplazando las filas superiores hacia abajo.

- **Detección del fin del juego**:
  - Si no hay espacio para generar una nueva pieza, el juego finaliza y se emite un evento `game_over`.

Este enfoque asegura que el juego sea fluido y que la interfaz gráfica responda rápidamente a las acciones del usuario.

---

### **Uso de Base de Datos (SQLite)**

La aplicación utiliza **SQLite** como base de datos para almacenar datos de manera persistente. A continuación, se describen las tablas principales:

1. **`chat_messages`**:
   - Almacena los mensajes de chat.
   - Campos: `id`, `sender`, `message`, `timestamp`.

2. **`received_emails`**:
   - Almacena los correos electrónicos recibidos.
   - Campos: `id`, `sender`, `recipient`, `subject`, `body`, `message_id`, `received_at`, `read`.

3. **`sent_emails`**:
   - Almacena los correos electrónicos enviados.
   - Campos: `id`, `sender`, `recipient`, `subject`, `body`, `attachment_path`, `sent_at`.

4. **`scrapped_links`**:
   - Almacena los enlaces extraídos durante el scraping.
   - Campos: `id`, `url`, `parent_url`, `timestamp`.

**Ventajas del uso de SQLite**:
- **Ligero y eficiente**: Ideal para aplicaciones de escritorio.
- **Integración sencilla**: No requiere configuración adicional.
- **Consultas SQL**: Permite realizar operaciones complejas de manera eficiente.

---

### **Video Explicativo**

Para una explicación detallada de la aplicación, consulta el siguiente video en YouTube:

[![Video Explicativo](https://img.youtube.com/vi/<VIDEO_IDjpg)](https://www.youtube.com/watch?v=<VIDEO_ID)

---
