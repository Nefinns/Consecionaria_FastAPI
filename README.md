# Concesionaria — Mini proyecto administrativo

## Estructura del repositorio

- `backend/`: API FastAPI + SuperTokens Managed + autorización por roles.
- `docs/`: alcance, diagramas Mermaid y SQL canónico PostgreSQL para Neon.
- `concesionaria.sql`, `consultas.py`: **material académico heredado**; no forma
  parte de la API nueva. No ejecutar sobre `concesionaria_dev`.

Para instalar, arrancar y probar autenticación, leer
[backend/README_AUTENTICACION.md](backend/README_AUTENTICACION.md).

Los secretos `backend/.env` y el entorno `.venv` **no se distribuyen**.
Solo se trabaja en la rama de desarrollo. Aún no se incluye frontend.
