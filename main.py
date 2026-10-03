from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from sqlmodel import create_engine

from sqlalchemy import text

from dotenv import load_dotenv

from ddl import ddl_create, ddl_alter, ddl_drop

from dcl import dcl_usuarios, dcl_grant, dcl_revoke, dcl_drop_user

import os


load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("No se encontró la URL en el archivo .env")

engine = create_engine(db_url, echo=True)

app = FastAPI(title="Concesionaria API")

class DatosUsuario(BaseModel):
    usuario: str
    password: str


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {"mensaje": "Conexión a la base de datos exitosa"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def ejecutar_sql(sql):
    with engine.begin() as conexion:
        conexion.execute(text(sql))


# Endpoint para los CREATE

@app.post("/ddl/create/{tabla}")
def crear_tabla(tabla: str):
    if tabla not in ddl_create:
        raise HTTPException(
            status_code=404, detail="La tabla no tiene una consulta CREATE definida")

    try:
        ejecutar_sql(ddl_create[tabla])

        return {"Operación:": "CREATE",
                "Tabla:": tabla,
                "Mensaje:": "Tabla creada correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint para los ALTER


@app.put("/ddl/alter/{tabla}")
def alterar_tabla(tabla: str):
    if tabla not in ddl_alter:
        raise HTTPException(
            status_code=404, detail="La tabla no tiene una consulta ALTER definida")

    try:
        ejecutar_sql(ddl_alter[tabla])
        return {"Operación:": "ALTER",
                "Tabla:": tabla,
                "Mensaje:": "Tabla modificada correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint para los DROP


@app.delete("/ddl/drop/{tabla}")
def eliminar_tabla(tabla: str):
    if tabla not in ddl_drop:
        raise HTTPException(
            status_code=404, detail="La tabla no tiene una consulta DROP definida")

    try:
        ejecutar_sql(ddl_drop[tabla])
        return {"Operación:": "DROP",
                "Tabla:": tabla,
                "Mensaje:": "Tabla eliminada correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# 3.4 Endpoint para crear roles/usuarios

@app.post("/dcl/crear_usuario")
def crear_usuario(datos: DatosUsuario):

    if datos.usuario not in dcl_usuarios:
        raise HTTPException(
            status_code=404,
            detail="El usuario no está definido en la actividad"
        )

    password_user = datos.password.replace("'", "''")

    sql = f"CREATE ROLE {datos.usuario} LOGIN PASSWORD '{password_user}';"

    try:
        ejecutar_sql(sql)

        return {
            "Operacion": "CREATE ROLE",
            "Usuario": datos.usuario,
            "Mensaje": "Usuario creado correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint extra a la actividad para eliminar roles/usuarios


@app.delete("/dcl/borrar_usuario/{usuario}")
def eliminar_usuario(usuario: str):
    if usuario not in dcl_drop_user:
        raise HTTPException(
            status_code=404,
            detail="El usuario no tiene una consulta DROP ROLE definida"
        )

    try:
        ejecutar_sql(dcl_drop_user[usuario])

        return {
            "Operacion": "DROP ROLE",
            "Usuario": usuario,
            "Mensaje": "Usuario eliminado correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint de GRANT


@app.post("/dcl/grant/{consulta}")
def conceder_privilegio(consulta: str):
    if consulta not in dcl_grant:
        raise HTTPException(
            status_code=404,
            detail="La consulta GRANT no está definida"
        )

    try:
        ejecutar_sql(dcl_grant[consulta])

        return {
            "Operacion": "GRANT",
            "Consulta": consulta,
            "Mensaje": "Privilegio concedido correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint para revoke


@app.post("/dcl/revoke/{consulta}")
def revocar_privilegio(consulta: str):
    if consulta not in dcl_revoke:
        raise HTTPException(
            status_code=404,
            detail="La consulta REVOKE no está definida"
        )

    try:
        ejecutar_sql(dcl_revoke[consulta])

        return {
            "Operacion": "REVOKE",
            "Consulta": consulta,
            "Mensaje": "Privilegio revocado correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# Endpoint para mostrar consultas DCL

@app.post("/dcl/sql/{operacion}")
def obtener_sql_dcl(operacion: str, datos: DatosUsuario):

    usuario = datos.usuario

    if usuario not in dcl_usuarios:
        raise HTTPException(
            status_code=404,
            detail="El usuario no está definido en la actividad"
        )

    if operacion == "crear_usuario":

        password_user = datos.password.replace("'", "''")

        sql = f"CREATE ROLE {usuario} LOGIN PASSWORD '{password_user}';"

    elif operacion == "eliminar_usuario":

        sql = dcl_drop_user[usuario]

    elif operacion == "otorgar_permiso":

        sql = dcl_grant[usuario]

    elif operacion == "quitar_permiso":

        sql = dcl_revoke[usuario]

    else:

        raise HTTPException(
            status_code=404,
            detail="Operación DCL no válida"
        )

    return {
        "Operacion": operacion.upper(),
        "Usuario": usuario,
        "SQL": sql
    }

# Endpoint para devolver datos JSON a Tkinter

@app.get("/dcl/ddl/sql/{operacion}/{consulta}")
def obtener_sql(operacion: str, consulta: str):

    operaciones = {
        "create": ddl_create,
        "alter": ddl_alter,
        "drop": ddl_drop,
        "usuario": dcl_usuarios,
        "grant": dcl_grant,
        "revoke": dcl_revoke,
        "drop_user": dcl_drop_user
    }

    if operacion not in operaciones:
        raise HTTPException(
            status_code=404,
            detail="Operación DCL no válida"
        )

    diccionario = operaciones[operacion]

    if consulta not in diccionario:
        raise HTTPException(
            status_code=404,
            detail="La consulta no está definida"
        )

    return {
        "Operacion": operacion.upper(),
        "Consulta": consulta,
        "SQL": diccionario[consulta]
    }

#Endpoint para ver la lista de usuarios

@app.get("/dcl/usuarios")
def consultar_usuarios():

    sql = """
    SELECT rolname
    FROM pg_roles
    WHERE rolcanlogin = true
    ORDER BY rolname;
    """

    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text(sql))

            usuarios = [
                fila[0]
                for fila in resultado
            ]

        return {
            "usuarios": usuarios
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


#Endpoint para ver los permisos de los usuarios

@app.get("/dcl/permisos/{usuario}")
def consultar_permisos(usuario: str):

    sql = """
    SELECT
        table_schema,
        table_name,
        privilege_type
    FROM information_schema.role_table_grants
    WHERE grantee = :usuario
    ORDER BY table_name, privilege_type;
    """

    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(
                text(sql),
                {"usuario": usuario}
            )

            permisos = [
                {
                    "esquema": fila[0],
                    "tabla": fila[1],
                    "privilegio": fila[2]
                }
                for fila in resultado
            ]

        return {
            "usuario": usuario,
            "permisos": permisos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e