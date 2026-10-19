# Concesionaria · Unidad 4 de Bases de Datos

Proyecto completo: **FastAPI + PostgreSQL/Neon + React/Vite** con administración de esquema (4.1–4.3), **respaldo/restauración (4.4)**, **15 roles DCL (4.5)**, **CSV y migración PostgreSQL → MySQL 8 (4.6)**.

## Instalación en Windows (PowerShell)

1. Extrae este ZIP encima de `D:\concesionaria_unidad4`, **combinando** carpetas `backend` y `frontend` y reemplazando los archivos coincidentes. No elimines tus `.env`, `.env.local` ni los respaldos ya existentes.
2. Si no existen, copia `backend/.env.example` a `backend/.env` y `frontend/.env.local.example` a `frontend/.env.local`. Si ya existen, **conserva tus archivos reales y añade las variables nuevas**.
3. Configura `DATABASE_URL` (Neon), `RESTORE_DATABASE_URL` (PostgreSQL local) y `MYSQL_URL` (MySQL local) en `backend/.env`. Nunca pongas contraseñas de las bases en `frontend/.env.local`.
4. Instala dependencias y ejecuta en dos terminales:

```powershell
cd D:\concesionaria_unidad4
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

En **otra terminal**:

```powershell
cd D:\concesionaria_unidad4\frontend
npm install
npm run build
npm run dev -- --host 127.0.0.1
```

Abrir **http://127.0.0.1:5173** y Swagger en **http://127.0.0.1:8000/docs**. El frontend por defecto usa la URL del backend `http://127.0.0.1:8000`.

**Nota:** si tu `.venv` no existe, créalo desde `D:\concesionaria_unidad4` con `py -m venv .venv`. Instala Node.js reciente y MySQL 8.0.16+.

### 4.4: respaldo y restauración

- Instala PostgreSQL Client Tools (`pg_dump.exe` y `pg_restore.exe`), preferiblemente versión igual o mayor que la versión del servidor de origen. Si no están en `PATH`, configura `PG_DUMP_PATH` y `PG_RESTORE_PATH` con ruta completa (sin comillas añadidas al valor).
- `DATABASE_URL` apunta al servidor PostgreSQL **de origen** (Neon). Para respaldar Neon, utiliza preferentemente la **conexión directa**, no la URL de pooler. Se generan archivos `.backup` en `backend/backups`.
- `RESTORE_DATABASE_URL` apunta a una **base de prácticas distinta** en PostgreSQL local; créala primero en pgAdmin. La restauración limpia/reemplaza los objetos restaurados de la base destino. El backend rechaza un destino cuyo host/puerto/nombre de base coincidan con el origen.
- En React: **Respaldos → Crear respaldo → Descargar → Restaurar**. Para restaurar se requiere escribir `RESTAURAR_DESTINO`.

### 4.5: 15 usuarios DCL

- React: **Usuarios y permisos → selecciona rol → establece contraseña (12 caracteres) → Crear → GRANT → consultar permisos → REVOKE**.
- Los roles y la única combinación GRANT por rol están tomados de `4.5_usuarios_concesionaria.sql`.
- La cuenta de PostgreSQL usada en `DATABASE_URL` necesita `CREATEROLE` para `CREATE ROLE` y capacidad de `GRANT` sobre las tablas. En Neon pueden existir **restricciones de permisos administrados por el proveedor**; si falla, realiza esa demostración con PostgreSQL local usando una cuenta administrativa y, si es necesario, configura `DATABASE_URL` a ese servidor de prácticas.
- La contraseña se introduce únicamente al crear el rol; no se guarda en el frontend ni en el proyecto.

### 4.6: CSV y PostgreSQL → MySQL

- En MySQL Workbench, crea una **base nueva y completamente vacía**:

