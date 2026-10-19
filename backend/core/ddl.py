# Esquema de Concesionaria para PostgreSQL
# Compatible con backend/routers/schema.py
# El backend ejecuta ddl_create y ddl_indices dentro de engine.begin().
# No agregar BEGIN, COMMIT o ROLLBACK en estas cadenas.

ddl_create = {
    "cliente": """
        CREATE TABLE cliente (
         codigo_cliente INTEGER GENERATED ALWAYS AS IDENTITY,
         nif CHAR(9) NOT NULL,
         nombre_cliente VARCHAR(80) NOT NULL,
         direccion VARCHAR(100) NOT NULL,
         ciudad VARCHAR(40) NOT NULL DEFAULT 'Guadalajara',
         telefono CHAR(10) NOT NULL,
         correo VARCHAR(100) NOT NULL,
         fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
         activo BOOLEAN NOT NULL DEFAULT TRUE,
         CONSTRAINT pk_cliente PRIMARY KEY (codigo_cliente),
         CONSTRAINT uq_cliente_nif UNIQUE (nif),
         CONSTRAINT uq_cliente_correo UNIQUE (correo),
         CONSTRAINT chk_cliente_nif CHECK (nif ~ '^[A-Z0-9]{9}$')
        )
    """,

    "proveedor": """
        CREATE TABLE proveedor (
         codigo_proveedor INTEGER GENERATED ALWAYS AS IDENTITY,
         nombre_proveedor VARCHAR(80) NOT NULL,
         direccion VARCHAR(100) NOT NULL,
         ciudad VARCHAR(40) NOT NULL DEFAULT 'Guadalajara',
         telefono CHAR(10) NOT NULL,
         correo VARCHAR(100) NOT NULL,
         activo BOOLEAN NOT NULL DEFAULT TRUE,
         CONSTRAINT pk_proveedor PRIMARY KEY (codigo_proveedor),
         CONSTRAINT uq_proveedor_correo UNIQUE (correo),
         CONSTRAINT chk_proveedor_correo CHECK (POSITION('@' IN correo) > 1)
        )
    """,

    "coche": """
        CREATE TABLE coche (
         matricula CHAR(7) NOT NULL,
         marca VARCHAR(30) NOT NULL,
         modelo VARCHAR(30) NOT NULL,
         color VARCHAR(20) NOT NULL DEFAULT 'Blanco',
         anio SMALLINT NOT NULL,
         precio_venta DECIMAL(10,2) NOT NULL,
         codigo_cliente INTEGER,
         fecha_alta DATE NOT NULL DEFAULT CURRENT_DATE,
         disponible BOOLEAN NOT NULL DEFAULT TRUE,
         CONSTRAINT pk_coche PRIMARY KEY (matricula),
         CONSTRAINT fk_coche_cliente FOREIGN KEY (codigo_cliente) REFERENCES cliente(codigo_cliente) ON UPDATE CASCADE ON DELETE SET NULL,
         CONSTRAINT chk_coche_anio CHECK (anio BETWEEN 1980 AND 2035),
         CONSTRAINT chk_coche_precio CHECK (precio_venta > 0),
         CONSTRAINT chk_coche_matricula CHECK (matricula ~ '^[A-Z0-9]{7}$')
        )
    """,

    "servicio": """
        CREATE TABLE servicio (
         codigo_servicio INTEGER GENERATED ALWAYS AS IDENTITY,
         nombre_servicio VARCHAR(80) NOT NULL,
         descripcion VARCHAR(200),
         costo DECIMAL(10,2) NOT NULL DEFAULT 0,
         duracion_minutos INTEGER NOT NULL DEFAULT 30,
         activo BOOLEAN NOT NULL DEFAULT TRUE,
         CONSTRAINT pk_servicio PRIMARY KEY (codigo_servicio),
         CONSTRAINT uq_servicio_nombre UNIQUE (nombre_servicio),
         CONSTRAINT ck_servicio_costo CHECK (costo >= 0),
         CONSTRAINT ck_servicio_duracion CHECK (duracion_minutos > 0)
        )
    """,

    "refaccion": """
        CREATE TABLE refaccion (
         codigo_refaccion INTEGER GENERATED ALWAYS AS IDENTITY,
         codigo_proveedor INTEGER NOT NULL,
         nombre_refaccion VARCHAR(80) NOT NULL,
         descripcion VARCHAR(200),
         precio DECIMAL(10,2) NOT NULL,
         existencia INTEGER NOT NULL DEFAULT 0,
         CONSTRAINT pk_refaccion PRIMARY KEY (codigo_refaccion),
         CONSTRAINT fk_refaccion_proveedor FOREIGN KEY (codigo_proveedor) REFERENCES proveedor(codigo_proveedor) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT uq_refaccion_proveedor_nombre UNIQUE (codigo_proveedor, nombre_refaccion),
         CONSTRAINT chk_refaccion_precio CHECK (precio >= 0),
         CONSTRAINT chk_refaccion_existencia CHECK (existencia >= 0)
        )
    """,

    "revision": """
        CREATE TABLE revision (
         codigo_revision INTEGER GENERATED ALWAYS AS IDENTITY,
         fecha_revision DATE NOT NULL DEFAULT CURRENT_DATE,
         cambio_filtro CHAR(1) NOT NULL DEFAULT 'N',
         cambio_aceite CHAR(1) NOT NULL DEFAULT 'N',
         cambio_frenos CHAR(1) NOT NULL DEFAULT 'N',
         otros VARCHAR(120),
         matricula CHAR(7) NOT NULL,
         kilometraje INTEGER NOT NULL DEFAULT 0,
         CONSTRAINT pk_revision PRIMARY KEY (codigo_revision),
         CONSTRAINT fk_revision_coche FOREIGN KEY (matricula) REFERENCES coche(matricula) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT chk_cambio_filtro CHECK (cambio_filtro IN ('S','N')),
         CONSTRAINT chk_cambio_aceite CHECK (cambio_aceite IN ('S','N')),
         CONSTRAINT chk_cambio_frenos CHECK (cambio_frenos IN ('S','N')),
         CONSTRAINT chk_revision_kilometraje CHECK (kilometraje >= 0)
        )
    """,

    "orden_servicio": """
        CREATE TABLE orden_servicio (
         codigo_orden INTEGER GENERATED ALWAYS AS IDENTITY,
         codigo_cliente INTEGER NOT NULL,
         matricula CHAR(7) NOT NULL,
         fecha_orden DATE NOT NULL DEFAULT CURRENT_DATE,
         estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
         observaciones VARCHAR(250),
         CONSTRAINT pk_orden_servicio PRIMARY KEY (codigo_orden),
         CONSTRAINT fk_orden_cliente FOREIGN KEY (codigo_cliente) REFERENCES cliente(codigo_cliente) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT fk_orden_coche FOREIGN KEY (matricula) REFERENCES coche(matricula) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT chk_orden_estado CHECK (estado IN ('Pendiente','En proceso','Terminada','Cancelada'))
        )
    """,

    "detalle_orden_servicio": """
        CREATE TABLE detalle_orden_servicio (
         codigo_detalle INTEGER GENERATED ALWAYS AS IDENTITY,
         codigo_orden INTEGER NOT NULL,
         codigo_servicio INTEGER,
         codigo_refaccion INTEGER,
         cantidad INTEGER NOT NULL DEFAULT 1,
         precio_unitario DECIMAL(10,2) NOT NULL,
         CONSTRAINT pk_detalle_orden PRIMARY KEY (codigo_detalle),
         CONSTRAINT fk_detalle_orden FOREIGN KEY (codigo_orden) REFERENCES orden_servicio(codigo_orden) ON UPDATE CASCADE ON DELETE CASCADE,
         CONSTRAINT fk_detalle_servicio FOREIGN KEY (codigo_servicio) REFERENCES servicio(codigo_servicio) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT fk_detalle_refaccion FOREIGN KEY (codigo_refaccion) REFERENCES refaccion(codigo_refaccion) ON UPDATE CASCADE ON DELETE RESTRICT,
         CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
         CONSTRAINT chk_detalle_precio CHECK (precio_unitario >= 0),
         CONSTRAINT chk_detalle_un_tipo CHECK ((codigo_servicio IS NOT NULL AND codigo_refaccion IS NULL) OR (codigo_servicio IS NULL AND codigo_refaccion IS NOT NULL))
        )
    """,

}

