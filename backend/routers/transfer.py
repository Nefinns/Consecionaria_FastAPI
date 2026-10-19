"""4.6 Importación y exportación CSV; migración de datos a MySQL 8.
No usa SQLines. Requiere una base MySQL nueva y vacía.
"""
import csv
import io
import os
import re
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from core.connections import obtener_engine, obtener_base_seleccionada
from core.dcl_config import TABLAS_CONCESIONARIA

router = APIRouter(prefix='/transfer', tags=['4.6 Importar, exportar y migrar'])
ORDEN = list(TABLAS_CONCESIONARIA)


def tabla_valida(nombre: str):
    if nombre not in ORDEN:
        raise HTTPException(422, 'Tabla no autorizada.')
    return nombre


def verificar_tablas():
    existentes = set(inspect(obtener_engine()).get_table_names(schema='public'))
    faltantes = sorted(set(ORDEN) - existentes)
    if faltantes:
        raise HTTPException(409, f'Faltan tablas en PostgreSQL: {", ".join(faltantes)}')


def cantidad(engine, tabla):
    with engine.connect() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM "{tabla}"')).scalar_one()


@router.get('/tablas')
def tablas():
    inspector = inspect(obtener_engine())
    presentes = set(inspector.get_table_names(schema='public'))
    return {'tablas': [
        {'nombre': t, 'registros': cantidad(obtener_engine(), t) if t in presentes else 0,
         'existe': t in presentes, 'columnas': [c['name'] for c in inspector.get_columns(t, schema='public')] if t in presentes else []}
        for t in ORDEN
    ]}


@router.get('/exportar/{nombre}')
def exportar_csv(nombre: str):
    tabla_valida(nombre)
    eng = obtener_engine()
    if nombre not in inspect(eng).get_table_names(schema='public'):
        raise HTTPException(404, 'La tabla no existe.')
    buffer = io.StringIO(newline='')
    with eng.connect() as conn:
        result = conn.execute(text(f'SELECT * FROM public."{nombre}"'))
        writer = csv.writer(buffer)
        writer.writerow(result.keys())
        max_rows = 100000
        for index, row in enumerate(result):
            if index >= max_rows:
                raise HTTPException(413, 'Supera 100,000 registros. Usa pg_dump para grandes volúmenes.')
            writer.writerow(list(row))
    data = buffer.getvalue().encode('utf-8-sig')
    return StreamingResponse(iter([data]), media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename="concesionaria_{nombre}.csv"'})


@router.post('/importar/{nombre}')
async def importar_csv(nombre: str, archivo: UploadFile = File(...)):
    tabla_valida(nombre)
    if not archivo.filename or not archivo.filename.lower().endswith('.csv'):
        raise HTTPException(422, 'Selecciona un archivo CSV.')
    # Limitación antes de parsear o insertar.
    max_bytes = 5 * 1024 * 1024
    data = await archivo.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(413, 'Archivo mayor de 5 MB.')
    try:
        texto_csv = data.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(texto_csv, newline=''))
        cabecera = reader.fieldnames
        if not cabecera or len(cabecera) != len(set(cabecera)):
            raise ValueError('Falta cabecera CSV o contiene columnas duplicadas.')
        eng = obtener_engine()
        columnas_db = inspect(eng).get_columns(nombre, schema='public')
        disponibles = {col['name'] for col in columnas_db}
        if not set(cabecera).issubset(disponibles):
            raise ValueError('Columnas desconocidas: ' + ', '.join(sorted(set(cabecera) - disponibles)))
        filas = []
        for row in reader:
            if None in row:
                raise ValueError('Fila CSV con más campos que columnas.')
            filas.append({k: (None if v == '' else v) for k, v in row.items()})
            if len(filas) > 10000:
                raise ValueError('Máximo 10,000 filas por importación.')
        if not filas:
            raise ValueError('El archivo no tiene registros.')
    except (UnicodeDecodeError, csv.Error, ValueError) as e:
        raise HTTPException(422, str(e)) from e

    # Se mantiene como una transacción: errores PK/FK/CHECK revierten el lote entero.
    # PostgreSQL permite OVERRIDING SYSTEM VALUE en las tablas con columnas IDENTITY.
    identity = {col['name'] for col in columnas_db if col.get('identity')}
    especifica_id = bool(identity & set(cabecera))
    cols = ', '.join(f'"{c}"' for c in cabecera)
    vals = ', '.join(f':v{i}' for i in range(len(cabecera)))
    overriding = ' OVERRIDING SYSTEM VALUE' if especifica_id else ''
    sentencia = text(f'INSERT INTO public."{nombre}" ({cols}){overriding} VALUES ({vals})')
    parametros = [{f'v{i}': fila[c] for i, c in enumerate(cabecera)} for fila in filas]
    try:
        with eng.begin() as conn:
            conn.execute(sentencia, parametros)
            # Si se importan IDs explícitos, avanza la secuencia para INSERT siguientes.
            for col in identity & set(cabecera):
                seq = conn.execute(text('SELECT pg_get_serial_sequence(:tbl,:col)'),
                                   {'tbl': f'public.{nombre}', 'col': col}).scalar()
                if seq:
                    conn.execute(text('SELECT setval(CAST(:seq AS regclass), GREATEST(COALESCE((SELECT MAX("' + col + '") FROM public."' + nombre + '"), 1), 1), (SELECT COUNT(*)>0 FROM public."' + nombre + '"))'), {'seq': seq})
    except SQLAlchemyError as e:
        raise HTTPException(409, f'Importación cancelada y revertida por PostgreSQL ({type(e).__name__}). Revisa duplicados y restricciones.') from e
    return {'mensaje': 'CSV importado correctamente.', 'tabla': nombre, 'registros_importados': len(filas)}


