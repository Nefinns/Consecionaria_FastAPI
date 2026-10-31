"""Instalación transaccional del esquema canónico y objetos académicos.

IMPORTANTE: el esquema entregado contiene un punto y coma en un literal SQL.
Por eso NO se divide por ';'. psycopg2 permite ejecutar el bloque DDL completo.
"""
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import text

from .database import connect_checked
from .objects import install_objects
from .seed import seed_demo

TABLES = {'cliente', 'proveedor', 'usuario_interno', 'coche', 'venta', 'revision'}
SCRIPT = Path(__file__).resolve().parents[1] / 'sql' / 'esquema_canonico.sql'
CONTROL = 'u5_autogest_control'

def current_tables(conn):
    return set(conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = current_schema()')).scalars())

def is_ready(conn):
    tables = current_tables(conn)
    if not TABLES.issubset(tables) or CONTROL not in tables:
        return False
    return bool(conn.execute(text("SELECT EXISTS (SELECT 1 FROM u5_autogest_control WHERE clave='datos_demo_v1')")).scalar())

def schema_sql():
    """Quita únicamente BEGIN/COMMIT independientes; conserva literalmente el DDL."""
    raw = SCRIPT.read_text(encoding='utf-8-sig')
    lines = [line for line in raw.splitlines() if line.strip().upper() not in ('BEGIN;', 'COMMIT;')]
    return '\n'.join(lines)

def prepare():
    conn = connect_checked()
    try:
        with conn.begin():
            existing = current_tables(conn)
            domain_present = existing & TABLES
            if domain_present and domain_present != TABLES:
                raise HTTPException(409, 'Esquema incompleto. Crea otra BD experimental vacía.')
            created_now = not bool(domain_present)
            if created_now:
                if existing:
                    raise HTTPException(409, 'La base contiene tablas ajenas. Utiliza una base vacía.')
                conn.exec_driver_sql(schema_sql())
            conn.exec_driver_sql('''CREATE TABLE IF NOT EXISTS u5_autogest_control (
                clave TEXT PRIMARY KEY, valor TEXT NOT NULL)''')
            previously_seeded = conn.execute(text("SELECT valor FROM u5_autogest_control WHERE clave='datos_demo_v1'")).scalar_one_or_none()
            if not previously_seeded:
                for table in TABLES:
                    if conn.execute(text(f'SELECT EXISTS (SELECT 1 FROM {table})')).scalar():
                        raise HTTPException(409, 'Existen registros previos; no se mezclarán con la demostración.')
                counters = seed_demo(conn)
                conn.execute(text("INSERT INTO u5_autogest_control (clave,valor) VALUES ('datos_demo_v1','instalado')"))
            else:
                counters = {'mensaje': 'Los registros de demostración ya existían; no se duplicaron.'}
            install_objects(conn)
        return {'ok': True, 'message': 'AutoGest Unidad 5 preparado correctamente.',
                'created_now': created_now, 'seed': counters, 'views': 5,
                'functions': 5, 'triggers': 5}
    finally:
        conn.close()
