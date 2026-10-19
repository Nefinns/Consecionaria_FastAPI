
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.connections import cerrar_conexiones, seleccionar_base, url_admin
from routers.database import router as database_router
from routers.schema import router as schema_router
from routers.dcl import router as dcl_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Selecciona la base configurada en el .env al iniciar.
    if not url_admin.database:
        raise RuntimeError("La URL de PostgreSQL no incluye el nombre de la base.")
    seleccionar_base(url_admin.database)
    yield
    cerrar_conexiones()


app = FastAPI(
    title="Concesionaria - Administración de Bases de Datos",
    description=(
        "API para creación de bases de datos, administración del esquema "
        "y gestión de usuarios y permisos PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Permite el desarrollo local del minifront.
# En producción, limita los orígenes a los dominios autorizados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(database_router)
app.include_router(schema_router)
app.include_router(dcl_router)


@app.get("/", tags=["General"])
def inicio():
    return {
        "aplicacion": "Concesionaria - Administración de BD",
        "estado": "activa",
        "documentacion": "/docs",
    }


@app.get("/db-test", tags=["Bases de datos"])
def db_test_alias():
    # Conserva la ruta anterior para las pruebas existentes.
    from routers.database import probar_conexion
    return probar_conexion()
