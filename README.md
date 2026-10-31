# AutoGest — Laboratorio de Bases de Datos, Unidad 5

**Concesionaria AutoGest · PostgreSQL 15+ · FastAPI · React / TypeScript / Vite · Tailwind CSS 4 + Base UI (shadcn/ui)**

Este proyecto es un **laboratorio académico independiente**, equivalente al laboratorio de DaVinciMusic de la Unidad 5, adaptado al **esquema canónico de seis tablas** suministrado para AutoGest. No sustituye el sistema de concesionaria original ni su autenticación SuperTokens.

## Alcance exacto: 65 ejercicios

| Unidad | Tema | Ejercicios |
|---|---|---:|
| 5.1 | Consultas simples (`SELECT`, `WHERE`, `LIKE`, rangos, orden) | 25 (`S01–S25`) |
| 5.2 | Operaciones JOIN (`INNER`, `LEFT`, `LATERAL`, varios JOIN) | 15 (`J01–J15`) |
| 5.3 | Agregaciones (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`) | 15 (`A01–A15`) |
| 5.4 | Vistas SQL | 5 (`V01–V05`) |
| 5.5 | Funciones PL/pgSQL y disparadores | 5 funciones + 5 triggers (`T01–T05`) |
| **Total** | | **65** |

### Tablas del esquema canónico

`cliente`, `proveedor`, `usuario_interno`, `coche`, `venta` y `revision`. El archivo **original, sin modificaciones**, está en `backend/sql/esquema_canonico.sql`. El laboratorio agrega únicamente una tabla técnica de control llamada `u5_autogest_control` y los diez objetos didácticos (cinco vistas, cinco funciones y cinco disparadores). Así, la base preparada contiene **7 tablas físicas en total**: seis de dominio y una de control. Los objetos `u5_*` están identificados para distinguirlos del esquema original.

## 1. Aislamiento obligatorio en Neon

1. En pgAdmin, dentro del **servidor experimental** de Neon, crea una base de datos **nueva y vacía** con el nombre `autogest_unidad5`.
2. No uses la base de datos original `concesionaria`, `concesionaria_dev`, `neondb` ni la de DaVinciMusic.
3. Crea una rama en tu repositorio de la concesionaria, por ejemplo `unidad_5_autogest`. La aplicación puede guardarse en `practicas/unidad5/`.
4. No ejecutes el SQL canónico manualmente antes de pulsar **Preparar base demo**; el instalador se encarga de hacerlo.

El backend **comprueba el nombre de la base dos veces**: en `DATABASE_URL` y mediante `SELECT current_database()`. No autoriza la preparación si no coincide con `UNIT5_ALLOWED_DATABASE`. Además, el nombre permitido debe incluir `unidad5`.

## 2. Backend · Windows · Python 3.13

Abre una terminal de PowerShell en `backend` y ejecuta:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita **`backend/.env`** y escribe la cadena **específica** de la nueva base experimental de Neon:

```dotenv
DATABASE_URL=postgresql+psycopg2://USUARIO:CONTRASEÑA@HOST/autogest_unidad5?sslmode=require
UNIT5_ALLOWED_DATABASE=autogest_unidad5
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> La URL es ilustrativa. Usa la conexión real que obtienes en Neon, escogiendo `autogest_unidad5`. Si Neon entrega `postgresql://`, cambia el prefijo a `postgresql+psycopg2://`. **Nunca subas `.env` a GitHub**.

Inicia FastAPI:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Verifica `http://127.0.0.1:8000/docs` o `http://127.0.0.1:8000/api/estado`.

## 3. Frontend · Windows · Node 22

En **otra terminal**, dentro de `frontend`:

```powershell
node -v
npm -v
npm ci
npm run build
npm run lint
Copy-Item .env.local.example .env.local
npm run dev
```

Abre **http://localhost:5173**. La variable `VITE_API_URL` tiene por defecto `http://127.0.0.1:8000`.

`npm run lint` es intencionalmente una **comprobación estricta de TypeScript**, no ESLint. El cambio está explicado en `SEGURIDAD_DEPENDENCIAS.md`.

## 4. Preparar la base e iniciar las prácticas

1. Verifica que el frontend muestre **Base experimental: autogest_unidad5** y conexión disponible.
2. Haz clic en **Preparar base demo** y acepta la confirmación.
3. Se ejecuta el DDL original dentro de una transacción, se insertan registros **ficticios** y se instalan las 5 vistas + 5 funciones/triggers.
4. Selecciona una categoría y un ejercicio; revisa el SQL, ajusta parámetros, pulsa **Ejecutar consulta** y observa los resultados.
5. Para `T01–T05`, cada demostración se ejecuta y **se revierte**; no se cambian de forma permanente los registros del laboratorio.

**No ejecutes el instalador sobre una base con datos preexistentes**. Las consultas de los primeros cuatro apartados son `SELECT` cerrados definidos en el backend: el navegador nunca envía SQL libre.

## 5. Datos ficticios y consideraciones sobre usuarios

El dataset contiene ejemplos de clientes, proveedores, personal, vehículos, ventas y revisiones, con dominios de correo `example.test`. Las filas de `usuario_interno` usan identificadores simulados `AUTOGEST-DEMO-NO-AUTH-*`: **no son usuarios de SuperTokens, no crean cuentas y no otorgan acceso al sistema real**.

Por ser una herramienta docente **local**, esta miniaplicación no incorpora sesiones, roles, login, endpoints de CRUD comercial, pagos ni controles de autorización de producción. El esquema canónico incluye reglas para el sistema real (validación de tokens, auditoría de identidades, autorización, etc.) que **no quedan implementadas para uso productivo en este laboratorio**. No publiques la API en Internet.

## 6. Qué se creó para la Unidad 5

| Objeto | Nombre | Función |
|---|---|---|
| Vista 1 | `v_u5_autos_proveedor` | Inventario y origen |
| Vista 2 | `v_u5_ventas_clientes` | Compradores, vehículos y ventas |
| Vista 3 | `v_u5_historial_revisiones` | Servicio técnico |
| Vista 4 | `v_u5_disponibilidad` | Venta vigente o disponible |
| Vista 5 | `v_u5_ventas_mensuales` | Ingresos por mes |
| Función + trigger T01 | `u5_fn_normalizar_auto` | Mayúsculas en serie/matrícula |
| Función + trigger T02 | `u5_fn_cliente_activo_venta` | Rechazar clientes inactivos |
| Función + trigger T03 | `u5_fn_kilometraje_coherente` | Evitar retroceso de odómetro |
| Función + trigger T04 | `u5_fn_venta_requiere_revision` | Revisión previa a venta |
| Función + trigger T05 | `u5_fn_venta_historica_inmutable` | Proteger datos históricos |

Las reglas de triggers son **demostraciones didácticas adicionales** al esquema, no equivalen a implementar íntegramente las doce políticas comerciales indicadas en los comentarios del DDL.

## 7. Errores comunes

- **503 al preparar**: revisa los detalles en la terminal del backend. Aquí se ejecuta el esquema completo **sin dividirlo por `;`**, porque el SQL incluye puntos y coma dentro de cadenas de texto.
- **La BD aparece como no conectada**: comprueba `DATABASE_URL`, SSL, permisos y acceso a Neon. La base autorizada debe ser exactamente `autogest_unidad5`.
- **409**: hay un esquema incompleto o tablas/registros ajenos. No se borran datos automáticamente; crea otra BD experimental vacía si corresponde.
- **Frontend no encuentra backend**: inicia FastAPI en el puerto 8000 y verifica `VITE_API_URL` y `FRONTEND_ORIGINS`.
- **Error npm `EAI_AGAIN` / `ETIMEDOUT`**: revisa la conectividad con el registro. No borres el lockfile ni utilices `npm audit fix --force`.

## 8. Comprobaciones

```powershell
# En backend (venv activado)
python -m pytest tests  # opcional: instala pytest en el venv

# En frontend
npm ci
npm run build
npm run lint
npm audit
npm audit --omit=dev
```

Los archivos incluyen **5 pruebas estáticas del catálogo/backend**. No se incluyen pruebas PostgreSQL de integración automatizadas; se deben verificar los ejercicios contra Neon con la base experimental. No se pudo ejecutar la instalación npm ni verificar las compilaciones TypeScript en el entorno de generación debido a falta de acceso a npmjs.org. Verifica los comandos anteriores en tu computadora.

## Estructura

```text
autogest_unidad5/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements_proyecto_original.txt
│   ├── sql/esquema_canonico.sql
│   ├── main.py
│   ├── app/catalog.py
│   ├── app/database.py
│   ├── app/objects.py
│   ├── app/seed.py
│   ├── app/setup.py
│   └── tests/test_catalog.py
├── frontend/
│   ├── .env.local.example
│   ├── package.json / package-lock.json
│   └── src/ (React / Vite / Tailwind / Base UI)
├── SEGURIDAD_DEPENDENCIAS.md
├── DISEÑO_UI.md
└── EVIDENCIAS.md
```
