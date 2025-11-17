# Control de Salidas Peatonales - Aplicación Web

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3-black.svg)
![MySQL](https://img.shields.io/badge/mysql-8.0-orange.svg)
![TailwindCSS](https://img.shields.io/badge/tailwind-css-blueviolet.svg)
![GitHub](https://img.shields.io/github/license/tu-usuario/tu-repositorio)

Aplicación web full-stack diseñada para gestionar y registrar las salidas peatonales de estudiantes en un colegio. La plataforma permite la administración de estudiantes, la generación de carnets con códigos QR, el registro de salidas en tiempo real mediante escaneo con la cámara y la generación de reportes detallados.

---

## 📸 Screenshots (Capturas de Pantalla)

*(**Nota:** Se recomienda encarecidamente añadir aquí capturas de pantalla del Dashboard, la página de escaneo y la lista de estudiantes para mostrar visualmente la aplicación).*

---

## ✨ Características Principales

### 👤 Rol de Administrador
*   **Gestión de Estudiantes (CRUD)**: Creación, lectura, actualización y eliminación de perfiles de estudiantes, incluyendo su foto.
*   **Gestión de Puertas (CRUD)**: Administración de las puertas de salida, incluyendo su nombre y estado (Abierta/Cerrada).
*   **Gestión de Usuarios**: Registro de nuevos usuarios con roles de Administrador u Operador.
*   **Importación Masiva**: Carga de estudiantes desde un archivo Excel (`.xlsx`), con descarga de plantilla de ejemplo.
*   **Carga de Fotos en Lote**: Actualización masiva de las fotos de los estudiantes mediante la carga de un archivo ZIP.
*   **Generación de Carnets**: Creación de carnets en formato PDF (tamaño 5.4 x 8.5 cm) con diseño personalizado, listos para imprimir. Descarga individual o de todos los carnets en un solo archivo.
*   **Generación de QR**: Descarga de todos los códigos QR de los estudiantes en un archivo ZIP.
*   **Dashboard Interactivo**: Visualización de estadísticas clave, con gráficas de salidas por día y por curso.
*   **Reportes Avanzados**: Filtrado de registros de salida por rango de fechas y ordenamiento dinámico por columnas.
*   **Exportación de Datos**: Exportación de reportes filtrados a formatos **CSV** y **PDF**.

### 🛂 Rol de Operador
*   **Escaneo de QR**: Interfaz optimizada para móviles que utiliza la cámara del dispositivo para escanear los carnets.
*   **Validación en Tiempo Real**: Al escanear, el sistema verifica si el estudiante existe y si está autorizado para salir.
*   **Registro de Salidas**: Registro de cada salida con un solo clic, asociando al estudiante, la puerta, el operador y un timestamp preciso (zona horaria de Colombia).
*   **Validación de Cooldown**: El sistema previene registros duplicados accidentales, requiriendo un tiempo de espera configurable entre salidas para el mismo estudiante.
*   **Acceso al Dashboard y Reportes**: Visualización de las estadísticas y los registros de salida.

### ⚙️ Características Técnicas
*   **Backend**: Python con **Flask**.
*   **Base de Datos**: **MySQL** (con soporte para SQLite). Migraciones gestionadas con **Flask-Migrate**.
*   **ORM**: **SQLAlchemy**.
*   **Frontend**: HTML5, **TailwindCSS** para un diseño moderno y responsivo, y JavaScript vanilla para la interactividad.
*   **PWA (Progressive Web App)**: Incluye `manifest.json` y `Service Worker` para una experiencia similar a una app nativa en móviles.
*   **Estructura Organizada**: Sigue el patrón de diseño "Application Factory" y "Blueprints" para una máxima escalabilidad y mantenibilidad.

---

## 💻 Pila Tecnológica

| Backend                      | Frontend & Diseño        | Base de Datos |
| ---------------------------- | ------------------------ | ------------- |
| Python 3.11+                 | HTML5                    | MySQL 8.0+    |
| Flask                        | TailwindCSS              | SQLAlchemy    |
| Flask-SQLAlchemy             | JavaScript (Vanilla)     | Flask-Migrate |
| Flask-Login (Sesiones)       | Chart.js (Gráficas)      | PyMySQL       |
| Flask-WTF (Formularios)      | html5-qrcode (Escáner)   |               |
| Werkzeug                     |                          |               |
| ReportLab (PDFs)             |                          |               |
| openpyxl (Excel)             |                          |               |
| qrcode                       |                          |               |

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno de desarrollo (Windows + VSCode).

### Prerrequisitos
*   **Python 3.10+**
*   **Git**
*   **MySQL Community Server 8.0+**

### Pasos de Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/tu-repositorio.git
    cd tu-repositorio
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la base de datos MySQL:**
    *   Inicia sesión en tu consola de MySQL como `root`.
    *   Crea la base de datos, el usuario y otorga los permisos (reemplaza `'tu_contraseña'` por una contraseña segura):
        ```sql
        CREATE DATABASE control_salidas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER 'control_salidas_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
        GRANT ALL PRIVILEGES ON control_salidas_db.* TO 'control_salidas_user'@'localhost';
        FLUSH PRIVILEGES;
        EXIT;
        ```

5.  **Configurar las variables de entorno:**
    *   Crea una copia del archivo `.env.example` y renómbrala a `.env`.
    *   Edita el archivo `.env` con tus propias credenciales.

    ```dotenv
    # Contenido del archivo .env
    FLASK_APP=run.py
    # ¡IMPORTANTE! Cambia esto por una clave secreta larga y aleatoria
    SECRET_KEY='una-clave-secreta-muy-dificil-de-adivinar'
    
    # Cadena de conexión a tu base de datos MySQL
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://control_salidas_user:tu_contraseña@localhost/control_salidas_db'
    ```

6.  **Aplicar las migraciones de la base de datos:**
    Este comando creará todas las tablas en tu base de datos MySQL.
    ```bash
    flask db upgrade
    ```

7.  **Crear el primer usuario administrador:**
    Ejecuta el siguiente comando y sigue las instrucciones interactivas en la terminal para crear tu cuenta de administrador.
    ```bash
    flask admin create
    ```

8.  **Ejecutar la aplicación:**
    ```bash
    flask run
    ```
    La aplicación estará disponible en **`http://127.0.0.1:5000`**.

---

## 📁 Estructura del Proyecto

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.