
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from core.connections import (
    crear_base,
    seleccionar_base,
    obtener_engine,
    obtener_base_seleccionada,
    listar_bases,
)

router = APIRouter(prefix="/db", tags=["Bases de datos"])


class DatosBaseDatos(BaseModel):
    nombre: str = Field(
        min_length=3,
        max_length=63,
        pattern=r"^[a-z][a-z0-9_]{2,62}$",
    )


@router.get("/listar")
def listar_bases_datos():
    return {
        "bases_datos": listar_bases(),
        "seleccionada": obtener_base_seleccionada(),
    }


@router.post("/crear")
def endpoint_crear_base(datos: DatosBaseDatos):
    return crear_base(datos.nombre)


@router.post("/seleccionar/{nombre}")
def endpoint_seleccionar_base(nombre: str):
    return seleccionar_base(nombre)


@router.get("/seleccionada")
def consultar_base_seleccionada():
    nombre = obtener_base_seleccionada()

    if nombre is None:
        raise HTTPException(
            status_code=409,
            detail="No hay una base de datos seleccionada.",
        )

    return {"base_datos": nombre}


@router.get("/test")
def probar_conexion():
    engine = obtener_engine()

    with engine.connect() as conexion:
        nombre = conexion.execute(
            text("SELECT current_database()")
        ).scalar_one()

        version = conexion.execute(
            text("SELECT version()")
        ).scalar_one()

    return {
        "conexion": "correcta",
        "base_datos": nombre,
        "version_postgresql": version,
    }
