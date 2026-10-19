# Configuración exacta de los 15 GRANT del ejercicio 4.5.
dcl_usuarios = {
    'gerente': 'Gerencia', 'vendedor': 'Ventas', 'vendedor_02': 'Ventas 02',
    'recepcion': 'Recepción', 'mecanico': 'Mecánica', 'mecanico_02': 'Mecánica 02',
    'asesor_servicio': 'Asesoría de servicio', 'almacen': 'Almacén',
    'contador': 'Contabilidad', 'compras': 'Compras',
    'administrador': 'Administración', 'supervisor': 'Supervisión',
    'proveedores': 'Proveedores', 'inventario': 'Inventario',
    'auditor': 'Auditoría',
}

PERMISOS_OBJETIVO = {
    'gerente': ('cliente', 'SELECT'),
    'vendedor': ('coche', 'SELECT'),
    'vendedor_02': ('cliente', 'INSERT'),
    'recepcion': ('revision', 'SELECT'),
    'mecanico': ('revision', 'UPDATE'),
    'mecanico_02': ('servicio', 'SELECT'),
    'asesor_servicio': ('servicio', 'INSERT'),
    'almacen': ('proveedor', 'SELECT'),
    'contador': ('cliente', 'SELECT'),
    'compras': ('proveedor', 'INSERT'),
    'administrador': ('cliente', 'UPDATE'),
    'supervisor': ('coche', 'UPDATE'),
    'proveedores': ('proveedor', 'UPDATE'),
    'inventario': ('servicio', 'DELETE'),
    'auditor': ('revision', 'SELECT'),
}

dcl_grant = {nombre: [operacion] for nombre, (_, operacion) in PERMISOS_OBJETIVO.items()}
dcl_revoke = {nombre: permisos.copy() for nombre, permisos in dcl_grant.items()}
dcl_tablas = {nombre: [tabla] for nombre, (tabla, _) in PERMISOS_OBJETIVO.items()}
OPERACIONES_PERMITIDAS = {'SELECT', 'INSERT', 'UPDATE', 'DELETE'}
TABLAS_CONCESIONARIA = (
    'cliente', 'proveedor', 'coche', 'servicio', 'refaccion',
    'revision', 'orden_servicio', 'detalle_orden_servicio',
)
