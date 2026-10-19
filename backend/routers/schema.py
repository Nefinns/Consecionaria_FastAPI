import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.connections import obtener_engine, obtener_base_seleccionada
from core.ddl import ddl_create, ddl_indices, ddl_drop, datos_prueba

router = APIRouter(prefix='/ddl', tags=['4.1-4.3 Esquema y restricciones'])


@router.get('/estado')
def estado_esquema():
    with obtener_engine().connect() as conexion:
        tablas = conexion.execute(text('''
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name
        ''')).scalars().all()
        restricciones = conexion.execute(text('''
            SELECT table_name, constraint_name, constraint_type
            FROM information_schema.table_constraints WHERE table_schema='public'
            ORDER BY table_name, constraint_type, constraint_name
        ''')).mappings().all()
        indices = conexion.execute(text('''
            SELECT tablename, indexname FROM pg_indexes WHERE schemaname='public'
            ORDER BY tablename, indexname
        ''')).mappings().all()
    return {'base_datos': obtener_base_seleccionada(), 'tablas': list(tablas),
            'total_tablas': len(tablas), 'restricciones': [dict(row) for row in restricciones],
            'total_restricciones': len(restricciones), 'indices': [dict(row) for row in indices],
            'total_indices': len(indices)}


@router.post('/create-all')
def crear_esquema_completo():
    if len(ddl_create) != 8 or len(ddl_indices) != 8:
        raise HTTPException(409, 'Se esperaban ocho tablas e índices específicos de Concesionaria.')
    engine = obtener_engine()
    try:
        with engine.begin() as conexion:
            existentes = set(conexion.execute(text('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE'
            ''')).scalars().all())
            if existentes:
                raise HTTPException(409, 'La base ya contiene tablas: ' + ', '.join(sorted(existentes)) + '. Usa una base vacía.')
            for sentencia in ddl_create.values():
                conexion.execute(text(sentencia))
            for sentencia in ddl_indices.values():
                conexion.execute(text(sentencia))
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(400, f'No se pudo crear el esquema ({type(e).__name__}). Revisa permisos y SQL.') from e
    return {'mensaje': 'Esquema de Concesionaria creado.', 'tablas_creadas': 8,
            'indices_creados': len(ddl_indices), 'base_datos': obtener_base_seleccionada()}


class ConfirmacionDDL(BaseModel):
    confirmacion: str


@router.post('/drop-all')
def eliminar_esquema_completo(datos: ConfirmacionDDL):
    if os.getenv('ENABLE_DESTRUCTIVE_DDL', 'false').lower() != 'true':
        raise HTTPException(403, 'DROP deshabilitado por defecto. Configura ENABLE_DESTRUCTIVE_DDL=true en el servidor.')
    if datos.confirmacion != 'ELIMINAR_OCHO_TABLAS':
        raise HTTPException(422, 'Debes confirmar ELIMINAR_OCHO_TABLAS.')
    try:
        with obtener_engine().begin() as conexion:
            for sentencia in ddl_drop.values():
                conexion.execute(text(sentencia))
    except SQLAlchemyError as e:
        raise HTTPException(409, f'No se pudieron eliminar las tablas ({type(e).__name__}).') from e
    return {'mensaje': 'Se eliminaron las ocho tablas.', 'tablas_eliminadas': len(ddl_drop)}


@router.post('/create/{tabla}')
def crear_tabla(tabla: str):
    if tabla not in ddl_create:
        raise HTTPException(404, 'Tabla desconocida.')
    try:
        with obtener_engine().begin() as conexion:
            conexion.execute(text(ddl_create[tabla]))
    except SQLAlchemyError as e:
        raise HTTPException(409, f'Error al crear tabla ({type(e).__name__}).') from e
    return {'mensaje': f'Tabla {tabla} creada.'}


@router.post('/drop/{tabla}')
def eliminar_tabla(tabla: str, datos: ConfirmacionDDL):
    if os.getenv('ENABLE_DESTRUCTIVE_DDL', 'false').lower() != 'true':
        raise HTTPException(403, 'DROP deshabilitado por defecto.')
    if tabla not in ddl_drop or datos.confirmacion != 'ELIMINAR_OCHO_TABLAS':
        raise HTTPException(422, 'Tabla o confirmación no válida.')
    try:
        with obtener_engine().begin() as conexion:
            conexion.execute(text(ddl_drop[tabla]))
    except SQLAlchemyError as e:
        raise HTTPException(409, f'No se pudo eliminar tabla ({type(e).__name__}).') from e
    return {'mensaje': f'Tabla {tabla} eliminada.'}


@router.get('/datos-prueba/estado')
def estado_datos_prueba():
    """Cuenta registros de las tablas para evitar inserciones duplicadas."""
    with obtener_engine().connect() as conexion:
        actuales = set(conexion.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")).scalars())
        faltantes = sorted(set(ddl_create) - actuales)
        conteos = {tabla: conexion.execute(text(f'SELECT COUNT(*) FROM public."{tabla}"')).scalar_one()
                   for tabla in ddl_create if tabla in actuales}
    return {'faltantes': faltantes, 'conteos': conteos, 'total_registros': sum(conteos.values()),
            'puede_cargar': not faltantes and not any(conteos.values())}


@router.post('/datos-prueba')
def cargar_datos_prueba():
    """Carga una vez los 43 registros originales en una sola transacción."""
    try:
        with obtener_engine().begin() as conexion:
            actuales = set(conexion.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")).scalars())
            if set(ddl_create) - actuales:
                raise HTTPException(409, 'Primero crea las ocho tablas.')
            for nombre in ddl_create:
                count = conexion.execute(text(f'SELECT COUNT(*) FROM public."{nombre}"')).scalar_one()
                if count:
                    raise HTTPException(409, 'Solo se pueden cargar datos cuando las ocho tablas están vacías.')
            for sql_insert in datos_prueba.values():
                conexion.execute(text(sql_insert))
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(409, f'No se pudieron insertar los datos de prueba ({type(e).__name__}).') from e
    return {'mensaje': 'Se cargaron los datos originales en ocho tablas.',
            'registros_insertados': 43}
