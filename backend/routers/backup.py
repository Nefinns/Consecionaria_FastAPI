"""4.4 Respaldos .backup de PostgreSQL y restauración a servidor de prácticas.
Se ejecuta localmente; nunca se envían claves al navegador.
"""
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.engine import make_url

from core.connections import obtener_base_seleccionada, url_admin

router = APIRouter(prefix='/backup', tags=['4.4 Respaldos y restauración'])
ROOT = Path(__file__).resolve().parents[1]
CARPETA = ROOT / 'backups'
CARPETA.mkdir(parents=True, exist_ok=True)
PATRON = re.compile(r'^concesionaria_[0-9]{8}_[0-9]{6}(?:_[0-9]{1,4})?\.backup$')


def ubicacion(nombre_env: str, fallback: str) -> str:
    value = os.getenv(nombre_env) or shutil.which(fallback)
    if not value or not Path(value).is_file():
        raise HTTPException(503, f'No se encontró {fallback}. Configura {nombre_env} con la ruta completa al ejecutable.')
    return value


def parametros_pg(url):
    if not url.drivername.startswith('postgresql'):
        raise HTTPException(422, 'Las operaciones 4.4 solo admiten servidores PostgreSQL.')
    usuario = url.username
    if not usuario or not url.host or not url.database:
        raise HTTPException(422, 'La URL PostgreSQL debe especificar servidor, base de datos y usuario.')
    env = os.environ.copy()
    env['PGPASSWORD'] = url.password or ''
    env['PGCLIENTENCODING'] = 'UTF8'
    # Neon requiere TLS. Preferimos sslmode de la URL cuando exista.
    query = dict(url.query)
    env['PGSSLMODE'] = query.get('sslmode', os.getenv('PG_SSLMODE', 'require'))
    args = ['--host', url.host, '--port', str(url.port or 5432), '--username', usuario,
            '--dbname', url.database, '--no-password']
    return args, env


def correr(comando, env):
    try:
        result = subprocess.run(comando, env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=600, check=False)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, 'La operación excedió 10 minutos.')
    except OSError:
        raise HTTPException(503, 'No fue posible iniciar la herramienta PostgreSQL.')
    if result.returncode:
        # No exponemos el comando ni la URL, que podrían contener credenciales.
        detalle = result.stderr[-1500:].strip()
        detalle = re.sub(r'(?i)(password\s*[=:]\s*)[^\s]+', r'\1***', detalle)
        raise HTTPException(400, f'La herramienta PostgreSQL terminó con error: {detalle}')
    return result


def archivos():
    return sorted([p for p in CARPETA.glob('*.backup') if p.is_file() and PATRON.fullmatch(p.name)],
                  key=lambda p: p.stat().st_mtime, reverse=True)


@router.get('/configuracion')
def configuracion():
    destino = os.getenv('RESTORE_DATABASE_URL')
    return {
        'base_origen': obtener_base_seleccionada(),
        'servidor_origen': url_admin.host,
        'restauracion_configurada': bool(destino),
        'servidor_destino': make_url(destino).host if destino else None,
        'base_destino': make_url(destino).database if destino else None,
        'pg_dump_disponible': bool(os.getenv('PG_DUMP_PATH') or shutil.which('pg_dump')),
        'pg_restore_disponible': bool(os.getenv('PG_RESTORE_PATH') or shutil.which('pg_restore')),
    }


@router.get('/listar')
def listar():
    return {'archivos': [
        {'nombre': p.name, 'bytes': p.stat().st_size,
         'fecha': datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()}
        for p in archivos()
    ]}


@router.post('/crear')
def crear():
    base = obtener_base_seleccionada()
    if not base:
        raise HTTPException(409, 'Selecciona primero la base de Concesionaria.')
    url = url_admin.set(database=base)
    herramienta = ubicacion('PG_DUMP_PATH', 'pg_dump')
    args, env = parametros_pg(url)
    marca = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre = f'concesionaria_{marca}.backup'
    n = 1
    while (CARPETA / nombre).exists():
        nombre = f'concesionaria_{marca}_{n}.backup'
        n += 1
    final = CARPETA / nombre
    temporal = final.with_suffix('.tmp')
    try:
        correr([herramienta, *args, '--format=custom', '--no-owner', '--no-privileges',
                '--file', str(temporal)], env)
        if not temporal.exists() or temporal.stat().st_size == 0:
            raise HTTPException(500, 'pg_dump no produjo un respaldo válido.')
        temporal.replace(final)
        return {'mensaje': 'Respaldo creado correctamente.', 'nombre': nombre, 'bytes': final.stat().st_size}
    finally:
        temporal.unlink(missing_ok=True)


def obtener_archivo(nombre):
    if not PATRON.fullmatch(nombre):
        raise HTTPException(422, 'Nombre de respaldo no permitido.')
    path = CARPETA / nombre
    if not path.is_file():
        raise HTTPException(404, 'No se encontró el respaldo.')
    return path


@router.get('/descargar/{nombre}')
def descargar(nombre: str):
    return FileResponse(obtener_archivo(nombre), media_type='application/octet-stream', filename=nombre)


class DatosRestauracion(BaseModel):
    nombre: str
    confirmacion: str


@router.post('/restaurar')
def restaurar(datos: DatosRestauracion):
    if datos.confirmacion != 'RESTAURAR_DESTINO':
        raise HTTPException(422, 'Escribe RESTAURAR_DESTINO para confirmar.')
    destino = os.getenv('RESTORE_DATABASE_URL')
    if not destino:
        raise HTTPException(409, 'Configura RESTORE_DATABASE_URL para un PostgreSQL de prácticas.')
    origen = url_admin.set(database=obtener_base_seleccionada() or url_admin.database)
    url = make_url(destino)
    if (url.host, url.port or 5432, url.database) == (origen.host, origen.port or 5432, origen.database):
        raise HTTPException(409, 'No se permite restaurar sobre la base de origen.')
    herramienta = ubicacion('PG_RESTORE_PATH', 'pg_restore')
    ruta = obtener_archivo(datos.nombre)
    args, env = parametros_pg(url)
    correr([herramienta, *args, '--clean', '--if-exists', '--no-owner', '--no-privileges',
            '--exit-on-error', '--single-transaction', str(ruta)], env)
    return {'mensaje': 'Respaldo restaurado en la base PostgreSQL de destino.',
            'base_destino': url.database, 'servidor_destino': url.host}