def motor_mysql():
    url = os.getenv('MYSQL_URL', '')
    if not url:
        raise HTTPException(409, 'Falta MYSQL_URL en backend/.env.')
    if not url.startswith('mysql+pymysql://'):
        raise HTTPException(422, 'MYSQL_URL debe comenzar con mysql+pymysql://')
    return create_engine(url, pool_pre_ping=True, connect_args={'connect_timeout': 10})


@router.get('/migracion/estado')
def estado_migracion():
    engine = obtener_engine()
    origen = {'base': obtener_base_seleccionada()}
    pg_tables = set(inspect(engine).get_table_names(schema='public'))
    origen['tablas'] = {t: cantidad(engine, t) if t in pg_tables else None for t in ORDEN}
    respuesta = {'origen': origen, 'mysql_configurado': bool(os.getenv('MYSQL_URL'))}
    if os.getenv('MYSQL_URL'):
        destino = motor_mysql()
        try:
            with destino.connect() as conn:
                base_mysql = conn.execute(text('SELECT DATABASE()')).scalar()
                version = conn.execute(text('SELECT VERSION()')).scalar()
            existentes = inspect(destino).get_table_names()
            respuesta['destino'] = {'base': base_mysql, 'version': version, 'tablas_existentes': existentes,
                                    'tablas': {t: cantidad_mysql(destino, t) for t in ORDEN if t in existentes}}
        except SQLAlchemyError as e:
            raise HTTPException(503, f'No se pudo conectar con MySQL: {type(e).__name__}. Revisa MYSQL_URL y el servicio.') from e
        finally:
            destino.dispose()
    return respuesta


def cantidad_mysql(engine, t):
    with engine.connect() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM `{t}`')).scalar_one()


class Confirmacion(BaseModel):
    confirmacion: str


@router.post('/migracion/ejecutar')
def migrar(datos: Confirmacion):
    if datos.confirmacion != 'MIGRAR_CONCESIONARIA':
        raise HTTPException(422, 'Escribe MIGRAR_CONCESIONARIA para ejecutar.')
    verificar_tablas()
    origen = obtener_engine()
    destino = motor_mysql()
    creadas = []
    try:
        if inspect(destino).get_table_names():
            raise HTTPException(409, 'La base MySQL de destino debe estar completamente vacía. Crea una nueva base para la práctica.')
        with destino.connect() as c:
            ver = c.execute(text('SELECT VERSION()')).scalar()
            if 'mariadb' in ver.lower():
                raise HTTPException(422, 'La migración requiere MySQL 8, no MariaDB.')
            match = re.match(r'(\d+)\.(\d+)\.(\d+)', ver)
            if not match or tuple(map(int, match.groups())) < (8, 0, 16):
                raise HTTPException(422, 'Se requiere MySQL 8.0.16 o superior.')
        ddl = (Path(__file__).resolve().parents[1] / 'sql' / 'mysql_concesionaria.sql').read_text(encoding='utf-8')
        # SQL del proyecto: no contiene valores con punto y coma dentro de cadenas.
        with destino.begin() as conn:
            for sentencia in [x.strip() for x in ddl.split(';') if x.strip()]:
                conn.exec_driver_sql(sentencia)
                # Guardamos nombres creados para limpieza si la copia falla.
                match = re.match(r'CREATE TABLE\s+(\w+)', sentencia, re.IGNORECASE)
                if match:
                    creadas.append(match.group(1))
        totales = {}
        with origen.connect() as pg, destino.begin() as mysql:
            metadata = MetaData()
            for nombre in ORDEN:
                tabla_mysql = Table(nombre, metadata, autoload_with=destino)
                fuente = pg.execute(text(f'SELECT * FROM public."{nombre}"'))
                keys = list(fuente.keys())
                cuenta = 0
                while True:
                    lote = fuente.fetchmany(500)
                    if not lote:
                        break
                    mysql.execute(tabla_mysql.insert(), [dict(zip(keys, registro)) for registro in lote])
                    cuenta += len(lote)
                totales[nombre] = cuenta
        validados = {nombre: cantidad_mysql(destino, nombre) for nombre in ORDEN}
        if any(totales[t] != validados[t] for t in ORDEN):
            raise HTTPException(500, 'Error de validación: el número de registros migrados no coincide.')
        return {'mensaje': 'Migración PostgreSQL a MySQL terminada.', 'registros_por_tabla': validados,
                'total_registros': sum(validados.values())}
    except HTTPException:
        raise
    except (SQLAlchemyError, ValueError, OSError) as e:
        # No revela URLs o contraseñas en trazas SQL.
        raise HTTPException(409, f'No se pudo completar la migración ({type(e).__name__}). Destino puede haber quedado parcialmente creado; usa una base MySQL nueva para reintentar.') from e
    finally:
        destino.dispose()