ddl_indices = {
    "idx_coche_codigo_cliente": """
        CREATE INDEX idx_coche_codigo_cliente ON coche(codigo_cliente)
    """,

    "idx_revision_matricula": """
        CREATE INDEX idx_revision_matricula ON revision(matricula)
    """,

    "idx_revision_fecha": """
        CREATE INDEX idx_revision_fecha ON revision(fecha_revision)
    """,

    "idx_refaccion_codigo_proveedor": """
        CREATE INDEX idx_refaccion_codigo_proveedor ON refaccion(codigo_proveedor)
    """,

    "idx_orden_cliente": """
        CREATE INDEX idx_orden_cliente ON orden_servicio(codigo_cliente)
    """,

    "idx_orden_matricula": """
        CREATE INDEX idx_orden_matricula ON orden_servicio(matricula)
    """,

    "idx_orden_fecha": """
        CREATE INDEX idx_orden_fecha ON orden_servicio(fecha_orden)
    """,

    "idx_detalle_codigo_orden": """
        CREATE INDEX idx_detalle_codigo_orden ON detalle_orden_servicio(codigo_orden)
    """,

}

# Orden inverso para respetar relaciones entre tablas.
# Cuidado: /ddl/drop-all elimina las ocho tablas y sus datos.
ddl_drop = {
    "detalle_orden_servicio": """
        DROP TABLE detalle_orden_servicio
    """,

    "orden_servicio": """
        DROP TABLE orden_servicio
    """,

    "revision": """
        DROP TABLE revision
    """,

    "refaccion": """
        DROP TABLE refaccion
    """,

    "servicio": """
        DROP TABLE servicio
    """,

    "coche": """
        DROP TABLE coche
    """,

    "proveedor": """
        DROP TABLE proveedor
    """,

    "cliente": """
        DROP TABLE cliente
    """,

}

