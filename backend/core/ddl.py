
ddl_create = {
    "usuario": """
        CREATE TABLE usuario (
            id_usuario SERIAL PRIMARY KEY,
            nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(150) NOT NULL,
            fecha_nacimiento DATE,
            curp CHAR(18) NOT NULL UNIQUE,
            ine VARCHAR(20) UNIQUE,
            correo VARCHAR(150) NOT NULL UNIQUE,
            telefono VARCHAR(20),
            direccion VARCHAR(255),
            contrasena_hash VARCHAR(255) NOT NULL,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_usuario_curp
                CHECK (LENGTH(TRIM(curp)) = 18),
            CONSTRAINT chk_usuario_correo
                CHECK (correo ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$'),
            CONSTRAINT chk_usuario_nombre_usuario
                CHECK (LENGTH(TRIM(nombre_usuario)) > 0)
        );
    """,

    "cliente": """
        CREATE TABLE cliente (
            id_cliente SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL UNIQUE,
            fecha_alta DATE NOT NULL DEFAULT CURRENT_DATE,
            CONSTRAINT fk_cliente_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuario(id_usuario)
        );
    """,

    "administrador": """
        CREATE TABLE administrador (
            id_administrador SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL UNIQUE,
            fecha_contratacion DATE,
            CONSTRAINT fk_administrador_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuario(id_usuario)
        );
    """,

    "maestro": """
        CREATE TABLE maestro (
            id_maestro SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL UNIQUE,
            especialidad VARCHAR(100) NOT NULL,
            fecha_contratacion DATE,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            CONSTRAINT fk_maestro_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuario(id_usuario),
            CONSTRAINT chk_maestro_especialidad
                CHECK (LENGTH(TRIM(especialidad)) > 0)
        );
    """,

    "periodo_academico": """
        CREATE TABLE periodo_academico (
            id_periodo SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'Planificado',
            CONSTRAINT chk_periodo_fechas
                CHECK (fecha_fin >= fecha_inicio),
            CONSTRAINT chk_periodo_estado
                CHECK (estado IN (
                    'Planificado', 'En curso',
                    'Finalizado', 'Cancelado'
                ))
        );
    """,

    "categoria_instrumento": """
        CREATE TABLE categoria_instrumento (
            id_categoria SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT,
            CONSTRAINT chk_categoria_nombre
                CHECK (LENGTH(TRIM(nombre)) > 0)
        );
    """,

    "instrumento": """
        CREATE TABLE instrumento (
            id_instrumento SERIAL PRIMARY KEY,
            id_categoria INTEGER NOT NULL,
            nombre_instrumento VARCHAR(150) NOT NULL,
            marca VARCHAR(100),
            modelo VARCHAR(100),
            tamano VARCHAR(50),
            color VARCHAR(50),
            precio NUMERIC(10, 2) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            CONSTRAINT fk_instrumento_categoria
                FOREIGN KEY (id_categoria)
                REFERENCES categoria_instrumento(id_categoria),
            CONSTRAINT chk_instrumento_precio
                CHECK (precio > 0),
            CONSTRAINT chk_instrumento_stock
                CHECK (stock >= 0),
            CONSTRAINT chk_instrumento_nombre
                CHECK (LENGTH(TRIM(nombre_instrumento)) > 0)
        );
    """,

    "clase": """
        CREATE TABLE clase (
            id_clase SERIAL PRIMARY KEY,
            id_maestro INTEGER NOT NULL,
            id_instrumento INTEGER NOT NULL,
            id_periodo INTEGER NOT NULL,
            nombre VARCHAR(150) NOT NULL,
            nivel VARCHAR(20) NOT NULL,
            costo NUMERIC(10, 2) NOT NULL DEFAULT 0,
            cupo INTEGER NOT NULL,
            activa BOOLEAN NOT NULL DEFAULT TRUE,
            CONSTRAINT fk_clase_maestro
                FOREIGN KEY (id_maestro)
                REFERENCES maestro(id_maestro),
            CONSTRAINT fk_clase_instrumento
                FOREIGN KEY (id_instrumento)
                REFERENCES instrumento(id_instrumento),
            CONSTRAINT fk_clase_periodo
                FOREIGN KEY (id_periodo)
                REFERENCES periodo_academico(id_periodo),
            CONSTRAINT chk_clase_costo
                CHECK (costo >= 0),
            CONSTRAINT chk_clase_cupo
                CHECK (cupo > 0),
            CONSTRAINT chk_clase_nivel
                CHECK (nivel IN (
                    'Inicial', 'Intermedio', 'Avanzado'
                ))
        );
    """,

    "horario_clase": """
        CREATE TABLE horario_clase (
            id_horario SERIAL PRIMARY KEY,
            id_clase INTEGER NOT NULL,
            dia VARCHAR(15) NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            salon VARCHAR(50),
            CONSTRAINT fk_horario_clase
                FOREIGN KEY (id_clase)
                REFERENCES clase(id_clase),
            CONSTRAINT chk_horario_dia
                CHECK (dia IN (
                    'Lunes', 'Martes', 'Miércoles',
                    'Jueves', 'Viernes', 'Sábado', 'Domingo'
                )),
            CONSTRAINT chk_horario_horas
                CHECK (hora_fin > hora_inicio)
        );
    """,

    "inscripcion_clase": """
        CREATE TABLE inscripcion_clase (
            id_inscripcion SERIAL PRIMARY KEY,
            id_cliente INTEGER NOT NULL,
            id_clase INTEGER NOT NULL,
            fecha_inscripcion DATE NOT NULL DEFAULT CURRENT_DATE,
            costo_mensual_acordado NUMERIC(10, 2) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'Activa',
            CONSTRAINT fk_inscripcion_cliente
                FOREIGN KEY (id_cliente)
                REFERENCES cliente(id_cliente),
            CONSTRAINT fk_inscripcion_clase
                FOREIGN KEY (id_clase)
                REFERENCES clase(id_clase),
            CONSTRAINT chk_inscripcion_costo
                CHECK (costo_mensual_acordado >= 0),
            CONSTRAINT chk_inscripcion_estado
                CHECK (estado IN (
                    'Activa', 'Cancelada', 'Finalizada'
                ))
        );
    """,

    "pago_clase": """
        CREATE TABLE pago_clase (
            id_pago SERIAL PRIMARY KEY,
            id_inscripcion INTEGER NOT NULL,
            periodo_pagado DATE NOT NULL,
            importe NUMERIC(10, 2) NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            fecha_pago DATE,
            metodo_pago VARCHAR(30),
            estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
            CONSTRAINT fk_pago_inscripcion
                FOREIGN KEY (id_inscripcion)
                REFERENCES inscripcion_clase(id_inscripcion),
            CONSTRAINT chk_pago_importe
                CHECK (importe >= 0),
            CONSTRAINT chk_pago_estado
                CHECK (estado IN (
                    'Pendiente', 'Pagado', 'Vencido', 'Cancelado'
                )),
            CONSTRAINT chk_pago_fechas
                CHECK (fecha_vencimiento >= periodo_pagado)
        );
    """,

    "venta": """
        CREATE TABLE venta (
            id_venta SERIAL PRIMARY KEY,
            id_cliente INTEGER NOT NULL,
            id_administrador INTEGER NOT NULL,
            fecha_venta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            metodo_pago VARCHAR(30) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'Completada',
            CONSTRAINT fk_venta_cliente
                FOREIGN KEY (id_cliente)
                REFERENCES cliente(id_cliente),
            CONSTRAINT fk_venta_administrador
                FOREIGN KEY (id_administrador)
                REFERENCES administrador(id_administrador),
            CONSTRAINT chk_venta_metodo_pago
                CHECK (metodo_pago IN (
                    'Efectivo', 'Tarjeta', 'Transferencia'
                )),
            CONSTRAINT chk_venta_estado
                CHECK (estado IN (
                    'Completada', 'Pendiente', 'Cancelada'
                ))
        );
    """,

    "detalle_venta": """
        CREATE TABLE detalle_venta (
            id_venta INTEGER NOT NULL,
            id_instrumento INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario NUMERIC(10, 2) NOT NULL,
            PRIMARY KEY (id_venta, id_instrumento),
            CONSTRAINT fk_detalle_venta_venta
                FOREIGN KEY (id_venta)
                REFERENCES venta(id_venta),
            CONSTRAINT fk_detalle_venta_instrumento
                FOREIGN KEY (id_instrumento)
                REFERENCES instrumento(id_instrumento),
            CONSTRAINT chk_detalle_venta_cantidad
                CHECK (cantidad > 0),
            CONSTRAINT chk_detalle_venta_precio
                CHECK (precio_unitario >= 0)
        );
    """,

    "proveedor": """
        CREATE TABLE proveedor (
            id_proveedor SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            rfc VARCHAR(13) NOT NULL UNIQUE,
            correo VARCHAR(150),
            direccion VARCHAR(255),
            telefono VARCHAR(20),
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            CONSTRAINT chk_proveedor_rfc
                CHECK (LENGTH(TRIM(rfc)) IN (12, 13)),
            CONSTRAINT chk_proveedor_nombre
                CHECK (LENGTH(TRIM(nombre)) > 0)
        );
    """,

    "orden_abastecimiento": """
        CREATE TABLE orden_abastecimiento (
            id_orden SERIAL PRIMARY KEY,
            id_proveedor INTEGER NOT NULL,
            id_administrador INTEGER NOT NULL,
            fecha_orden TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
            CONSTRAINT fk_orden_proveedor
                FOREIGN KEY (id_proveedor)
                REFERENCES proveedor(id_proveedor),
            CONSTRAINT fk_orden_administrador
                FOREIGN KEY (id_administrador)
                REFERENCES administrador(id_administrador),
            CONSTRAINT chk_orden_estado
                CHECK (estado IN (
                    'Pendiente', 'Enviada',
                    'Recibida', 'Cancelada'
                ))
        );
    """,

    "detalle_orden": """
        CREATE TABLE detalle_orden (
            id_orden INTEGER NOT NULL,
            id_instrumento INTEGER NOT NULL,
            cantidad_solicitada INTEGER NOT NULL,
            cantidad_recibida INTEGER NOT NULL DEFAULT 0,
            costo_unitario NUMERIC(10, 2) NOT NULL,
            PRIMARY KEY (id_orden, id_instrumento),
            CONSTRAINT fk_detalle_orden_orden
                FOREIGN KEY (id_orden)
                REFERENCES orden_abastecimiento(id_orden),
            CONSTRAINT fk_detalle_orden_instrumento
                FOREIGN KEY (id_instrumento)
                REFERENCES instrumento(id_instrumento),
            CONSTRAINT chk_detalle_orden_solicitada
                CHECK (cantidad_solicitada > 0),
            CONSTRAINT chk_detalle_orden_recibida
                CHECK (
                    cantidad_recibida >= 0
                    AND cantidad_recibida <= cantidad_solicitada
                ),
            CONSTRAINT chk_detalle_orden_costo
                CHECK (costo_unitario >= 0)
        );
    """
}


