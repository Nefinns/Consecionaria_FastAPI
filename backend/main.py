"""API FastAPI; las tablas PostgreSQL existentes nunca se crean al arrancar."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from supertokens_python import get_all_cors_headers
from supertokens_python.asyncio import get_user_count
from supertokens_python.framework.fastapi import get_middleware

from app.api.routes.info import router as ayuda_router
from app.api.routes.usuarios import router as usuarios_router
from app.core.config import obtener_database_url
from app.core.supertokens import configuracion_auth, iniciar_supertokens
from app.db.sesion import cerrar_motor, obtener_motor

# SuperTokens debe iniciarse antes de crear el middleware y consultar cabeceras CORS.
iniciar_supertokens()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Validar formato de configuración sin abrir conexiones de BD anticipadas."""
    obtener_database_url()
    try:
        yield
    finally:
        cerrar_motor()


app = FastAPI(title="Concesionaria API", version="0.3.0", lifespan=lifespan)
app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracion_auth()["WEBSITE_DOMAIN"]],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=list(dict.fromkeys(["Content-Type", "Authorization"] + get_all_cors_headers())),
)
app.include_router(usuarios_router)
app.include_router(ayuda_router)


@app.get("/", tags=["Estado"])
def inicio():
    return {"mensaje": "API de la concesionaria funcionando"}


@app.get("/health", tags=["Estado"])
def comprobar_api():
    return {"status": "ok"}


@app.get("/health/db", tags=["Estado"])
def comprobar_base_datos():
    try:
        with obtener_motor().connect() as conexion:
            resultado = conexion.execute(
                text("SELECT 1 AS resultado, current_database() AS base")
            ).one()
        if resultado.resultado != 1 or resultado.base != obtener_database_url().database:
            raise HTTPException(status_code=503, detail="Base de datos no disponible.")
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Base de datos no disponible.") from None
    return {"status": "ok", "database": "conectada"}


@app.get("/health/auth", tags=["Estado"])
async def comprobar_servicio_autenticacion():
    """Probar conectividad real al Core sin revelar claves ni el número de cuentas."""
    try:
        await get_user_count()
    except Exception:
        raise HTTPException(status_code=503, detail="Servicio de autenticación no disponible.") from None
    return {"status": "ok", "auth": "conectada"}
