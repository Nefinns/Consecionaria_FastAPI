"""Configuración central del proveedor de identidad y sesiones.

Las credenciales permanecen en variables de entorno o backend/.env.
La receta EmailPassword expone los flujos oficiales bajo /auth.
"""
from functools import lru_cache
from urllib.parse import urlparse

from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.recipe import emailpassword, session

from app.core.config import obtener_valores_entorno


@lru_cache
def configuracion_auth() -> dict[str, str]:
    valores = obtener_valores_entorno()
    requeridas = (
        "SUPERTOKENS_CONNECTION_URI", "SUPERTOKENS_API_KEY",
        "API_DOMAIN", "WEBSITE_DOMAIN",
    )
    faltantes = [campo for campo in requeridas if not str(valores.get(campo) or "").strip()]
    if faltantes:
        raise RuntimeError("Faltan variables de autenticación: " + ", ".join(faltantes))

    config = {campo: str(valores[campo]).strip().rstrip("/") for campo in requeridas}
    api = urlparse(config["API_DOMAIN"])
    web = urlparse(config["WEBSITE_DOMAIN"])
    core = urlparse(config["SUPERTOKENS_CONNECTION_URI"])
    if core.scheme != "https" or not core.hostname or core.username or core.password:
        raise ValueError("SUPERTOKENS_CONNECTION_URI debe ser HTTPS (servicio Managed).")
    for url in (api, web):
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            raise ValueError("API_DOMAIN y WEBSITE_DOMAIN deben ser orígenes HTTP(S) válidos.")
        if url.scheme == "http" and url.hostname not in {"localhost", "127.0.0.1"}:
            raise ValueError("Los dominios remotos deben usar HTTPS.")
        if url.path not in {"", "/"} or url.query or url.fragment:
            raise ValueError("API_DOMAIN y WEBSITE_DOMAIN no deben incluir rutas ni parámetros.")
    return config


def iniciar_supertokens() -> None:
    """Registrar las recetas una vez al importar main; el SDK administra /auth."""
    c = configuracion_auth()
    init(
        framework="fastapi",
        mode="asgi",
        app_info=InputAppInfo(
            app_name="Concesionaria",
            api_domain=c["API_DOMAIN"],
            website_domain=c["WEBSITE_DOMAIN"],
            api_base_path="/auth",
            website_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=c["SUPERTOKENS_CONNECTION_URI"],
            api_key=c["SUPERTOKENS_API_KEY"],
        ),
        recipe_list=[emailpassword.init(), session.init()],
        telemetry=False,
    )
