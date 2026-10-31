# Backend de autenticación — Concesionaria

## Alcance y arquitectura

Este proyecto utiliza **SuperTokens Managed** para registro, inicio/cierre de sesión,
renovación de sesiones y recuperación de contraseña. Las rutas oficiales son servidas
por el middleware del SDK Python instalado en FastAPI. **No hay contraseñas, hashes,
tokens ni tablas de sesiones propias en PostgreSQL.**

PostgreSQL Neon contiene las seis tablas canónicas, incluida `usuario_interno` con
`identidad_externa` (SuperTokens **User ID**) y un rol fijo: `administrador`, `gerente`
o `mecanico`. **Registrarse en SuperTokens NO concede acceso a módulos internos**;
solo `usuario_interno.activo = TRUE` da acceso al perfil y, según el rol, a la
administración. Todos los permisos se validan en FastAPI.

**Seguridad importante:** el registro de identidad está abierto en este MVP. Las
cuentas recién registradas son **no autorizadas** para el negocio y reciben 403.
Para usarlo con empleados reales, restringir el registro mediante un proceso de
invitación autorizado y verificar el correo electrónico (EmailVerification) antes
de vincular una identidad. No se ha implementado todavía esa función.

## Preparación

1. Respaldar el directorio y hacer commit/push en `desarrollo_proyecto` antes de
   sustituir archivos.
2. NO copiar `.env`, `.venv` ni `.git` desde un ZIP. Conservar los existentes.
3. Comprobar `backend/.env` (sin compartir valores):

   ```dotenv
   DATABASE_URL=<cadena real ya existente, con sslmode=require>
   SUPERTOKENS_CONNECTION_URI=https://<URI de Managed>
   SUPERTOKENS_API_KEY=<clave privada>
   API_DOMAIN=http://localhost:8000
   WEBSITE_DOMAIN=http://localhost:5173
   ```

4. Desde `D:\Concesionaria_fastapi\backend` con tu entorno virtual ya configurado:

   ```powershell
   python -m pip check
   python -m uvicorn main:app --reload
   ```

   No necesitas reinstalar dependencias si ya tienes FastAPI, Neon y
   `supertokens-python==0.31.4` en `.venv`.

5. Abrir `http://localhost:8000/health`, `/health/db`, `/health/auth`, `/docs` y
   `/ayuda/autenticacion`. Swagger documenta rutas del negocio, **no** registra
   automáticamente rutas creadas por el SDK; estas se consultan en la guía.

6. Realizar la **validación manual** descrita al final de este documento; esta entrega no incluye herramientas ni archivos de pruebas automatizadas.

## Endpoints de SuperTokens (no duplicados en la aplicación)

Son rutas integradas por la receta `EmailPassword` y `Session` bajo `/auth`:

| Función | Método / ruta |
|---|---|
| Registro | `POST /auth/signup` |
| Inicio de sesión | `POST /auth/signin` |
| Salida | `POST /auth/signout` |
| Renovar sesión | `POST /auth/session/refresh` |
| Solicitar correo recuperación | `POST /auth/user/password/reset/token` |
| Restablecer contraseña con token | `POST /auth/user/password/reset` |

Para llamar directamente estos endpoints hay que seguir el formato de solicitud de
la **Frontend Driver Interface** de SuperTokens (cabeceras `rid`, `fdi-version`,
`formFields` y gestión de cookies/anti-CSRF). La forma recomendada es usar el SDK
oficial `supertokens-auth-react` desde React. React solo muestra formularios;
**FastAPI valida credenciales/sesiones a través del SDK y protege operaciones**.
El correo de recuperación enlaza a `WEBSITE_DOMAIN/auth/reset-password`, por lo
que para demostrar el flujo completo se necesita la UI React o una página equivalente.
El proveedor de envío de correo predeterminado puede imponer límites.

Es preferible usar **localhost** tanto en frontend como en backend para que las
cookies se comporten correctamente. No mezclar localhost y 127.0.0.1.

## Primer administrador: alta controlada en PostgreSQL

