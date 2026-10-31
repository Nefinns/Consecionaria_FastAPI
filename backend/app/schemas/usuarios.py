"""Datos de entrada/salida. Los roles nunca son elegidos por el usuario final."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Rol = Literal["administrador", "gerente", "mecanico"]
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Identidad = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class UsuarioPerfil(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_usuario: int
    nombre: str
    rol: Rol
    activo: bool


class UsuarioDetalle(UsuarioPerfil):
    identidad_externa: str


class UsuarioCrear(BaseModel):
    identidad_externa: Identidad
    nombre: Nombre
    rol: Rol


class UsuarioModificar(BaseModel):
    nombre: Nombre | None = None
    rol: Rol | None = None
    activo: bool | None = None


class ListaUsuarios(BaseModel):
    usuarios: list[UsuarioDetalle]
    total: int = Field(ge=0)
