"""Dependencias obligatorias: sesión SuperTokens + permiso en Neon.

La autenticación nunca autoriza por sí misma. Un registro externo sin fila
activa en usuario_interno recibe 403. Las consultas son por solicitud.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.db.sesion import obtener_sesion
from app.models.usuario import UsuarioInterno

SesionBD = Annotated[Session, Depends(obtener_sesion)]


async def obtener_usuario_actual(
    bd: SesionBD,
    sesion_auth: SessionContainer = Depends(verify_session(check_database=True)),
) -> UsuarioInterno:
    """Verificar sesión real y autorización local, incluso tras desactivar usuario."""
    identidad = sesion_auth.get_user_id()
    usuario = bd.exec(
        select(UsuarioInterno).where(UsuarioInterno.identidad_externa == identidad)
    ).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta no está autorizada para la concesionaria.",
        )
    return usuario


def exigir_roles(*roles: str):
    """Aplicar RBAC del negocio en FastAPI (no en la interfaz React)."""
    def comprobar(usuario: Annotated[UsuarioInterno, Depends(obtener_usuario_actual)]) -> UsuarioInterno:
        if usuario.rol not in roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes.")
        return usuario
    return comprobar
