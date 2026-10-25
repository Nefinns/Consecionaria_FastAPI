from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import obtener_database_url
from app.db.sesion import cerrar_motor, obtener_motor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Valida la configuración sin conectarse todavía a PostgreSQL.
    obtener_database_url()

    try:
        yield
    finally:
        cerrar_motor()


app = FastAPI(
    title="Concesionaria API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Estado"])
def inicio():
    return {
        "mensaje": "API de la concesionaria funcionando"
    }


@app.get("/health", tags=["Estado"])
def comprobar_api():
    return {"status": "ok"}


@app.get("/health/db", tags=["Estado"])
def comprobar_base_datos():
    try:
        with obtener_motor().connect() as conexion:
            resultado = conexion.execute(
                text(
                    "SELECT 1 AS resultado, "
                    "current_database() AS base"
                )
            ).one()

        base_esperada = obtener_database_url().database

        if (
            resultado.resultado != 1
            or resultado.base != base_esperada
        ):
            raise HTTPException(
                status_code=503,
                detail="Base de datos no disponible.",
            )

    except SQLAlchemyError:
        # Evita devolver credenciales o detalles del servidor.
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible.",
        ) from None

    return {
        "status": "ok",
        "database": "conectada",
    }