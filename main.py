from fastapi import FastAPI

from sqlmodel import create_engine

from sqlalchemy import text

from dotenv import load_dotenv

from consultas import consultas_31, consultas_32

import os


load_dotenv()

db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url, echo=True)

app = FastAPI(title="Concesionaria API")


@app.get("/")
def inicio():

    return {"mensaje": "API de la concesionaria funcionando"}


@app.get("/db-test")
def probar_conexion():

    with engine.connect() as conexion:

        resultado = conexion.execute(text("SELECT 1"))

        return {
            "database": "conectada",
            "resultado": resultado.scalar()
        }


def ejecutar_sql():

    with open("concesionaria.sql", "r", encoding="utf-8") as archivo:

        sql = archivo.read()

    sentencias = [
        sentencia.strip()
        for sentencia in sql.split(";")
        if sentencia.strip()
    ]

    with engine.begin() as conexion:

        for sentencia in sentencias:

            conexion.execute(text(sentencia))


def ejecutar_consulta(consulta):

    try:

        with engine.begin() as conexion:

            conexion.execute(text(consulta))

    except Exception as error:

        print("ERROR SQL:", error)

        raise


@app.post("/crear-tablas")
def crear_tablas():

    ejecutar_sql()

    return {
        "mensaje": "Tablas creadas correctamente"
    }


@app.post("/insertar-cliente")
def insertar_cliente():

    ejecutar_consulta(consultas_32["insert_cliente_1"])

    return {
        "mensaje": "Cliente insertado correctamente"
    }


def ejecutar_consultas(consultas):

    with engine.begin() as conexion:

        for nombre, consulta in consultas.items():

            print(f"Ejecutando: {nombre}")

            conexion.execute(text(consulta))


def hay_datos_cargados():

    with engine.connect() as conexion:

        resultado = conexion.execute(text("SELECT COUNT(*) FROM cliente"))

        total = resultado.scalar()

    return total > 0


@app.post("/cargar-datos")
def cargar_datos():

    if hay_datos_cargados():

        return {
            "mensaje": "Los datos ya fueron cargados anteriormente. No se insertó nada para evitar duplicados."
        }

    ejecutar_consultas(consultas_32)

    return {
        "mensaje": "Todos los datos fueron insertados correctamente"
    }


def ejecutar_consulta_seleccion(consulta):

    with engine.connect() as conexion:

        resultado = conexion.execute(text(consulta))

        filas = [dict(fila._mapping) for fila in resultado]

    return filas


@app.get("/consultas")
def listar_consultas():

    return {
        "disponibles": list(consultas_31.keys())
    }


@app.get("/consulta/{nombre}")
def ejecutar_consulta_individual(nombre: str):

    if nombre not in consultas_31:

        return {
            "error": f"Consulta '{nombre}' no encontrada"
        }

    resultado = ejecutar_consulta_seleccion(consultas_31[nombre])

    return {
        "consulta": nombre,
        "resultado": resultado
    }