ddl_indices = {
    "idx_instrumento_categoria":
        "CREATE INDEX idx_instrumento_categoria ON instrumento(id_categoria)",

    "idx_instrumento_nombre":
        "CREATE INDEX idx_instrumento_nombre ON instrumento(nombre_instrumento)",

    "idx_clase_maestro":
        "CREATE INDEX idx_clase_maestro ON clase(id_maestro)",

    "idx_clase_instrumento":
        "CREATE INDEX idx_clase_instrumento ON clase(id_instrumento)",

    "idx_clase_periodo":
        "CREATE INDEX idx_clase_periodo ON clase(id_periodo)",

    "idx_horario_clase":
        "CREATE INDEX idx_horario_clase ON horario_clase(id_clase)",

    "idx_inscripcion_cliente":
        "CREATE INDEX idx_inscripcion_cliente ON inscripcion_clase(id_cliente)",

    "idx_inscripcion_clase":
        "CREATE INDEX idx_inscripcion_clase ON inscripcion_clase(id_clase)",

    "idx_pago_inscripcion":
        "CREATE INDEX idx_pago_inscripcion ON pago_clase(id_inscripcion)",

    "idx_pago_estado_vencimiento":
        "CREATE INDEX idx_pago_estado_vencimiento ON pago_clase(estado, fecha_vencimiento)",

    "idx_venta_cliente":
        "CREATE INDEX idx_venta_cliente ON venta(id_cliente)",

    "idx_venta_administrador":
        "CREATE INDEX idx_venta_administrador ON venta(id_administrador)",

    "idx_venta_fecha":
        "CREATE INDEX idx_venta_fecha ON venta(fecha_venta)",

    "idx_detalle_venta_instrumento":
        "CREATE INDEX idx_detalle_venta_instrumento ON detalle_venta(id_instrumento)",

    "idx_orden_proveedor":
        "CREATE INDEX idx_orden_proveedor ON orden_abastecimiento(id_proveedor)",

    "idx_orden_administrador":
        "CREATE INDEX idx_orden_administrador ON orden_abastecimiento(id_administrador)",

    "idx_detalle_orden_instrumento":
        "CREATE INDEX idx_detalle_orden_instrumento ON detalle_orden(id_instrumento)"
}