```sql
CREATE DATABASE concesionaria_migracion
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

- Configura en `backend/.env` la URL con driver `mysql+pymysql://.../concesionaria_migracion?charset=utf8mb4`. Si tu contraseña tiene caracteres reservados (`@`, `:`, `/`, `#`, `%`), utiliza su codificación percent-encoded en la URL.
- React: **Importar y migrar → Exportar CSV / Importar CSV** para transferir registros por tabla. Los CSV tienen encabezados. Si contienen IDs automáticos, la importación conserva esos IDs y ajusta secuencias. Importación es transaccional (rollback por PK/FK/CHECK).
- React: **Migración → Migrar las 8 tablas a MySQL**. La herramienta lee `backend/sql/mysql_concesionaria.sql`, crea estructura compatible y copia datos por lotes con los FKs activos. Requiere confirmación `MIGRAR_CONCESIONARIA`. Compara cantidades finales tabla por tabla. **No mezcla datos con bases MySQL previamente pobladas**; usa una base vacía. Las diferencias entre PostgreSQL/MySQL (collations, regex y tipos) son inherentes a la migración: no se garantiza equivalencia idéntica de motor. **En dos llaves foráneas (`detalle_orden_servicio.codigo_servicio` y `.codigo_refaccion`) MySQL no permite simultáneamente la restricción XOR `CHECK` y `ON UPDATE CASCADE`; el esquema de destino conserva el `CHECK` y la FK con actualización RESTRICT predeterminada.**
- Si una migración falla, debido a los commits implícitos de DDL MySQL, **usa una nueva base de MySQL vacía para reintentar**.

### Cargar datos del ejercicio

En **Tablas y esquema** crea las ocho tablas **solo si la base PostgreSQL está vacía**; después pulsa **Cargar los 43 registros**. Esto reproduce las filas de muestra del SQL aportado, sin necesitar pegarlas en pgAdmin. No repitas la carga porque hay claves únicas.

Para demostrar importar **todo** el contenido CSV, exporta las ocho tablas desde una base con datos, cambia a **otra base PostgreSQL vacía** con las ocho tablas creadas, e importa CSV en orden: `cliente`, `proveedor`, `coche`, `servicio`, `refaccion`, `revision`, `orden_servicio`, `detalle_orden_servicio`.

## Evidencias sugeridas para el documento

| Apartado | Evidencias recomendadas |
|---|---|
| 4.4 | Conexión origen, respaldo en listado, descarga, restauración en PostgreSQL local, tablas y conteos restaurados |
| 4.5 | Lista de 15 roles, `CREATE ROLE`, GRANT, consulta de privilegios, REVOKE |
| 4.6 | Exportación CSV, importación CSV en tabla de práctica, base MySQL vacía, resumen de migración y consulta de conteos en ambos motores |

### Pruebas rápidas

```powershell
cd D:\concesionaria_unidad4\backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Verifica `GET /db/test`, `GET /ddl/estado`, `GET /backup/configuracion`, `GET /dcl/usuarios`, `GET /transfer/tablas` y `GET /transfer/migracion/estado` en Swagger. Si MySQL está sin instalar, los endpoints del módulo CSV siguen disponibles.

## Seguridad y límites

Este es **un panel administrativo local y académico**, no un servicio listo para publicación. FastAPI restringe el acceso a loopback y valida el origen de solicitudes. No expongas Uvicorn con `--host 0.0.0.0`, ni puertos públicos o túneles. No hay autenticación multiusuario. Mantén `.env`, `.env.local` y `backend/backups/` fuera de Git. La eliminación DDL está desactivada (`ENABLE_DESTRUCTIVE_DDL=false`). La carga de datos, restauración, migración y cambios de permisos requieren una base de prácticas y revisión de su destino.

**No se probaron conexiones reales a Neon, PostgreSQL local ni MySQL durante la generación del parche porque sus credenciales y servidores no estaban disponibles.** Se verificaron la sintaxis Python, el tipado TypeScript, las rutas FastAPI y las configuraciones estáticas. La compilación Vite completa debe ejecutarse en Windows tras `npm install` porque los módulos nativos incluidos en los archivos originales eran de Windows.
