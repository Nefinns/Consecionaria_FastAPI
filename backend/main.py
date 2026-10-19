from contextlib import asynccontextmanager
from ipaddress import ip_address

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core.connections import cerrar_conexiones, seleccionar_base, url_admin
from routers.database import router as database_router
from routers.schema import router as schema_router
from routers.dcl import router as dcl_router
from routers.backup import router as backup_router
from routers.transfer import router as transfer_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not url_admin.database:
        raise RuntimeError('DATABASE_URL debe incluir nombre de base.')
    seleccionar_base(url_admin.database)
    yield
    cerrar_conexiones()


app = FastAPI(title='Concesionaria · Administración de Bases de Datos',
              description='Unidad 4: PostgreSQL/Neon, roles, respaldo y migración a MySQL.',
              version='2.0.0', lifespan=lifespan)

# PANEL SOLO LOCAL: las rutas permiten crear usuarios, importar datos y restaurar bases.
# Nunca publicar con --host 0.0.0.0 ni exponer mediante túneles públicos.
ALLOWED_ORIGINS = {'http://localhost:5173', 'http://127.0.0.1:5173'}
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', 'testserver'])
app.add_middleware(CORSMiddleware, allow_origins=sorted(ALLOWED_ORIGINS),
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['*'])


@app.middleware('http')
async def solo_local(request: Request, call_next):
    host = request.client.host if request.client else ''
    try:
        local = ip_address(host).is_loopback
    except ValueError:
        local = host == 'testclient'
    if not local:
        return JSONResponse(status_code=403, content={'detail': 'Panel administrativo exclusivo para localhost.'})
    origin = request.headers.get('origin')
    if origin and origin not in ALLOWED_ORIGINS:
        return JSONResponse(status_code=403, content={'detail': 'Origen web no autorizado.'})
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and origin and not origin.startswith('http://localhost:5173') and origin != 'http://127.0.0.1:5173':
        return JSONResponse(status_code=403, content={'detail': 'Solicitud rechazada.'})
    return await call_next(request)


for router in [database_router, schema_router, dcl_router, backup_router, transfer_router]:
    app.include_router(router)


@app.get('/', tags=['General'])
def inicio():
    return {'aplicacion': 'Concesionaria', 'version': '2.0.0', 'documentacion': '/docs'}


@app.get('/db-test', tags=['General'])
def test_alias():
    from routers.database import probar_conexion
    return probar_conexion()