No existe registro automático de privilegios. Después de registrar la primera
identidad en SuperTokens, obtener su **User ID** estable del Dashboard (no correo,
ni sesión, ni token). En pgAdmin conectado a `concesionaria_dev`, comprobar que
`usuario_interno` está vacía o revisar el estado antes de insertar:

```sql
-- Sustituir el marcador por el User ID real y confirmar la identidad
BEGIN;
INSERT INTO usuario_interno (identidad_externa, nombre, rol, activo)
VALUES ('REEMPLAZAR_POR_USER_ID_REAL', 'Administrador inicial', 'administrador', TRUE);
-- Antes de COMMIT verificar con SELECT (en la misma pestaña de pgAdmin)
SELECT id_usuario, identidad_externa, nombre, rol, activo
FROM usuario_interno WHERE rol = 'administrador';
COMMIT;
```

**No ejecutar el ejemplo con el marcador**. No registrar contraseñas ni claves del
servicio Managed en la base de negocio. El bootstrap es un procedimiento de
administración privilegiada externo a la API: no hay endpoint público que cree admins.

## Usuarios y roles en API

| Ruta | Rol |
|---|---|
| `GET /usuarios/me` | cualquiera de los 3, si activo |
| `GET /usuarios?offset=0&limit=50` | administrador |
| `GET /usuarios/{id_usuario}` | administrador |
| `POST /usuarios` | administrador |
| `PATCH /usuarios/{id_usuario}` | administrador |

`POST /usuarios` **vincula únicamente una identidad que ya existe en SuperTokens**.
No crea contraseñas ni genera automáticamente una invitación. JSON de ejemplo:

```json
{
  "identidad_externa": "USER_ID_REAL_DEL_DASHBOARD",
  "nombre": "Empleado demo",
  "rol": "gerente"
}
```

Solo se admiten los roles `administrador`, `gerente`, `mecanico`. El PATCH permite
cambiar `nombre`, `rol` y `activo`; nunca el identificador externo, que debe ser
inmutable. No hay eliminación física. Se rechaza autodesactivación, autopérdida
 de privilegios y eliminación del último administrador activo. El control sobre
el último administrador utiliza bloqueo de filas en PostgreSQL.

## Matriz de pruebas manuales en ambiente de desarrollo

1. `GET /health` = 200; `/health/db` = 200 y `/health/auth` = 200
   (conexión efectiva al Core). No hay cambios en el esquema.
2. Registro por SDK: la nueva identidad aparece en SuperTokens Managed.
3. Login válido: SuperTokens establece la sesión. Un login erróneo no la establece.
4. `GET /usuarios/me` de cuenta **sin** fila autorizada = 403.
5. Alta bootstrap con pgAdmin; misma sesión = `/usuarios/me` 200.
6. Una cuenta de `mecanico` intentando `GET /usuarios` = 403.
7. Administrador puede listar y vincular User IDs reales. ID inexistente = 422.
8. Se rechazan roles inválidos, campos vacíos y registros duplicados.
9. Admin no puede desactivarse ni degradarse; otra cuenta activa sin privilegios
   no accede a gestión de usuarios inmediatamente.
10. Logout por SDK revoca la sesión; solicitud protegida posterior = 401.
11. Restablecimiento: solicitar correo, abrir enlace en frontend y elegir contraseña
    nueva; se rechaza la anterior. La aplicación **no registra enlaces ni tokens**.
12. Renovación automática: el SDK del frontend gestiona la sesión expirada.

## Qué NO hace este parche

- No incluye aún frontend ni formularios React.
- No implementa CRUD de clientes, coches, revisiones, proveedores o ventas.
- No automatiza provisión/invitación de personal ni verifica correos por sí mismo.
- No cambia el SQL canónico ni crea tablas nuevas.
- No confirma que tu instancia Managed real sea accesible: falta prueba con tus secretos.

La fuente de referencia de los endpoints SDK es:
https://supertokens.com/docs/quickstart y
https://supertokens.com/docs/authentication/email-password/password-reset
