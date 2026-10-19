
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.connections import (
    obtener_engine,
    obtener_base_seleccionada,
)
from core.ddl import ddl_create, ddl_indices, ddl_drop

router = APIRouter(
    prefix="/ddl",
    tags=["DDL - Tablas y restricciones"],
)


@router.get("/estado")
def estado_esquema():
    engine = obtener_engine()

    try:
        with engine.connect() as conexion:
            tablas = conexion.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
            ).scalars().all()

            restricciones = conexion.execute(
                text(
                    """
                    SELECT
                        tc.table_name,
                        tc.constraint_name,
                        tc.constraint_type
                    FROM information_schema.table_constraints AS tc
                    WHERE tc.table_schema = 'public'
                    ORDER BY
                        tc.table_name,
                        tc.constraint_type,
                        tc.constraint_name
                    """
                )
            ).mappings().all()

            indices = conexion.execute(
                text(
                    """
                    SELECT tablename, indexname
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                    """
                )
            ).mappings().all()

        return {
            "base_datos": obtener_base_seleccionada(),
            "tablas": list(tablas),
            "total_tablas": len(tablas),
            "restricciones": [
                dict(fila) for fila in restricciones
            ],
            "indices": [
                dict(fila) for fila in indices
            ],
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo consultar el esquema: {error}",
        )


@router.post("/create-all")
@router.post("/create-all")
def crear_esquema_completo():
    if not ddl_create:
        raise HTTPException(
            status_code=409,
            detail="No hay tablas configuradas para crear."
        )

    engine = obtener_engine()

    try:
        with engine.begin() as conexion:

            existentes = set(
                conexion.execute(
                    text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE'
                    """)
                ).scalars().all()
            )

            configuradas = set(ddl_create.keys())
            duplicadas = sorted(existentes & configuradas)

            if duplicadas:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Ya existen tablas de Concesionaria: "
                        + ", ".join(duplicadas)
                    )
                )

            for sentencia in ddl_create.values():
                conexion.execute(text(sentencia))

            for sentencia in ddl_indices.values():
                conexion.execute(text(sentencia))

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el esquema: {error}"
        )

    return {
        "mensaje": "Esquema creado correctamente.",
        "tablas_creadas": len(ddl_create),
        "indices_creados": len(ddl_indices),
    }

@router.post("/drop-all")
def eliminar_esquema_completo():
    if not ddl_drop:
        raise HTTPException(
            status_code=409,
            detail="El DROP está deshabilitado hasta adaptar el esquema de Concesionaria.",
        )
    engine = obtener_engine()

    try:
        with engine.begin() as conexion:
            for nombre, sentencia in ddl_drop.items():
                conexion.execute(text(sentencia))

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo eliminar el esquema completo. "
                f"Tipo: {type(error).__name__}. "
                f"Detalle: {error}"
            ),
        )

    return {
        "mensaje": "Se eliminaron las tablas configuradas.",
        "tablas_eliminadas": len(ddl_drop),
        "base_datos": obtener_base_seleccionada(),
    }


@router.post("/create/{tabla}")
def crear_tabla(tabla: str):
    sentencia = ddl_create.get(tabla)

    if sentencia is None:
        raise HTTPException(
            status_code=404,
            detail=f"La tabla '{tabla}' no está definida.",
        )

    engine = obtener_engine()

    try:
        with engine.begin() as conexion:
            conexion.execute(text(sentencia))

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"No se pudo crear la tabla '{tabla}'. "
                f"Tipo: {type(error).__name__}. "
                f"Detalle: {error}"
            ),
        )

    return {
        "mensaje": f"Tabla '{tabla}' creada correctamente."
    }


@router.post("/drop/{tabla}")
def eliminar_tabla(tabla: str):
    sentencia = ddl_drop.get(tabla)

    if sentencia is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"La tabla '{tabla}' no está definida "
                "para eliminación."
            ),
        )

    engine = obtener_engine()

    try:
        with engine.begin() as conexion:
            conexion.execute(text(sentencia))

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"No se pudo eliminar la tabla '{tabla}'. "
                f"Tipo: {type(error).__name__}. "
                f"Detalle: {error}"
            ),
        )

    return {
        "mensaje": f"Tabla '{tabla}' eliminada correctamente."
    }
