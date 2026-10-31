"""Ruta descriptiva: los endpoints /auth reales los proporciona el SDK."""
from fastapi import APIRouter

router = APIRouter(prefix="/ayuda", tags=["Ayuda"])


@router.get("/autenticacion")
def informacion_auth():
    """Guía de rutas gestionadas por SuperTokens (no registrar versiones duplicadas)."""
    return {
        "gestionado_por": "SuperTokens EmailPassword + Session",
        "flujos": {
            "registro": "POST /auth/signup",
            "login": "POST /auth/signin",
            "logout": "POST /auth/signout",
            "renovacion": "POST /auth/session/refresh",
            "solicitar_recuperacion": "POST /auth/user/password/reset/token",
            "establecer_contrasena": "POST /auth/user/password/reset",
        },
        "nota": "Las rutas las registra SuperTokens y requieren el formato FDI de su SDK frontend.",
        "perfil": "GET /usuarios/me",
        "usuarios_roles": "GET/POST/PATCH /usuarios (solo administrador)",
    }
