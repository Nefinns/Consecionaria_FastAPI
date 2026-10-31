"""Cinco vistas y cinco pares función/disparador PostgreSQL para AutoGest."""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

VIEWS = {
'v_u5_autos_proveedor': '''
SELECT c.id_coche, c.marca, c.modelo, c.anio, c.color, c.numero_serie,
       c.matricula, c.precio_referencia, p.nombre AS proveedor, p.ciudad AS ciudad_proveedor
FROM coche c JOIN proveedor p ON p.id_proveedor=c.id_proveedor''',
'v_u5_ventas_clientes': '''
SELECT v.id_venta, v.fecha_venta, v.estado, v.importe,
       cl.nombre AS cliente, c.marca, c.modelo, c.anio,
       u.nombre AS registrado_por
FROM venta v JOIN cliente cl ON cl.id_cliente=v.id_cliente
 JOIN coche c ON c.id_coche=v.id_coche
 JOIN usuario_interno u ON u.id_usuario=v.registrado_por''',
'v_u5_historial_revisiones': '''
SELECT r.id_revision, r.fecha_revision, r.kilometraje, r.cambio_aceite,
       r.cambio_filtro, r.cambio_frenos, c.marca, c.modelo, c.matricula,
       u.nombre AS mecanico
FROM revision r JOIN coche c ON c.id_coche=r.id_coche
 JOIN usuario_interno u ON u.id_usuario=r.realizado_por''',
'v_u5_disponibilidad': '''
SELECT c.id_coche, c.marca, c.modelo, c.anio, c.precio_referencia,
 CASE WHEN EXISTS (SELECT 1 FROM venta v WHERE v.id_coche=c.id_coche AND v.estado='registrada')
 THEN 'Vendido' ELSE 'Disponible' END AS situacion,
 (SELECT count(*) FROM revision r WHERE r.id_coche=c.id_coche) AS revisiones
FROM coche c''',
'v_u5_ventas_mensuales': '''
SELECT date_trunc('month', fecha_venta)::date AS mes,
 count(*) FILTER (WHERE estado='registrada') AS ventas_vigentes,
 count(*) FILTER (WHERE estado='cancelada') AS cancelaciones,
 coalesce(sum(importe) FILTER (WHERE estado='registrada'),0) AS ingresos_registrados
FROM venta GROUP BY 1''',
}

FUNCTIONS = {
'T01': '''CREATE OR REPLACE FUNCTION u5_fn_normalizar_auto() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.numero_serie := upper(btrim(NEW.numero_serie));
  IF NEW.matricula IS NOT NULL THEN NEW.matricula := upper(btrim(NEW.matricula)); END IF;
  RETURN NEW;
END;
$$''',
'T02': '''CREATE OR REPLACE FUNCTION u5_fn_cliente_activo_venta() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado='registrada' AND NOT EXISTS (
      SELECT 1 FROM cliente WHERE id_cliente=NEW.id_cliente AND activo=TRUE
  ) THEN
    RAISE EXCEPTION 'La venta requiere un cliente activo.';
  END IF;
  RETURN NEW;
END;
$$''',

'T03': '''CREATE OR REPLACE FUNCTION u5_fn_kilometraje_coherente() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE km_max INTEGER;
BEGIN
  SELECT max(kilometraje) INTO km_max
  FROM revision
  WHERE id_coche = NEW.id_coche
    AND id_revision IS DISTINCT FROM NEW.id_revision;

  IF km_max IS NOT NULL AND NEW.kilometraje < km_max THEN
    RAISE EXCEPTION USING MESSAGE =
      'El kilometraje no puede ser inferior a una revision registrada ('
      || km_max::text || ').';
  END IF;

  RETURN NEW;
END;
$$''',

'T04': '''CREATE OR REPLACE FUNCTION u5_fn_venta_requiere_revision() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado='registrada' AND NOT EXISTS (
       SELECT 1 FROM revision WHERE id_coche=NEW.id_coche
  ) THEN
    RAISE EXCEPTION 'El vehiculo requiere una revision antes de registrarse su venta.';
  END IF;
  RETURN NEW;
END;
$$''',
'T05': '''CREATE OR REPLACE FUNCTION u5_fn_venta_historica_inmutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.estado='cancelada' THEN
    RAISE EXCEPTION 'Las ventas canceladas son historicas e inmutables.';
  END IF;
  IF (NEW.id_coche, NEW.id_cliente, NEW.registrado_por, NEW.fecha_venta, NEW.importe)
      IS DISTINCT FROM
     (OLD.id_coche, OLD.id_cliente, OLD.registrado_por, OLD.fecha_venta, OLD.importe) THEN
    RAISE EXCEPTION 'No se permite modificar datos historicos de venta.';
  END IF;
  IF NEW.estado <> OLD.estado AND NEW.estado <> 'cancelada' THEN
    RAISE EXCEPTION 'Solo se permite cancelar una venta registrada.';
  END IF;
  RETURN NEW;
END;
$$''',
}

