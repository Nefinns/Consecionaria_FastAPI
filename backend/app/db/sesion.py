from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.core.config import obtener_database_url


@lru_cache
def obtener_motor() -> Engine:
    return create_engine(
        obtener_database_url(),
        pool_pre_ping=True,
        pool_timeout=10,
        connect_args={"connect_timeout": 10},
        echo=False,
        hide_parameters=True,
    )


def obtener_sesion() -> Iterator[Session]:
    with Session(obtener_motor()) as sesion:
        yield sesion


def cerrar_motor() -> None:
    if obtener_motor.cache_info().currsize:
        obtener_motor().dispose()
        obtener_motor.cache_clear()