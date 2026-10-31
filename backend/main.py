"""API educativa de AutoGest Unidad 5. No implementa autenticación comercial."""
import logging
import os
import time
from datetime import date, datetime, time as dt_time
from decimal import Decimal
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.catalog import EXERCISES, list_catalog
from app.database import connect_checked
from app.objects import demo_trigger, trigger_source
from app.setup import is_ready, prepare

load_dotenv(Path(__file__).resolve().parent / '.env')
logger = logging.getLogger('autogest.unidad5')
app = FastAPI(title='AutoGest | Laboratorio Unidad 5', version='1.0.0',
    description='65 ejercicios predefinidos de PostgreSQL; base experimental aislada y datos ficticios.')
origins = [s.strip() for s in os.getenv('FRONTEND_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173').split(',') if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins,
    allow_methods=['GET','POST'],allow_headers=['Content-Type'])

class RunBody(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)

def normalize(value):
    if isinstance(value, Decimal): return float(value)
    if isinstance(value, (date, datetime, dt_time)): return value.isoformat()
    return value

def checked_params(exercise, raw):
    allowed = {p['name'] for p in exercise.params}
    if set(raw) - allowed:
        raise HTTPException(422, 'Hay parámetros que no pertenecen a este ejercicio.')
    values={}
    for param in exercise.params:
        name=param['name']
        value=raw.get(name,param['default'])
        try:
            if param['kind']=='int':
                if isinstance(value,bool): raise ValueError()
                value=int(value)
                if not -10000000 <= value <= 10000000: raise ValueError()
            elif param['kind']=='float':
                if isinstance(value,bool): raise ValueError()
                value=float(value)
                if not -10000000 <= value <= 10000000: raise ValueError()
            elif param['kind']=='date':
                value=date.fromisoformat(str(value)).isoformat()
            else:
                value=str(value)
                if len(value)>80: raise ValueError()
        except (ValueError,TypeError,OverflowError):
            raise HTTPException(422,f'Parámetro incorrecto: {name}') from None
        values[name]=value
    return values

@app.get('/')
def root():
    return {'app':'AutoGest','unidad':5,'ejercicios':len(EXERCISES)}

@app.get('/api/catalogo')
def catalog():
    data=list_catalog()
    for exercise in data['exercises']:
        if exercise['group']=='triggers':
            exercise['sql']=trigger_source(exercise['code'])
    return data

@app.get('/api/estado')
def state():
    try:
        conn=connect_checked()
        try:
            ready=is_ready(conn)
            db=conn.execute(text('SELECT current_database()')).scalar_one()
            return {'connected':True,'ready':ready,'database':db,
                'message':'Preparada' if ready else 'Conectada; requiere preparar la base'}
        finally:
            conn.close()
    except HTTPException as exc:
        return {'connected':False,'ready':False,'message':exc.detail}
    except SQLAlchemyError:
        logger.exception('Error de conexión consultando el estado')
        return {'connected':False,'ready':False,
                'message':'No se pudo conectar con PostgreSQL; comprueba .env, SSL y red.'}

@app.post('/api/preparar')
def setup():
    try:
        return prepare()
    except HTTPException:
        raise
    except (SQLAlchemyError, OSError) as exc:
        logger.exception('No fue posible preparar AutoGest Unidad 5: %s', type(exc).__name__)
        raise HTTPException(503,
            'No fue posible preparar la base. El detalle está en la terminal de FastAPI.') from exc

@app.post('/api/ejecutar/{code}')
def run(code: str, body: RunBody):
    code=code.upper()
    exercise=EXERCISES.get(code)
    if exercise is None: raise HTTPException(404,'El ejercicio no existe.')
    params=checked_params(exercise,body.params)
    start=time.perf_counter()
    try:
        conn=connect_checked()
        try:
            if not is_ready(conn):
                raise HTTPException(409,'Primero prepara la base de datos experimental.')
            if exercise.group=='triggers':
                conn.rollback()
                with conn.begin() as transaction:
                    result=demo_trigger(conn,code)
                    transaction.rollback()
                return {'code':code,'title':exercise.title,'columns':list(result),
                    'rows':[{key:normalize(value) for key,value in result.items()}],
                    'duration_ms':round((time.perf_counter()-start)*1000,2),
                    'message':'Prueba realizada dentro de una transacción revertida.'}
            query_result=conn.execute(text(exercise.sql),params)
            columns=list(query_result.keys())
            rows=[{k:normalize(v) for k,v in dict(row).items()}
                for row in query_result.mappings().fetchmany(101)]
            truncated=len(rows)>100
            return {'code':code,'title':exercise.title,'columns':columns,
                'rows':rows[:100], 'truncated':truncated,
                'duration_ms':round((time.perf_counter()-start)*1000,2),
                'message':'Consulta ejecutada correctamente.'}
        finally:
            conn.close()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception('Error SQL ejecutando ejercicio %s',code)
        raise HTTPException(422,
            'La consulta no pudo ejecutarse. Revisa el detalle en la terminal del backend.') from exc