# Datos de prueba originales: no se insertan automáticamente.
# Para usarlos, ejecutar cada sentencia una sola vez y en este orden.
datos_prueba = {
    "cliente": """
        INSERT INTO cliente (nif,nombre_cliente,direccion,ciudad,telefono,correo) VALUES
        ('ABC123456','Ana Lopez Ramirez','Av. Vallarta 120','Guadalajara','3312345678','ana.lopez@example.com'),
        ('DEF234567','Carlos Martinez Ruiz','Calle Morelos 45','Zapopan','3323456789','carlos.martinez@example.com'),
        ('GHI345678','Sofia Hernandez Cruz','Av. Patria 890','Tlaquepaque','3334567890','sofia.hernandez@example.com'),
        ('JKL456789','Miguel Torres Diaz','Calle Juarez 16','Guadalajara','3345678901','miguel.torres@example.com'),
        ('MNO567890','Valeria Garcia Soto','Av. Mexico 300','Zapopan','3356789012','valeria.garcia@example.com')
    """,

    "proveedor": """
        INSERT INTO proveedor (nombre_proveedor,direccion,ciudad,telefono,correo) VALUES
        ('Refacciones del Centro','Calz. Independencia 100','Guadalajara','3611111111','ventas@refacentro.example'),
        ('Autopartes Jalisco','Av. Lopez Mateos 200','Zapopan','3622222222','contacto@autopartesjalisco.example'),
        ('Suministros Motor','Calle Industria 30','Tlaquepaque','3633333333','pedidos@suministrosmotor.example')
    """,

    "coche": """
        INSERT INTO coche (matricula,marca,modelo,color,anio,precio_venta,codigo_cliente,disponible) VALUES
        ('JAL1234','Nissan','Versa','Gris',2021,245000,1,FALSE),
        ('JAL2345','Toyota','Corolla','Blanco',2022,315000,2,FALSE),
        ('JAL3456','Mazda','Mazda 3','Rojo',2020,289000,3,FALSE),
        ('JAL4567','Volkswagen','Jetta','Azul',2023,365000,NULL,TRUE),
        ('JAL5678','Kia','Rio','Negro',2019,198000,4,FALSE),
        ('JAL6789','Honda','Civic','Plata',2024,410000,NULL,TRUE)
    """,

    "servicio": """
        INSERT INTO servicio (nombre_servicio,descripcion,costo,duracion_minutos) VALUES
        ('Cambio de aceite','Cambio de aceite y revision basica',850,45),
        ('Cambio de filtro','Sustitucion del filtro de aceite',320,20),
        ('Revision de frenos','Inspeccion del sistema de frenado',600,40),
        ('Afinacion general','Servicio preventivo general',1450,90),
        ('Diagnostico electronico','Escaneo de sistemas electronicos',500,30)
    """,

    "refaccion": """
        INSERT INTO refaccion (codigo_proveedor,nombre_refaccion,descripcion,precio,existencia) VALUES
        (1,'Filtro de aceite universal','Filtro compatible con varios modelos',180,25),
        (1,'Aceite sintetico 5W-30','Envase de un litro',140,80),
        (2,'Pastillas de freno delanteras','Juego de pastillas delanteras',950,12),
        (2,'Bujias de encendido','Juego de cuatro bujias',420,18),
        (3,'Filtro de aire','Filtro de aire para motor',260,20),
        (3,'Limpiador de inyectores','Aditivo para sistema de inyeccion',160,30)
    """,

    "revision": """
        INSERT INTO revision (fecha_revision,cambio_filtro,cambio_aceite,cambio_frenos,otros,matricula,kilometraje) VALUES
        ('2026-01-15','S','S','N','Revision preventiva','JAL1234',35000),
        ('2026-02-10','N','S','S','Inspeccion de frenos','JAL2345',28000),
        ('2026-03-05','S','S','S','Servicio completo','JAL3456',52000),
        ('2026-04-20','N','N','N','Revision general sin cambios','JAL5678',61000),
        ('2026-05-11','S','N','N','Cambio de filtro','JAL1234',39000)
    """,

    "orden_servicio": """
        INSERT INTO orden_servicio (codigo_cliente,matricula,fecha_orden,estado,observaciones) VALUES
        (1,'JAL1234','2026-06-02','Terminada','Servicio preventivo'),
        (2,'JAL2345','2026-06-10','En proceso','Revisar vibracion al frenar'),
        (3,'JAL3456','2026-07-01','Pendiente','Solicita afinacion'),
        (4,'JAL5678','2026-07-15','Terminada','Diagnostico general'),
        (1,'JAL1234','2026-08-04','Pendiente','Mantenimiento programado')
    """,

    "detalle_orden_servicio": """
        INSERT INTO detalle_orden_servicio (codigo_orden,codigo_servicio,codigo_refaccion,cantidad,precio_unitario) VALUES
        (1,1,NULL,1,850),
        (1,NULL,2,4,140),
        (2,3,NULL,1,600),
        (2,NULL,3,1,950),
        (3,4,NULL,1,1450),
        (4,5,NULL,1,500),
        (4,NULL,4,1,420),
        (5,2,NULL,1,320)
    """,

}

