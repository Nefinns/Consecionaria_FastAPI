# DaVinci Music - DDL & DCL API 🎵⚙️

Este repositorio contiene el backend y la interfaz de escritorio experimental para la administración de la base de datos de **DaVinci Music** (escuela y tienda de música). Permite ejecutar operaciones estructurales de bases de datos y gestionar la seguridad y los permisos de los usuarios de forma segura y centralizada.

## 🚀 Tecnologías Principales
* **Backend:** Python, FastAPI, Uvicorn
* **Base de Datos:** PostgreSQL (Neon Cloud), SQLAlchemy, SQLModel
* **Interfaz Gráfica:** Tkinter, `requests`
* **Seguridad:** Variables de entorno (`python-dotenv`) y parametrización de consultas para evitar Inyección SQL.

## ⚙️ Características
* **Módulo DDL (Data Definition Language):** Interfaz para la ejecución controlada de operaciones `CREATE`, `ALTER` y `DROP` sobre las tablas de la base de datos.
* **Módulo DCL (Data Control Language):** Gestión de usuarios mediante la creación de roles, asignación de contraseñas y control granular de privilegios (`GRANT` y `REVOKE`) por tabla y esquema.
* **Arquitectura de Capas:** Separación limpia entre la interfaz visual (Tkinter) y el manejo de transacciones a la base de datos (FastAPI).

## 🛠️ Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone <url-de-tu-repositorio>
   cd <nombre-de-la-carpeta>