
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.connections import obtener_engine, obtener_engine_admin
from core.dcl_config import (
    dcl_usuarios,
    dcl_grant,
    dcl_revoke,
    TABLAS_PERMITIDAS,
    OPERACIONES_PERMITIDAS,
)

router = APIRouter(prefix="/dcl", tags=["DCL - Usuarios y permisos"])

PATRON_ROL = re.compile(r"^[a-z][a-z0-9_]{2,62}$")


class DatosUsuario(BaseModel):
    usuario: str = Field(min_length=3, max_length=63)
    contrasena: str = Field(min_length=12, max_length=128)


class DatosPermiso(BaseModel):
    usuario: str
    tabla: str
    operacion: str


def validar_rol(usuario: str) -> str:
    if usuario not in dcl_usuarios or not PATRON_ROL.fullmatch(usuario):
        raise HTTPException(
            status_code=400,
            detail="El rol no está permitido en la configuración.",
        )
    return usuario


def validar_permiso(datos: DatosPermiso) -> tuple[str, str, str]:
    usuario = validar_rol(datos.usuario)
    tabla = datos.tabla.lower()
    operacion = datos.operacion.upper()

    if tabla not in TABLAS_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="La tabla indicada no está permitida.",
        )

    if operacion not in OPERACIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="La operación indicada no está permitida.",
        )

    return usuario, tabla, operacion


@router.get("/usuarios")
def listar_roles():
    engine = obtener_engine_admin()

    with engine.connect() as conexion:
        filas = conexion.execute(
            text(
                """
                SELECT rolname, rolsuper, rolcreatedb, rolcreaterole,
                       rolcanlogin
                FROM pg_roles
                WHERE rolname NOT LIKE 'pg_%'
                ORDER BY rolname
                """
            )
        ).mappings().all()

    return {"usuarios": [dict(fila) for fila in filas]}


@router.post("/crear_usuario")
def crear_usuario(datos: DatosUsuario):
    usuario = validar_rol(datos.usuario)
    engine = obtener_engine_admin()

    try:
        with engine.begin() as conexion:
            existe = conexion.execute(
                text(
                    "SELECT 1 FROM pg_roles WHERE rolname = :usuario"
                ),
                {"usuario": usuario},
            ).scalar_one_or_none()

            if existe:
                raise HTTPException(
                    status_code=409,
                    detail=f"El rol '{usuario}' ya existe.",
                )

            conexion.execute(
                text(
                    f'CREATE ROLE "{usuario}" '
                    "LOGIN PASSWORD :contrasena"
                ),
                {"contrasena": datos.contrasena},
            )

    except HTTPException:
        raise
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo crear el rol: {error}",
        )

    return {"mensaje": f"Rol '{usuario}' creado correctamente."}


@router.post("/grant")
def conceder_permiso(datos: DatosPermiso):
    usuario, tabla, operacion = validar_permiso(datos)

    if operacion not in dcl_grant.get(usuario, []):
        raise HTTPException(
            status_code=403,
            detail="La operación no está permitida para este rol.",
        )

    engine = obtener_engine()

    try:
        with engine.begin() as conexion:
            conexion.exec_driver_sql(
                f'GRANT {operacion} ON TABLE public."{tabla}" '
                f'TO "{usuario}"'
            )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo conceder el permiso: {error}",
        )

    return {
        "mensaje": "Permiso concedido.",
        "usuario": usuario,
        "tabla": tabla,
        "operacion": operacion,
    }


@router.post("/revoke")
def revocar_permiso(datos: DatosPermiso):
    usuario, tabla, operacion = validar_permiso(datos)

    if operacion not in dcl_revoke.get(usuario, []):
        raise HTTPException(
            status_code=403,
            detail="La operación no está permitida para este rol.",
        )

    engine = obtener_engine()

    try:
        with engine.begin() as conexion:
            conexion.exec_driver_sql(
                f'REVOKE {operacion} ON TABLE public."{tabla}" '
                f'FROM "{usuario}"'
            )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo revocar el permiso: {error}",
        )

    return {
        "mensaje": "Permiso revocado.",
        "usuario": usuario,
        "tabla": tabla,
        "operacion": operacion,
    }


@router.get("/permisos/{usuario}")
def consultar_permisos(usuario: str):
    usuario = validar_rol(usuario)
    engine = obtener_engine()

    with engine.connect() as conexion:
        filas = conexion.execute(
            text(
                """
                SELECT table_name, privilege_type, grantable
                FROM information_schema.role_table_grants
                WHERE table_schema = 'public'
                  AND grantee = :usuario
                ORDER BY table_name, privilege_type
                """
            ),
            {"usuario": usuario},
        ).mappings().all()

    return {
        "usuario": usuario,
        "permisos": [dict(fila) for fila in filas],
    }


@router.get("/configuracion")
def consultar_configuracion_dcl():
    return {
        "usuarios": dcl_usuarios,
        "permisos_grant": dcl_grant,
        "permisos_revoke": dcl_revoke,
    }