ddl_drop = {
    "detalle_orden":
        "DROP TABLE IF EXISTS detalle_orden",

    "orden_abastecimiento":
        "DROP TABLE IF EXISTS orden_abastecimiento",

    "proveedor":
        "DROP TABLE IF EXISTS proveedor",

    "detalle_venta":
        "DROP TABLE IF EXISTS detalle_venta",

    "venta":
        "DROP TABLE IF EXISTS venta",

    "pago_clase":
        "DROP TABLE IF EXISTS pago_clase",

    "inscripcion_clase":
        "DROP TABLE IF EXISTS inscripcion_clase",

    "horario_clase":
        "DROP TABLE IF EXISTS horario_clase",

    "clase":
        "DROP TABLE IF EXISTS clase",

    "instrumento":
        "DROP TABLE IF EXISTS instrumento",

    "categoria_instrumento":
        "DROP TABLE IF EXISTS categoria_instrumento",

    "periodo_academico":
        "DROP TABLE IF EXISTS periodo_academico",

    "maestro":
        "DROP TABLE IF EXISTS maestro",

    "administrador":
        "DROP TABLE IF EXISTS administrador",

    "cliente":
        "DROP TABLE IF EXISTS cliente",

    "usuario":
        "DROP TABLE IF EXISTS usuario"
}
