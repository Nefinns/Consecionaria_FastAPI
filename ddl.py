
# Consultas CREATE
crear_cliente = """CREATE TABLE cliente (
    codigo_cliente INTEGER GENERATED ALWAYS AS IDENTITY,
    nif CHAR(9) NOT NULL,
    nombre_cliente VARCHAR(80) NOT NULL,
    direccion VARCHAR(100) NOT NULL,
    ciudad VARCHAR(40) NOT NULL,
    telefono CHAR(10) NOT NULL,

    CONSTRAINT pk_cliente
        PRIMARY KEY (codigo_cliente),

    CONSTRAINT uq_cliente_nif
        UNIQUE (nif)
);"""

crear_coche = """CREATE TABLE coche (
    matricula CHAR(7) NOT NULL,
    marca VARCHAR(30) NOT NULL,
    modelo VARCHAR(30) NOT NULL,
    color VARCHAR(20) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    codigo_cliente INTEGER,

    CONSTRAINT pk_coche
        PRIMARY KEY (matricula),

    CONSTRAINT fk_coche_cliente
        FOREIGN KEY (codigo_cliente)
        REFERENCES cliente(codigo_cliente)
);"""

crear_revision = """CREATE TABLE revision (
    codigo_revision INTEGER GENERATED ALWAYS AS IDENTITY,
    fecha_revision DATE NOT NULL,
    cambio_filtro CHAR(1) NOT NULL,
    cambio_aceite CHAR(1) NOT NULL,
    cambio_frenos CHAR(1) NOT NULL,
    otros VARCHAR(120),
    matricula CHAR(7) NOT NULL,

    CONSTRAINT pk_revision
        PRIMARY KEY (codigo_revision),

    CONSTRAINT fk_revision_coche
        FOREIGN KEY (matricula)
        REFERENCES coche(matricula),

    CONSTRAINT chk_cambio_filtro
        CHECK (cambio_filtro IN ('S', 'N')),

    CONSTRAINT chk_cambio_aceite
        CHECK (cambio_aceite IN ('S', 'N')),

    CONSTRAINT chk_cambio_frenos
        CHECK (cambio_frenos IN ('S', 'N'))
);"""

crear_proveedor = """CREATE TABLE proveedor (
    codigo_proveedor INTEGER GENERATED ALWAYS AS IDENTITY,
    nombre_proveedor VARCHAR(80) NOT NULL,
    direccion VARCHAR(100) NOT NULL,
    ciudad VARCHAR(40) NOT NULL,
    telefono CHAR(10) NOT NULL,
    correo VARCHAR(100) NOT NULL,

    CONSTRAINT pk_proveedor
        PRIMARY KEY (codigo_proveedor),

    CONSTRAINT uq_proveedor_correo
        UNIQUE (correo)
);"""

crear_servicio = """CREATE TABLE servicio (
    codigo_servicio INTEGER GENERATED ALWAYS AS IDENTITY,
    nombre_servicio VARCHAR(80) NOT NULL,
    descripcion VARCHAR(200),
    costo DECIMAL(10,2) NOT NULL,

    CONSTRAINT pk_servicio
        PRIMARY KEY (codigo_servicio),

    CONSTRAINT ck_servicio_costo
        CHECK (costo >= 0)
);"""

# Consultas ALTER
alterar_cliente = """ALTER TABLE cliente
ADD COLUMN correo VARCHAR(100);
"""

alterar_coche = """ALTER TABLE coche
ADD COLUMN year INTEGER;"""

alterar_revision = """ALTER TABLE revision
ADD COLUMN costo DECIMAL(10,2);"""

alterar_proveedor = """ALTER TABLE proveedor
ADD COLUMN contacto VARCHAR(80);"""

alterar_servicio = """ALTER TABLE servicio
ADD COLUMN duracion_minutos INTEGER;"""

# Consultas DROP

borrar_servicio = """DROP TABLE servicio;"""

borrar_proveedor = """DROP TABLE proveedor;"""

borrar_revision = """DROP TABLE revision;"""

borrar_coche = """DROP TABLE coche;"""

borrar_cliente = """DROP TABLE cliente;"""

ddl_create = {
    "cliente": crear_cliente,
    "coche": crear_coche,
    "revision": crear_revision,
    "proveedor": crear_proveedor,
    "servicio": crear_servicio
}

ddl_alter = {
    "cliente": alterar_cliente,
    "coche": alterar_coche,
    "revision": alterar_revision,
    "proveedor": alterar_proveedor,
    "servicio": alterar_servicio
}

ddl_drop = {
    "revision": borrar_revision,
    "coche": borrar_coche,
    "cliente": borrar_cliente,
    "servicio": borrar_servicio,
    "proveedor": borrar_proveedor
}
