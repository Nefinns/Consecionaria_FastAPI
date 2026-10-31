# Sustitución segura del backend — SuperTokens Managed

Este ZIP contiene el proyecto compartido con la integración del SDK oficial de SuperTokens y la administración de usuarios internos/roles. **No incluye pruebas automatizadas ni dependencias de desarrollo para pruebas.** No distribuye `.env`, `.venv`, `.git` ni credenciales; no cambia el SQL canónico.

## Respaldo y sustitución

1. En tu proyecto de Windows, confirma la rama `desarrollo_proyecto` y guarda tus cambios en GitHub con `git status`, `git add`, `git commit`, `git push` (sin versionar secretos ni el entorno virtual).
2. Haz también una copia local de la carpeta completa.
3. **No borres el directorio original**. El ZIP no trae `.git`, `backend/.env` ni `backend/.venv`, y esos archivos deben conservarse.
4. Descomprime el ZIP en una carpeta temporal y copia el **contenido** de `Concesionaria_fastapi/` a `D:\Concesionaria_fastapi\`, combinando carpetas y sustituyendo los archivos de código necesarios. Compara antes de sobrescribir cualquier cambio posterior al ZIP original.
5. Si ya habías aplicado una versión anterior del parche, puedes eliminar `backend/tests/` y `backend/requirements-dev.txt` de tu copia local: **ya no forman parte de esta entrega**.
6. Desde `D:\Concesionaria_fastapi\backend`, con tu `.venv` activo, ejecuta:

   ```powershell
   python -m pip check
   python -m uvicorn main:app --reload
   ```

   Ya instalaste las dependencias de la aplicación y `supertokens-python==0.31.4`: **no necesitas volver a ejecutar `pip install`** si todo sigue presente. Solo si Uvicorn informa que falta un paquete, instala las dependencias de `requirements.txt`.
7. Verifica manualmente `http://localhost:8000/health`, `/health/db`, `/health/auth`, `/docs` y `/ayuda/autenticacion`.
8. Sigue `backend/README_AUTENTICACION.md` para probar registro, login, permisos, logout y recuperación de contraseña.

## Alcance de la validación manual

Las pruebas de conexión `/health/db` y `/health/auth` no sustituyen las pruebas de flujos de sesión. Registra una identidad de prueba, confirma que no tenga acceso empresarial hasta autorizarla en `usuario_interno`, prueba un login y un logout y comprueba permisos de varios roles. El restablecimiento de contraseña requiere un cliente compatible o el futuro frontend React.

El backend incorpora los endpoints de autenticación del SDK de SuperTokens, pero **no incluye todavía formularios ni frontend React**, y el funcionamiento real contra tu Managed Core y Neon solo puede confirmarse en tu ambiente.
