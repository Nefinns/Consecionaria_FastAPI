-- Tabla CLIENTE

CREATE TABLE cliente (
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
);


-- Tabla COCHE

CREATE TABLE coche (
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
);


-- Tabla REVISION

CREATE TABLE revision (
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
);