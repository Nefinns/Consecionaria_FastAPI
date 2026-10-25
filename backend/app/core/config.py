import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError


BACKEND_DIR = Path(__file__).resolve().parents[2]


@lru_cache
def obtener_database_url() -> URL:
    valores = {
        **dotenv_values(BACKEND_DIR / ".env"),
        **os.environ,
    }

    valor = (valores.get("DATABASE_URL") or "").strip()

    if not valor:
        raise ValueError(
            "Falta DATABASE_URL en backend/.env o en el entorno."
        )

    try:
        url = make_url(valor)
        _ = url.port
    except (ArgumentError, ValueError):
        raise ValueError(
            "DATABASE_URL no tiene un formato válido."
        ) from None

    if url.drivername not in {
        "postgres",
        "postgresql",
        "postgresql+psycopg2",
    }:
        raise ValueError(
            "DATABASE_URL debe usar PostgreSQL con psycopg2."
        )

    if not url.host or not url.database or not url.username:
        raise ValueError(
            "DATABASE_URL requiere servidor, base de datos y usuario."
        )

    sslmode = url.query.get("sslmode", "require")

    if sslmode not in {"require", "verify-ca", "verify-full"}:
        raise ValueError(
            "La conexión remota requiere un sslmode cifrado."
        )

    return (
        url.set(drivername="postgresql+psycopg2")
        .update_query_dict({"sslmode": sslmode})
    )