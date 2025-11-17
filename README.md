---

# Control de Salidas Peatonales - Colegio

Aplicación web y móvil (PWA) para la gestión y control de salidas peatonales de estudiantes en un entorno escolar. El sistema permite registrar estudiantes, generar carnets con códigos QR y validar las salidas en tiempo real utilizando la cámara de un dispositivo.

![Dashboard](app/static/img/dashboard.png) <!-- Asegúrate de que esta ruta sea correcta o reemplázala con una captura de pantalla de la app -->

---

## ✨ Características Principales

*   **Autenticación y Roles**: Sistema de inicio de sesión seguro con dos roles:
    *   **Administrador**: Acceso total al sistema.
    *   **Operador**: Acceso exclusivo a la funcionalidad de escaneo y registro de salidas.
*   **Gestión de Estudiantes**: CRUD completo para estudiantes, incluyendo ID, nombre, curso, foto y estado de autorización de salida.
*   **Gestión de Puertas**: CRUD para las puertas de salida del colegio, cada una con un nombre y estado (Abierta/Cerrada).
*   **Escaneo de QR en Tiempo Real**: Utiliza la cámara del dispositivo (móvil o de escritorio) para leer el código QR del carnet del estudiante y validar su identidad y autorización.
*   **Generación de Carnets PDF**:
    *   Creación de carnets individuales o en lote.
    *   Diseño vertical de 5.4 x 8.5 cm, listo para imprimir.
    *   Incluye logo del colegio, foto del estudiante, nombre, ID y código QR.
*   **Importación y Carga Masiva**:
    *   **Importación de Estudiantes**: Añade estudiantes de forma masiva subiendo un archivo Excel (`.xlsx`).
    *   **Carga de Fotos**: Actualiza las fotos de los estudiantes en lote subiendo un archivo ZIP con las imágenes nombradas según el ID del estudiante.
*   **Dashboard Interactivo**:
    *   Resumen de estadísticas clave (total de estudiantes, salidas del día).
    *   Gráficas dinámicas de salidas por día, por curso y por puerta.
*   **Reportes Avanzados**:
    *   Visualización de todos los registros de salida con filtros por rango de fechas.
    *   Ordenamiento dinámico de la tabla haciendo clic en los encabezados.
    *   Exportación de los reportes filtrados a **CSV** y **PDF**.
*   **Soporte PWA (Progressive Web App)**: La aplicación puede ser "instalada" en la pantalla de inicio de un dispositivo móvil para un acceso rápido y una experiencia similar a la de una app nativa.

---

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **Base de Datos**: SQLAlchemy ORM con soporte para SQLite y **MySQL**.
*   **Migraciones**: Flask-Migrate (basado en Alembic).
*   **Frontend**: HTML5, TailwindCSS, JavaScript.
*   **Librerías Clave**:
    *   `Flask-Login`: Gestión de sesiones de usuario.
    *   `Flask-WTF`: Formularios y validaciones.
    *   `openpyxl`: Lectura de archivos Excel.
    *   `qrcode`: Generación de imágenes de códigos QR.
    *   `reportlab`: Creación de documentos PDF.
    *   `html5-qrcode`: Librería de JavaScript para el escaneo de QR.
    *   `Chart.js`: Gráficas interactivas.

---

## ⚙️ Configuración y Ejecución Local

Sigue estos pasos para poner en marcha el proyecto en tu entorno de desarrollo.

### Prerrequisitos

*   Python 3.8 o superior.
*   Git.
*   Servidor de base de datos MySQL Community.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/joanvup/control-salidas-colegio.git
cd control-salidas-colegio
```

### 2. Crear y Activar el Entorno Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos MySQL

1.  Inicia sesión en tu consola de MySQL como `root`:
    ```sql
    mysql -u root -p
    ```
2.  Ejecuta los siguientes comandos para crear la base de datos y un usuario dedicado:
    ```sql
    CREATE DATABASE control_salidas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'control_salidas_user'@'localhost' IDENTIFIED BY 'tu-contraseña-segura-aqui';
    GRANT ALL PRIVILEGES ON control_salidas_db.* TO 'control_salidas_user'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```

### 5. Configurar las Variables de Entorno

1.  Renombra el archivo `.env.template` a `.env` (si lo tienes) o crea un nuevo archivo `.env` en la raíz del proyecto.
2.  Añade y modifica el siguiente contenido:

    ```env
    # Clave secreta para la seguridad de la aplicación. Cámbiala por una cadena aleatoria.
    SECRET_KEY='una-clave-secreta-muy-dificil-de-adivinar'

    # Cadena de conexión a tu base de datos MySQL
    # Asegúrate de usar el usuario y la contraseña que creaste en el paso anterior.
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://control_salidas_user:tu-contraseña-segura-aqui@localhost/control_salidas_db'
    ```

### 6. Aplicar las Migraciones de la Base de Datos

Este comando creará todas las tablas necesarias en tu base de datos MySQL.

```bash
flask db upgrade
```

### 7. Crear el Primer Usuario Administrador

El sistema incluye un comando personalizado para crear tu primer usuario de forma interactiva y segura.

```bash
flask admin create
```
Sigue las instrucciones en la consola para establecer el nombre de usuario, email y contraseña.

### 8. Ejecutar la Aplicación

```bash
flask run
```
La aplicación estará disponible en `http://127.0.0.1:5000`.

---

## 🚀 Uso de la Aplicación

1.  **Inicio de Sesión**: Accede a la aplicación con las credenciales del usuario administrador que creaste.
2.  **Configuración Inicial (Admin)**:
    *   Ve a **Puertas** y añade las puertas de salida del colegio (ej. "Puerta Principal", "Salida Patio"). Asegúrate de que estén en estado "Abierta".
    *   Ve a **Estudiantes** y añade algunos estudiantes manualmente, o utiliza la función "Importar" para subirlos desde un archivo Excel.
    *   Genera los carnets en PDF y entrégalos a los estudiantes.
3.  **Registro de Salidas (Operador)**:
    *   Un usuario con rol de Operador inicia sesión.
    *   Va a la sección **Escanear Salida**.
    *   Selecciona la puerta por la que se está realizando la salida.
    *   Escanea el código QR del carnet del estudiante.
    *   Si el estudiante está autorizado, confirma la salida. El registro queda guardado con la fecha, hora, estudiante, puerta y operador.
4.  **Monitoreo y Reportes (Admin)**:
    *   El **Dashboard** muestra en tiempo real las estadísticas de salida del día.
    *   La sección de **Reportes** permite consultar el historial de salidas, filtrar por fechas, ordenar los resultados y exportar los datos.

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.