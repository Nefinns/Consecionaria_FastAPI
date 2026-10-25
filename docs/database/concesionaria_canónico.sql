-- Concesionaria | Esquema canonico v1.0 | PostgreSQL 15+
-- Una sucursal, proveedores de vehiculos, ventas administrativas y revisiones.
-- Ejecutar solo sobre una base de datos NUEVA y vacia.
-- No contiene DROP, datos ficticios, cuentas ni credenciales.
-- No sustituye una migracion del esquema academico anterior.

BEGIN;

CREATE TABLE cliente (
    id_cliente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL CHECK (btrim(nombre) <> ''),
    telefono VARCHAR(25) NOT NULL CHECK (btrim(telefono) <> ''),
    correo VARCHAR(254) CHECK (correo IS NULL OR btrim(correo) <> ''),
    direccion VARCHAR(200) CHECK (direccion IS NULL OR btrim(direccion) <> ''),
    ciudad VARCHAR(80) CHECK (ciudad IS NULL OR btrim(ciudad) <> ''),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE proveedor (
    id_proveedor INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL CHECK (btrim(nombre) <> ''),
    telefono VARCHAR(25) NOT NULL CHECK (btrim(telefono) <> ''),
    correo VARCHAR(254) CHECK (correo IS NULL OR btrim(correo) <> ''),
    direccion VARCHAR(200) CHECK (direccion IS NULL OR btrim(direccion) <> ''),
    ciudad VARCHAR(80) CHECK (ciudad IS NULL OR btrim(ciudad) <> ''),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE usuario_interno (
    id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identidad_externa VARCHAR(255) NOT NULL UNIQUE
        CHECK (btrim(identidad_externa) <> ''),
    nombre VARCHAR(120) NOT NULL CHECK (btrim(nombre) <> ''),
    rol VARCHAR(20) NOT NULL
        CHECK (rol IN ('administrador', 'gerente', 'mecanico')),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE coche (
    id_coche INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_proveedor INTEGER NOT NULL REFERENCES proveedor(id_proveedor)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    numero_serie VARCHAR(30) NOT NULL UNIQUE
        CHECK (numero_serie = upper(btrim(numero_serie)) AND numero_serie <> ''),
    matricula VARCHAR(15) UNIQUE
        CHECK (matricula IS NULL OR
               (matricula = upper(btrim(matricula)) AND matricula <> '')),
    marca VARCHAR(50) NOT NULL CHECK (btrim(marca) <> ''),
    modelo VARCHAR(60) NOT NULL CHECK (btrim(modelo) <> ''),
    anio SMALLINT NOT NULL CHECK (anio BETWEEN 1886 AND 9999),
    color VARCHAR(40) NOT NULL CHECK (btrim(color) <> ''),
    precio_referencia NUMERIC(12,2) NOT NULL CHECK (precio_referencia > 0)
);

CREATE TABLE venta (
    id_venta INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_coche INTEGER NOT NULL REFERENCES coche(id_coche)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    id_cliente INTEGER NOT NULL REFERENCES cliente(id_cliente)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    registrado_por INTEGER NOT NULL REFERENCES usuario_interno(id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    fecha_venta DATE NOT NULL,
    importe NUMERIC(12,2) NOT NULL CHECK (importe > 0),
    estado VARCHAR(10) NOT NULL DEFAULT 'registrada'
        CHECK (estado IN ('registrada', 'cancelada')),
    cancelado_por INTEGER REFERENCES usuario_interno(id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    fecha_cancelacion TIMESTAMPTZ,
    motivo_cancelacion VARCHAR(250),
    CONSTRAINT ck_venta_cancelacion_coherente CHECK (
        (estado = 'registrada' AND cancelado_por IS NULL
            AND fecha_cancelacion IS NULL AND motivo_cancelacion IS NULL)
        OR
        (estado = 'cancelada' AND cancelado_por IS NOT NULL
            AND fecha_cancelacion IS NOT NULL AND motivo_cancelacion IS NOT NULL
            AND btrim(motivo_cancelacion) <> '')
    ),
    CONSTRAINT ck_venta_cancelacion_fecha CHECK (
        fecha_cancelacion IS NULL OR
        (fecha_cancelacion AT TIME ZONE 'America/Mexico_City')::date >= fecha_venta
    )
);

CREATE TABLE revision (
    id_revision INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_coche INTEGER NOT NULL REFERENCES coche(id_coche)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    realizado_por INTEGER NOT NULL REFERENCES usuario_interno(id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    fecha_revision DATE NOT NULL,
    kilometraje INTEGER NOT NULL CHECK (kilometraje >= 0),
    cambio_filtro BOOLEAN NOT NULL,
    cambio_aceite BOOLEAN NOT NULL,
    cambio_frenos BOOLEAN NOT NULL,
    observaciones VARCHAR(500)
        CHECK (observaciones IS NULL OR btrim(observaciones) <> '')
);

-- Garantia atomica incluso ante dos solicitudes de venta concurrentes.
CREATE UNIQUE INDEX ux_venta_unica_vigente_por_coche
    ON venta(id_coche) WHERE estado = 'registrada';

-- Indices de busqueda y soporte a claves foraneas.
CREATE INDEX ix_coche_proveedor ON coche(id_proveedor);
CREATE INDEX ix_venta_coche ON venta(id_coche);
CREATE INDEX ix_venta_cliente ON venta(id_cliente);
CREATE INDEX ix_venta_registrado_por ON venta(registrado_por);
CREATE INDEX ix_venta_cancelado_por ON venta(cancelado_por)
    WHERE cancelado_por IS NOT NULL;
CREATE INDEX ix_venta_fecha ON venta(fecha_venta);
CREATE INDEX ix_revision_coche_fecha ON revision(id_coche, fecha_revision DESC);
CREATE INDEX ix_revision_realizado_por ON revision(realizado_por);

COMMENT ON TABLE usuario_interno IS
    'Autorizacion local: la autenticacion externa nunca concede acceso por si sola.';
COMMENT ON TABLE venta IS
    'Registro administrativo; no procesa pagos, reembolsos ni transferencias legales.';
COMMENT ON COLUMN coche.precio_referencia IS
    'Precio actual de referencia en MXN, independiente del importe historico de venta.';

COMMIT;

-- REGLAS QUE DEBE IMPLEMENTAR FASTAPI (NO garantizadas solo por este DDL):
-- 1. Validar token del proveedor, usuario_interno activo y rol en CADA endpoint.
-- 2. Usuario interno: alta y cambios de rol solo por administrador; no autoalta.
-- 3. Clientes/proveedores activos al crear ventas/coches respectivamente.
-- 4. Registrado_por y cancelado_por deben proceder de la identidad autenticada.
-- 5. Revisiones: el mecanico solo registra/edita las suyas; filtrar campos sensibles.
-- 6. Fecha de venta/revision <= fecha actual de America/Mexico_City.
-- 7. Anio modelo <= anio actual + 1; formato de correo validado por la API.
-- 8. Solo cancelar ventas registradas; nunca reactivar ni borrar ventas.
-- 9. Al corregir una venta, cancelar y crear la nueva dentro de una transaccion.
-- 10. No borrar historicos; desactivar cliente/proveedor/usuario relacionados.
-- 11. Restringir modificaciones de campos historicos de venta y las operaciones
--     de eliminacion conforme a las reglas de negocio, no solo a las FK.
-- 12. Ajustar CORS, permisos del usuario de BD y gestion de secretos.
