
# Configuración DCL de Concesionaria
# Actividad 4.5: Administración de usuarios y permisos
# Base de datos PostgreSQL

# Usuarios autorizados para las operaciones DCL

dcl_usuarios = {
    "gerente": "Gerente de la concesionaria",
    "vendedor": "Vendedor de vehículos",
    "vendedor_02": "Segundo vendedor",
    "recepcion": "Personal de recepción",
    "mecanico": "Mecánico de taller",
    "mecanico_02": "Segundo mecánico",
    "asesor_servicio": "Asesor de servicio",
    "almacen": "Encargado de almacén",
    "contador": "Personal de contabilidad",
    "compras": "Encargado de compras",
    "administrador": "Administrador de la concesionaria",
    "supervisor": "Supervisor de operaciones",
    "proveedores": "Gestión de proveedores",
    "inventario": "Control de inventario",
    "auditor": "Auditor de registros",
}

# Operaciones SQL permitidas para cada usuario
# Se conservan los permisos definidos en el script original

dcl_grant = {
    "gerente": ["SELECT"],
    "vendedor": ["SELECT"],
    "vendedor_02": ["INSERT"],
    "recepcion": ["SELECT"],
    "mecanico": ["UPDATE"],
    "mecanico_02": ["SELECT"],
    "asesor_servicio": ["INSERT"],
    "almacen": ["SELECT"],
    "contador": ["SELECT"],
    "compras": ["INSERT"],
    "administrador": ["UPDATE"],
    "supervisor": ["UPDATE"],
    "proveedores": ["UPDATE"],
    "inventario": ["DELETE"],
    "auditor": ["SELECT"],
}

# Tablas autorizadas por usuario
# Relación basada en los GRANT del archivo SQL original

dcl_tablas = {
    "gerente": ["cliente"],
    "vendedor": ["coche"],
    "vendedor_02": ["cliente"],
    "recepcion": ["revision"],
    "mecanico": ["revision"],
    "mecanico_02": ["servicio"],
    "asesor_servicio": ["servicio"],
    "almacen": ["proveedor"],
    "contador": ["cliente"],
    "compras": ["proveedor"],
    "administrador": ["cliente"],
    "supervisor": ["coche"],
    "proveedores": ["proveedor"],
    "inventario": ["servicio"],
    "auditor": ["revision"],
}

# Permisos que se pueden revocar
# Se permite revocar las mismas operaciones configuradas para GRANT

dcl_revoke = {
    usuario: permisos.copy()
    for usuario, permisos in dcl_grant.items()
}

# Operaciones DCL compatibles

OPERACIONES_PERMITIDAS = {
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
}

# Tablas válidas del esquema de Concesionaria

TABLAS_CONCESIONARIA = {
    "cliente",
    "proveedor",
    "coche",
    "servicio",
    "refaccion",
    "revision",
    "orden_servicio",
    "detalle_orden_servicio",
}