TRIGGERS = {
'T01': "CREATE TRIGGER u5_t01_normalizar_auto BEFORE INSERT OR UPDATE ON coche FOR EACH ROW EXECUTE FUNCTION u5_fn_normalizar_auto()",
'T02': "CREATE TRIGGER u5_t02_cliente_activo BEFORE INSERT OR UPDATE ON venta FOR EACH ROW EXECUTE FUNCTION u5_fn_cliente_activo_venta()",
'T03': "CREATE TRIGGER u5_t03_kilometraje BEFORE INSERT OR UPDATE ON revision FOR EACH ROW EXECUTE FUNCTION u5_fn_kilometraje_coherente()",
'T04': "CREATE TRIGGER u5_t04_revision_preventa BEFORE INSERT OR UPDATE ON venta FOR EACH ROW EXECUTE FUNCTION u5_fn_venta_requiere_revision()",
'T05': "CREATE TRIGGER u5_t05_venta_inmutable BEFORE UPDATE ON venta FOR EACH ROW EXECUTE FUNCTION u5_fn_venta_historica_inmutable()",
}

NAMES = {
'T01':'u5_t01_normalizar_auto', 'T02':'u5_t02_cliente_activo',
'T03':'u5_t03_kilometraje', 'T04':'u5_t04_revision_preventa',
'T05':'u5_t05_venta_inmutable',
}
TABLE_BY_TRIGGER = {'T01':'coche','T02':'venta','T03':'revision','T04':'venta','T05':'venta'}

def install_objects(conn):
    for name, statement in VIEWS.items():
        conn.exec_driver_sql(f'CREATE OR REPLACE VIEW {name} AS {statement}')
    for code, statement in FUNCTIONS.items():
        conn.exec_driver_sql(statement)
    for code, statement in TRIGGERS.items():
        conn.exec_driver_sql(f'DROP TRIGGER IF EXISTS {NAMES[code]} ON {TABLE_BY_TRIGGER[code]}')
        conn.exec_driver_sql(statement)

def trigger_source(code):
    return FUNCTIONS[code] + ';\n\n' + TRIGGERS[code] + ';'

def _expect_rejection(conn, sql, params):
    try:
        with conn.begin_nested():
            conn.execute(text(sql), params)
    except SQLAlchemyError as exc:
        safe_summary = str(getattr(exc, 'orig', exc)).splitlines()[0]
        return {'rechazado': True, 'detalle': safe_summary[:220]}
    return {'rechazado': False, 'detalle': 'La operación no se rechazó; verificar regla.'}

def demo_trigger(conn, code):
    """Demos con cambios revertidos por la transacción superior en main.py."""
    if code == 'T01':
        conn.execute(text("UPDATE coche SET matricula='demo-x123' WHERE id_coche=29"))
        value = conn.execute(text('SELECT matricula FROM coche WHERE id_coche=29')).scalar_one()
        return {'trigger':'Normalización', 'matricula_tras_actualizar':value,
                'funciono':value=='DEMO-X123'}
    if code == 'T02':
        status = _expect_rejection(conn, '''INSERT INTO venta
            (id_coche,id_cliente,registrado_por,fecha_venta,importe)
            VALUES (18,18,1,DATE '2026-07-01',200000)''', {})
        return {'trigger':'Cliente activo', **status}
    if code == 'T03':
        status = _expect_rejection(conn, '''INSERT INTO revision
            (id_coche,realizado_por,fecha_revision,kilometraje,cambio_filtro,cambio_aceite,cambio_frenos)
            VALUES (1,3,DATE '2026-09-15',0,FALSE,FALSE,FALSE)''', {})
        return {'trigger':'Kilometraje', **status}
    if code == 'T04':
        status = _expect_rejection(conn, '''INSERT INTO venta
            (id_coche,id_cliente,registrado_por,fecha_venta,importe)
            VALUES (29,1,1,DATE '2026-07-01',200000)''', {})
        return {'trigger':'Revisión previa', **status}
    if code == 'T05':
        status = _expect_rejection(conn, '''UPDATE venta SET importe=importe+1
            WHERE id_venta=1''', {})
        return {'trigger':'Histórico inmutable', **status}
    raise ValueError('No existe el disparador.')
