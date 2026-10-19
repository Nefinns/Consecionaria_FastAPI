CREATE TABLE cliente (
 codigo_cliente INT NOT NULL AUTO_INCREMENT, nif CHAR(9) NOT NULL, nombre_cliente VARCHAR(80) NOT NULL,
 direccion VARCHAR(100) NOT NULL, ciudad VARCHAR(40) NOT NULL DEFAULT 'Guadalajara', telefono CHAR(10) NOT NULL,
 correo VARCHAR(100) NOT NULL, fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, activo BOOLEAN NOT NULL DEFAULT TRUE,
 CONSTRAINT pk_cliente PRIMARY KEY (codigo_cliente), CONSTRAINT uq_cliente_nif UNIQUE (nif),
 CONSTRAINT uq_cliente_correo UNIQUE (correo), CONSTRAINT chk_cliente_nif CHECK (REGEXP_LIKE(nif,'^[A-Z0-9]{9}$','c'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE proveedor (
 codigo_proveedor INT NOT NULL AUTO_INCREMENT, nombre_proveedor VARCHAR(80) NOT NULL, direccion VARCHAR(100) NOT NULL,
 ciudad VARCHAR(40) NOT NULL DEFAULT 'Guadalajara', telefono CHAR(10) NOT NULL, correo VARCHAR(100) NOT NULL,
 activo BOOLEAN NOT NULL DEFAULT TRUE, CONSTRAINT pk_proveedor PRIMARY KEY (codigo_proveedor),
 CONSTRAINT uq_proveedor_correo UNIQUE (correo), CONSTRAINT chk_proveedor_correo CHECK (LOCATE('@', correo)>1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE coche (
 matricula CHAR(7) NOT NULL, marca VARCHAR(30) NOT NULL, modelo VARCHAR(30) NOT NULL,
 color VARCHAR(20) NOT NULL DEFAULT 'Blanco', anio SMALLINT NOT NULL, precio_venta DECIMAL(10,2) NOT NULL,
 codigo_cliente INT NULL, fecha_alta DATE NOT NULL DEFAULT (CURRENT_DATE), disponible BOOLEAN NOT NULL DEFAULT TRUE,
 CONSTRAINT pk_coche PRIMARY KEY (matricula),
 CONSTRAINT fk_coche_cliente FOREIGN KEY (codigo_cliente) REFERENCES cliente(codigo_cliente) ON UPDATE CASCADE ON DELETE SET NULL,
 CONSTRAINT chk_coche_anio CHECK (anio BETWEEN 1980 AND 2035),
 CONSTRAINT chk_coche_precio CHECK (precio_venta > 0),
 CONSTRAINT chk_coche_matricula CHECK (REGEXP_LIKE(matricula,'^[A-Z0-9]{7}$','c')),
 INDEX idx_coche_codigo_cliente (codigo_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE servicio (
 codigo_servicio INT NOT NULL AUTO_INCREMENT, nombre_servicio VARCHAR(80) NOT NULL, descripcion VARCHAR(200),
 costo DECIMAL(10,2) NOT NULL DEFAULT 0, duracion_minutos INT NOT NULL DEFAULT 30,
 activo BOOLEAN NOT NULL DEFAULT TRUE, CONSTRAINT pk_servicio PRIMARY KEY (codigo_servicio),
 CONSTRAINT uq_servicio_nombre UNIQUE (nombre_servicio), CONSTRAINT ck_servicio_costo CHECK (costo>=0),
 CONSTRAINT ck_servicio_duracion CHECK (duracion_minutos>0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE refaccion (
 codigo_refaccion INT NOT NULL AUTO_INCREMENT, codigo_proveedor INT NOT NULL,
 nombre_refaccion VARCHAR(80) NOT NULL, descripcion VARCHAR(200), precio DECIMAL(10,2) NOT NULL,
 existencia INT NOT NULL DEFAULT 0, CONSTRAINT pk_refaccion PRIMARY KEY (codigo_refaccion),
 CONSTRAINT fk_refaccion_proveedor FOREIGN KEY (codigo_proveedor) REFERENCES proveedor(codigo_proveedor) ON UPDATE CASCADE ON DELETE RESTRICT,
 CONSTRAINT uq_refaccion_proveedor_nombre UNIQUE (codigo_proveedor, nombre_refaccion),
 CONSTRAINT chk_refaccion_precio CHECK (precio>=0), CONSTRAINT chk_refaccion_existencia CHECK (existencia>=0),
 INDEX idx_refaccion_codigo_proveedor (codigo_proveedor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE revision (
 codigo_revision INT NOT NULL AUTO_INCREMENT, fecha_revision DATE NOT NULL DEFAULT (CURRENT_DATE),
 cambio_filtro CHAR(1) NOT NULL DEFAULT 'N', cambio_aceite CHAR(1) NOT NULL DEFAULT 'N',
 cambio_frenos CHAR(1) NOT NULL DEFAULT 'N', otros VARCHAR(120), matricula CHAR(7) NOT NULL,
 kilometraje INT NOT NULL DEFAULT 0, CONSTRAINT pk_revision PRIMARY KEY (codigo_revision),
 CONSTRAINT fk_revision_coche FOREIGN KEY (matricula) REFERENCES coche(matricula) ON UPDATE CASCADE ON DELETE RESTRICT,
 CONSTRAINT chk_cambio_filtro CHECK (cambio_filtro IN ('S','N')),
 CONSTRAINT chk_cambio_aceite CHECK (cambio_aceite IN ('S','N')),
 CONSTRAINT chk_cambio_frenos CHECK (cambio_frenos IN ('S','N')),
 CONSTRAINT chk_revision_kilometraje CHECK (kilometraje>=0),
 INDEX idx_revision_matricula (matricula), INDEX idx_revision_fecha (fecha_revision)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE orden_servicio (
 codigo_orden INT NOT NULL AUTO_INCREMENT, codigo_cliente INT NOT NULL, matricula CHAR(7) NOT NULL,
 fecha_orden DATE NOT NULL DEFAULT (CURRENT_DATE), estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
 observaciones VARCHAR(250), CONSTRAINT pk_orden_servicio PRIMARY KEY (codigo_orden),
 CONSTRAINT fk_orden_cliente FOREIGN KEY (codigo_cliente) REFERENCES cliente(codigo_cliente) ON UPDATE CASCADE ON DELETE RESTRICT,
 CONSTRAINT fk_orden_coche FOREIGN KEY (matricula) REFERENCES coche(matricula) ON UPDATE CASCADE ON DELETE RESTRICT,
 CONSTRAINT chk_orden_estado CHECK (estado IN ('Pendiente','En proceso','Terminada','Cancelada')),
 INDEX idx_orden_cliente (codigo_cliente), INDEX idx_orden_matricula (matricula), INDEX idx_orden_fecha (fecha_orden)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE detalle_orden_servicio (
 codigo_detalle INT NOT NULL AUTO_INCREMENT, codigo_orden INT NOT NULL, codigo_servicio INT NULL,
 codigo_refaccion INT NULL, cantidad INT NOT NULL DEFAULT 1, precio_unitario DECIMAL(10,2) NOT NULL,
 CONSTRAINT pk_detalle_orden PRIMARY KEY (codigo_detalle),
 CONSTRAINT fk_detalle_orden FOREIGN KEY (codigo_orden) REFERENCES orden_servicio(codigo_orden) ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT fk_detalle_servicio FOREIGN KEY (codigo_servicio) REFERENCES servicio(codigo_servicio),
 CONSTRAINT fk_detalle_refaccion FOREIGN KEY (codigo_refaccion) REFERENCES refaccion(codigo_refaccion),
 CONSTRAINT chk_detalle_cantidad CHECK (cantidad>0), CONSTRAINT chk_detalle_precio CHECK (precio_unitario>=0),
 CONSTRAINT chk_detalle_un_tipo CHECK ((codigo_servicio IS NOT NULL AND codigo_refaccion IS NULL) OR (codigo_servicio IS NULL AND codigo_refaccion IS NOT NULL)),
 INDEX idx_detalle_codigo_orden (codigo_orden), INDEX idx_detalle_servicio (codigo_servicio), INDEX idx_detalle_refaccion (codigo_refaccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
