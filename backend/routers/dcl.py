from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from psycopg2 import sql

from core.connections import obtener_engine, obtener_engine_admin
from core.dcl_config import dcl_usuarios, PERMISOS_OBJETIVO, TABLAS_CONCESIONARIA

router = APIRouter(prefix='/dcl', tags=['4.5 Administración de usuarios'])


class DatosUsuario(BaseModel):
    usuario: str
    contrasena: str = Field(min_length=12, max_length=128)


class DatosPermiso(BaseModel):
    usuario: str
    tabla: str
    operacion: str


def validar_usuario(usuario: str) -> str:
    if usuario not in dcl_usuarios:
        raise HTTPException(422, 'El usuario no está entre los 15 roles de la actividad.')
    return usuario


def validar_permiso(datos: DatosPermiso):
    usuario = validar_usuario(datos.usuario)
    tabla, operacion = PERMISOS_OBJETIVO[usuario]
    if (datos.tabla, datos.operacion.upper()) != (tabla, operacion):
        raise HTTPException(403, f'Permiso de práctica permitido: {operacion} en {tabla}.')
    return usuario, tabla, operacion


@router.get('/configuracion')
def configuracion():
    return {
        'usuarios': [
            {'usuario': nombre, 'descripcion': dcl_usuarios[nombre], 'tabla': tabla, 'operacion': accion}
            for nombre, (tabla, accion) in PERMISOS_OBJETIVO.items()
        ],
        'tablas': list(TABLAS_CONCESIONARIA),
    }


@router.get('/usuarios')
def listar_usuarios():
    with obtener_engine_admin().connect() as conexion:
        filas = conexion.execute(text('SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname = ANY(:nombres)'),
                                 {'nombres': list(dcl_usuarios)}).mappings().all()
    presentes = {f['rolname']: f['rolcanlogin'] for f in filas}
    return {'usuarios': [
        {'usuario': u, 'descripcion': desc, 'existe': u in presentes,
         'puede_iniciar_sesion': presentes.get(u, False),
         'tabla': PERMISOS_OBJETIVO[u][0], 'operacion': PERMISOS_OBJETIVO[u][1]}
        for u, desc in dcl_usuarios.items()
    ]}


@router.post('/crear_usuario')
def crear_usuario(datos: DatosUsuario):
    usuario = validar_usuario(datos.usuario)
    try:
        # CREATE ROLE requiere permiso CREATEROLE; es una operación del clúster PostgreSQL.
        with obtener_engine_admin().begin() as conexion:
            existe = conexion.execute(text('SELECT 1 FROM pg_roles WHERE rolname=:u'), {'u': usuario}).scalar()
            if existe:
                raise HTTPException(409, f'El usuario {usuario} ya existe.')
            raw = conexion.connection.driver_connection
            with raw.cursor() as cursor:
                cursor.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(
                    sql.Identifier(usuario), sql.Literal(datos.contrasena)
                ))
        # GRANT USAGE es por base de datos, no por clúster.
        with obtener_engine().begin() as conexion:
            conexion.exec_driver_sql(f'GRANT USAGE ON SCHEMA public TO "{usuario}"')
        return {'mensaje': f'Usuario {usuario} creado y con USAGE en public.'}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(400, f'PostgreSQL rechazó la creación del rol: {type(e.orig).__name__ if getattr(e, "orig", None) else type(e).__name__}. Revisa CREATEROLE/GRANT.') from e


@router.post('/grant')
def grant(datos: DatosPermiso):
    usuario, tabla, operacion = validar_permiso(datos)
    try:
        with obtener_engine().begin() as conexion:
            if not conexion.execute(text('SELECT 1 FROM pg_roles WHERE rolname=:u'), {'u': usuario}).scalar():
                raise HTTPException(404, 'Primero crea el usuario.')
            if not conexion.execute(text('SELECT to_regclass(:t)'), {'t': f'public.{tabla}'}).scalar():
                raise HTTPException(404, 'Primero crea las tablas de Concesionaria.')
            conexion.exec_driver_sql(f'GRANT USAGE ON SCHEMA public TO "{usuario}"')
            conexion.exec_driver_sql(f'GRANT {operacion} ON TABLE public."{tabla}" TO "{usuario}"')
        return {'mensaje': f'GRANT {operacion} ON {tabla} TO {usuario} ejecutado.'}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(400, f'No se pudo conceder el permiso ({type(e).__name__}).') from e


@router.post('/revoke')
def revoke(datos: DatosPermiso):
    usuario, tabla, operacion = validar_permiso(datos)
    try:
        with obtener_engine().begin() as conexion:
            conexion.exec_driver_sql(f'REVOKE {operacion} ON TABLE public."{tabla}" FROM "{usuario}"')
        return {'mensaje': f'REVOKE {operacion} ON {tabla} FROM {usuario} ejecutado.'}
    except SQLAlchemyError as e:
        raise HTTPException(400, f'No se pudo revocar el permiso ({type(e).__name__}).') from e


@router.get('/permisos/{usuario}')
def permisos(usuario: str):
    validar_usuario(usuario)
    with obtener_engine().connect() as conexion:
        filas = conexion.execute(text('''
            SELECT table_name, privilege_type, is_grantable
            FROM information_schema.role_table_grants
            WHERE table_schema='public' AND grantee=:usuario
            ORDER BY table_name, privilege_type
        '''), {'usuario': usuario}).mappings().all()
    return {'usuario': usuario, 'permisos': [dict(x) for x in filas]}