# Consultas originales para las evidencias. No se ejecutan automáticamente.
consultas_evidencia = {
    "consulta_1": """
        SELECT table_name AS tabla FROM information_schema.tables
        WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name
    """,

    "consulta_2": """
        SELECT table_name AS tabla, column_name AS columna, data_type AS tipo_dato,
               is_nullable AS permite_null, column_default AS valor_default
        FROM information_schema.columns WHERE table_schema='public'
        ORDER BY table_name, ordinal_position
    """,

    "consulta_3": """
        SELECT table_name AS tabla, constraint_name AS restriccion, constraint_type AS tipo
        FROM information_schema.table_constraints WHERE constraint_schema='public'
        ORDER BY table_name, constraint_type, constraint_name
    """,

    "consulta_4": """
        SELECT tablename AS tabla, indexname AS indice, indexdef AS definicion
        FROM pg_indexes WHERE schemaname='public' ORDER BY tablename,indexname
    """,

    "consulta_5": """
        SELECT 'cliente' AS tabla, COUNT(*) AS registros FROM cliente
        UNION ALL SELECT 'coche',COUNT(*) FROM coche
        UNION ALL SELECT 'revision',COUNT(*) FROM revision
        UNION ALL SELECT 'proveedor',COUNT(*) FROM proveedor
        UNION ALL SELECT 'servicio',COUNT(*) FROM servicio
        UNION ALL SELECT 'refaccion',COUNT(*) FROM refaccion
        UNION ALL SELECT 'orden_servicio',COUNT(*) FROM orden_servicio
        UNION ALL SELECT 'detalle_orden_servicio',COUNT(*) FROM detalle_orden_servicio
        ORDER BY tabla
    """,

    "consulta_6": """
        SELECT c.matricula,c.marca,c.modelo,cl.nombre_cliente
        FROM coche c LEFT JOIN cliente cl ON cl.codigo_cliente=c.codigo_cliente
        ORDER BY c.matricula
    """,

    "consulta_7": """
        SELECT o.codigo_orden,o.fecha_orden,o.estado,cl.nombre_cliente,c.matricula,c.marca,c.modelo
        FROM orden_servicio o JOIN cliente cl ON cl.codigo_cliente=o.codigo_cliente
        JOIN coche c ON c.matricula=o.matricula ORDER BY o.codigo_orden
    """,

}
