
import os
import re
from threading import RLock

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_ADMIN_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Define DATABASE_URL o DATABASE_ADMIN_URL en el archivo .env"
    )

url_admin = make_url(DATABASE_URL)

engine_admin = create_engine(
    url_admin,
    isolation_level="AUTOCOMMIT",
    pool_pre_ping=True,
)

_engine: Engine | None = None
_base_seleccionada: str | None = None
_lock_bd = RLock()

PATRON_NOMBRE_BD = re.compile(r"^[a-z][a-z0-9_]{2,62}$")


def obtener_engine() -> Engine:
    with _lock_bd:
        if _engine is None:
            raise HTTPException(
                status_code=409,
                detail="Primero debes seleccionar una base de datos.",
            )
        return _engine


def obtener_engine_admin() -> Engine:
    return engine_admin


def obtener_base_seleccionada() -> str | None:
    with _lock_bd:
        return _base_seleccionada


def validar_nombre_bd(nombre: str) -> str:
    if not PATRON_NOMBRE_BD.fullmatch(nombre):
        raise HTTPException(
            status_code=422,
            detail=(
                "Nombre inválido. Usa entre 3 y 63 caracteres: "
                "letras minúsculas, números y guion bajo; "
                "debe comenzar con una letra."
            ),
        )
    return nombre


def existe_base(nombre: str) -> bool:
    with engine_admin.connect() as conexion:
        resultado = conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nombre"),
            {"nombre": nombre},
        )
        return resultado.scalar_one_or_none() is not None


def seleccionar_base(nombre: str) -> dict:
    global _engine, _base_seleccionada

    validar_nombre_bd(nombre)

    if not existe_base(nombre):
        raise HTTPException(
            status_code=404,
            detail=f"La base de datos '{nombre}' no existe.",
        )

    nuevo_engine = create_engine(
        url_admin.set(database=nombre),
        pool_pre_ping=True,
    )

    try:
        with nuevo_engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
    except Exception:
        nuevo_engine.dispose()
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible conectarse a la base '{nombre}'.",
        )

    with _lock_bd:
        engine_anterior = _engine
        _engine = nuevo_engine
        _base_seleccionada = nombre

    if engine_anterior is not None:
        engine_anterior.dispose()

    return {
        "base_datos": nombre,
        "seleccionada": True,
        "conexion": "correcta",
    }


def crear_base(nombre: str) -> dict:
    validar_nombre_bd(nombre)

    if existe_base(nombre):
        raise HTTPException(
            status_code=409,
            detail=f"La base de datos '{nombre}' ya existe.",
        )

    # El nombre está validado y se delimita como identificador SQL.
    nombre_sql = f'"{nombre}"'

    try:
        with engine_admin.connect() as conexion:
            conexion.execute(text(f"CREATE DATABASE {nombre_sql}"))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo crear la base de datos: {error}",
        )

    return seleccionar_base(nombre)


def listar_bases() -> list[str]:
    with engine_admin.connect() as conexion:
        resultado = conexion.execute(
            text(
                """
                SELECT datname
                FROM pg_database
                WHERE datistemplate = FALSE
                  AND datallowconn = TRUE
                ORDER BY datname
                """
            )
        )
        return list(resultado.scalars().all())


def cerrar_conexiones() -> None:
    global _engine

    with _lock_bd:
        engine_actual = _engine
        _engine = None

    if engine_actual is not None:
        engine_actual.dispose()

    engine_admin.dispose()
