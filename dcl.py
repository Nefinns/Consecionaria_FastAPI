import os

from dotenv import load_dotenv


load_dotenv()

#Obtener contraseñas de los usuarios

passwords = {
    "gerente": os.getenv("PASSWORD_GERENTE"),
    "vendedor": os.getenv("PASSWORD_VENDEDOR"),
    "vendedor_02": os.getenv("PASSWORD_VENDEDOR_02"),
    "recepcion": os.getenv("PASSWORD_RECEPCION"),
    "mecanico": os.getenv("PASSWORD_MECANICO"),
    "mecanico_02": os.getenv("PASSWORD_MECANICO_02"),
    "asesor_servicio": os.getenv("PASSWORD_ASESOR_SERVICIO"),
    "almacen": os.getenv("PASSWORD_ALMACEN"),
    "contador": os.getenv("PASSWORD_CONTADOR"),
    "compras": os.getenv("PASSWORD_COMPRAS"),
    "administrador": os.getenv("PASSWORD_ADMINISTRADOR"),
    "supervisor": os.getenv("PASSWORD_SUPERVISOR"),
    "proveedores": os.getenv("PASSWORD_PROVEEDORES"),
    "inventario": os.getenv("PASSWORD_INVENTARIO"),
    "auditor": os.getenv("PASSWORD_AUDITOR")
}

#Diccionario para crer roles/usuarios
dcl_usuarios = {
    "gerente": f"CREATE ROLE gerente LOGIN PASSWORD '{passwords['gerente']}';",

    "vendedor": f"CREATE ROLE vendedor LOGIN PASSWORD '{passwords['vendedor']}';",

    "vendedor_02": f"CREATE ROLE vendedor_02 LOGIN PASSWORD '{passwords['vendedor_02']}';",

    "recepcion": f"CREATE ROLE recepcion LOGIN PASSWORD '{passwords['recepcion']}';",

    "mecanico": f"CREATE ROLE mecanico LOGIN PASSWORD '{passwords['mecanico']}';",

    "mecanico_02": f"CREATE ROLE mecanico_02 LOGIN PASSWORD '{passwords['mecanico_02']}';",

    "asesor_servicio": f"CREATE ROLE asesor_servicio LOGIN PASSWORD '{passwords['asesor_servicio']}';",

    "almacen": f"CREATE ROLE almacen LOGIN PASSWORD '{passwords['almacen']}';",

    "contador": f"CREATE ROLE contador LOGIN PASSWORD '{passwords['contador']}';",

    "compras": f"CREATE ROLE compras LOGIN PASSWORD '{passwords['compras']}';",

    "administrador": f"CREATE ROLE administrador LOGIN PASSWORD '{passwords['administrador']}';",

    "supervisor": f"CREATE ROLE supervisor LOGIN PASSWORD '{passwords['supervisor']}';",

    "proveedores": f"CREATE ROLE proveedores LOGIN PASSWORD '{passwords['proveedores']}';",

    "inventario": f"CREATE ROLE inventario LOGIN PASSWORD '{passwords['inventario']}';",

    "auditor": f"CREATE ROLE auditor LOGIN PASSWORD '{passwords['auditor']}';"
}

#Diccionario para las consultas de asignación de permisos
dcl_grant = {
    "gerente": "GRANT SELECT ON TABLE public.cliente TO gerente;",

    "vendedor": "GRANT SELECT ON TABLE public.coche TO vendedor;",

    "vendedor_02": "GRANT INSERT ON TABLE public.cliente TO vendedor_02;",

    "recepcion": "GRANT SELECT ON TABLE public.revision TO recepcion;",

    "mecanico": "GRANT UPDATE ON TABLE public.revision TO mecanico;",

    "mecanico_02": "GRANT SELECT ON TABLE public.servicio TO mecanico_02;",

    "asesor_servicio": "GRANT INSERT ON TABLE public.servicio TO asesor_servicio;",

    "almacen": "GRANT SELECT ON TABLE public.proveedor TO almacen;",

    "contador": "GRANT SELECT ON TABLE public.cliente TO contador;",

    "compras": "GRANT INSERT ON TABLE public.proveedor TO compras;",

    "administrador": "GRANT UPDATE ON TABLE public.cliente TO administrador;",

    "supervisor": "GRANT UPDATE ON TABLE public.coche TO supervisor;",

    "proveedores": "GRANT UPDATE ON TABLE public.proveedor TO proveedores;",

    "inventario": "GRANT DELETE ON TABLE public.servicio TO inventario;",

    "auditor": "GRANT SELECT ON TABLE public.revision TO auditor;"
}

#Diccionario para revocar permisos
dcl_revoke = {
    "gerente": "REVOKE SELECT ON TABLE public.cliente FROM gerente;",

    "vendedor": "REVOKE SELECT ON TABLE public.coche FROM vendedor;",

    "vendedor_02": "REVOKE INSERT ON TABLE public.cliente FROM vendedor_02;",

    "recepcion": "REVOKE SELECT ON TABLE public.revision FROM recepcion;",

    "mecanico": "REVOKE UPDATE ON TABLE public.revision FROM mecanico;",

    "mecanico_02": "REVOKE SELECT ON TABLE public.servicio FROM mecanico_02;",

    "asesor_servicio": "REVOKE INSERT ON TABLE public.servicio FROM asesor_servicio;",

    "almacen": "REVOKE SELECT ON TABLE public.proveedor FROM almacen;",

    "contador": "REVOKE SELECT ON TABLE public.cliente FROM contador;",

    "compras": "REVOKE INSERT ON TABLE public.proveedor FROM compras;",

    "administrador": "REVOKE UPDATE ON TABLE public.cliente FROM administrador;",

    "supervisor": "REVOKE UPDATE ON TABLE public.coche FROM supervisor;",

    "proveedores": "REVOKE UPDATE ON TABLE public.proveedor FROM proveedores;",

    "inventario": "REVOKE DELETE ON TABLE public.servicio FROM inventario;",

    "auditor": "REVOKE SELECT ON TABLE public.revision FROM auditor;"
}

#Diccionario para eliminar roles/usuarios

dcl_drop_user = {
    "gerente": "DROP ROLE gerente;",

    "vendedor": "DROP ROLE vendedor;",

    "vendedor_02": "DROP ROLE vendedor_02;",

    "recepcion": "DROP ROLE recepcion;",

    "mecanico": "DROP ROLE mecanico;",

    "mecanico_02": "DROP ROLE mecanico_02;",

    "asesor_servicio": "DROP ROLE asesor_servicio;",

    "almacen": "DROP ROLE almacen;",

    "contador": "DROP ROLE contador;",

    "compras": "DROP ROLE compras;",

    "administrador": "DROP ROLE administrador;",

    "supervisor": "DROP ROLE supervisor;",

    "proveedores": "DROP ROLE proveedores;",

    "inventario": "DROP ROLE inventario;",

    "auditor": "DROP ROLE auditor;"
}