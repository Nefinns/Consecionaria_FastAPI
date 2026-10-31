"""CRUD restringido de autorización interna. No manipula contraseñas."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select
from supertokens_python.asyncio import get_user

from app.api.deps import SesionBD, exigir_roles, obtener_usuario_actual
from app.models.usuario import UsuarioInterno
from app.schemas.usuarios import (
    ListaUsuarios, UsuarioCrear, UsuarioDetalle, UsuarioModificar, UsuarioPerfil,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios y roles"])
Administrador = Annotated[UsuarioInterno, Depends(exigir_roles("administrador"))]
Autorizado = Annotated[UsuarioInterno, Depends(obtener_usuario_actual)]


@router.get("/me", response_model=UsuarioPerfil)
def mi_perfil(usuario: Autorizado):
    """Perfil de la identidad autenticada y autorizada en Neon."""
    return usuario


@router.get("", response_model=ListaUsuarios)
def listar_usuarios(
    bd: SesionBD,
    _administrador: Administrador,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Listado paginado: solo administradores."""
    total = bd.exec(select(func.count()).select_from(UsuarioInterno)).one()
    filas = bd.exec(select(UsuarioInterno).order_by(UsuarioInterno.id_usuario).offset(offset).limit(limit)).all()
    return ListaUsuarios(usuarios=[UsuarioDetalle.model_validate(f) for f in filas], total=total)


@router.get("/{id_usuario}", response_model=UsuarioDetalle)
def consultar_usuario(id_usuario: int, bd: SesionBD, _administrador: Administrador):
    usuario = bd.get(UsuarioInterno, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario interno inexistente.")
    return usuario


@router.post("", response_model=UsuarioDetalle, status_code=201)
async def agregar_usuario(datos: UsuarioCrear, bd: SesionBD, _administrador: Administrador):
    """Vincular una identidad YA registrada en SuperTokens; no genera claves."""
    try:
        existente_en_core = await get_user(datos.identidad_externa)
    except Exception:
        raise HTTPException(status_code=503, detail="No se pudo verificar la identidad externa.") from None
    if existente_en_core is None:
        raise HTTPException(status_code=422, detail="La identidad no existe en SuperTokens.")

    nuevo = UsuarioInterno(
        identidad_externa=datos.identidad_externa,
        nombre=datos.nombre,
        rol=datos.rol,
        activo=True,
    )
    bd.add(nuevo)
    try:
        bd.commit()
        bd.refresh(nuevo)
    except IntegrityError:
        bd.rollback()
        raise HTTPException(status_code=409, detail="Esa identidad ya está vinculada.") from None
    return nuevo


@router.patch("/{id_usuario}", response_model=UsuarioDetalle)
def modificar_usuario(
    id_usuario: int,
    datos: UsuarioModificar,
    bd: SesionBD,
    administrador: Administrador,
):
    """Nunca permite desactivar al último administrador ni a sí mismo."""
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios or any(valor is None for valor in cambios.values()):
        raise HTTPException(status_code=422, detail="Indica cambios válidos y no nulos.")

    # El bloqueo serializa degradaciones/desactivaciones concurrentes de administradores.
    administradores = bd.exec(
        select(UsuarioInterno)
        .where(UsuarioInterno.rol == "administrador", UsuarioInterno.activo.is_(True))
        .order_by(UsuarioInterno.id_usuario)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).all()
    usuario = bd.get(UsuarioInterno, id_usuario, populate_existing=True)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario interno inexistente.")

    nuevo_rol = cambios.get("rol", usuario.rol)
    nuevo_activo = cambios.get("activo", usuario.activo)
    if usuario.id_usuario == administrador.id_usuario and (
        nuevo_rol != "administrador" or not nuevo_activo
    ):
        raise HTTPException(status_code=409, detail="No puedes quitarte tus privilegios ni desactivarte.")
    if usuario.rol == "administrador" and usuario.activo and (
        nuevo_rol != "administrador" or not nuevo_activo
    ) and len(administradores) <= 1:
        raise HTTPException(status_code=409, detail="Debe quedar al menos un administrador activo.")

    for clave, valor in cambios.items():
        setattr(usuario, clave, valor)
    bd.add(usuario)
    try:
        bd.commit()
        bd.refresh(usuario)
    except IntegrityError:
        bd.rollback()
        raise HTTPException(status_code=409, detail="Los cambios incumplen una restricción de la base.") from None
    return usuario
