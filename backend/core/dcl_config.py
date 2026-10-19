
# Roles de PostgreSQL para la actividad 4.5.
# Cambia los nombres o permisos según los requisitos del profesor.

dcl_usuarios = {
    "director": "Dirección general",
    "ventas_tienda": "Personal de ventas",
    "recepcion": "Recepción",
    "control_escolar": "Control escolar",
    "consulta_catalogo": "Consulta del catálogo",
    "captura_catalogo": "Captura del catálogo",
    "almacen": "Personal de almacén",
    "contabilidad": "Contabilidad",
    "compras": "Compras y abastecimiento",
    "auditor": "Auditoría de información",
}

# Permisos por rol. Cada entrada es una lista de sentencias permitidas.
# Los nombres de tabla se limitan a tablas de este esquema.

dcl_grant = {
    "director": [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
    ],
    "ventas_tienda": [
        "SELECT",
        "INSERT",
    ],
    "recepcion": [
        "SELECT",
    ],
    "control_escolar": [
        "SELECT",
        "INSERT",
        "UPDATE",
    ],
    "consulta_catalogo": [
        "SELECT",
    ],
    "captura_catalogo": [
        "SELECT",
        "INSERT",
        "UPDATE",
    ],
    "almacen": [
        "SELECT",
        "UPDATE",
    ],
    "contabilidad": [
        "SELECT",
        "INSERT",
        "UPDATE",
    ],
    "compras": [
        "SELECT",
        "INSERT",
        "UPDATE",
    ],
    "auditor": [
        "SELECT",
    ],
}

# Lista explícita de operaciones que el backend puede revocar.
dcl_revoke = {
    usuario: permisos.copy()
    for usuario, permisos in dcl_grant.items()
}

TABLAS_PERMITIDAS = {
    "usuario",
    "cliente",
    "administrador",
    "maestro",
    "periodo_academico",
    "categoria_instrumento",
    "instrumento",
    "clase",
    "horario_clase",
    "inscripcion_clase",
    "pago_clase",
    "venta",
    "detalle_venta",
    "proveedor",
    "orden_abastecimiento",
    "detalle_orden",
}

OPERACIONES_PERMITIDAS = {"SELECT", "INSERT", "UPDATE", "DELETE"}
