from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from app.catalog import EXERCISES, GROUPS
from app.objects import FUNCTIONS, TRIGGERS, VIEWS, demo_trigger, trigger_source
from app.setup import TABLES, schema_sql


def test_65_exercises():
    assert len(EXERCISES)==65
    assert Counter(ex.group for ex in EXERCISES.values()) == {
        'simples':25,'joins':15,'agregadas':15,'vistas':5,'triggers':5}
    assert sum(g['target'] for g in GROUPS)==65

def test_canonical_six_tables():
    assert TABLES=={'cliente','proveedor','usuario_interno','coche','venta','revision'}
    script=schema_sql()
    for table in TABLES:
        assert f'CREATE TABLE {table} (' in script
    assert 'BEGIN;' not in script.splitlines()
    assert "'Registro administrativo; no procesa" in script

def test_five_views_and_function_trigger_pairs():
    assert len(VIEWS)==len(FUNCTIONS)==len(TRIGGERS)==5
    assert set(FUNCTIONS)==set(TRIGGERS)=={f'T{i:02d}' for i in range(1,6)}
    assert all('CREATE OR REPLACE FUNCTION' in trigger_source(code) for code in FUNCTIONS)

def test_all_read_exercises_use_queries():
    for item in EXERCISES.values():
        if item.group!='triggers':
            assert item.sql.lstrip().upper().startswith('SELECT')
        assert item.code[0] in 'SJAVT'

def test_no_raw_client_sql():
    assert all('DROP TABLE' not in item.sql.upper() for item in EXERCISES.values())
