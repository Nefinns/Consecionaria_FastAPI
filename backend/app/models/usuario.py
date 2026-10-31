"""Reflejo ORM de la tabla canónica usuario_interno ya creada en Neon.

SQLModel.metadata.create_all() NO se utiliza durante el arranque.
"""
from sqlmodel import Field, SQLModel


class UsuarioInterno(SQLModel, table=True):
    __tablename__ = "usuario_interno"

    id_usuario: int | None = Field(default=None, primary_key=True)
    identidad_externa: str = Field(max_length=255, unique=True, nullable=False)
    nombre: str = Field(max_length=120, nullable=False)
    rol: str = Field(max_length=20, nullable=False)
    activo: bool = Field(default=True, nullable=False)
