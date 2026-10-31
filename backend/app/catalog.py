"""65 ejercicios SQL predefinidos y parametrizados para las seis tablas AutoGest."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Exercise:
    code: str
    group: str
    title: str
    description: str
    sql: str
    params: list[dict] = field(default_factory=list)

EXERCISES: dict[str, Exercise] = {}
GROUPS = [
    {'id':'simples','title':'Consultas simples','target':25},
    {'id':'joins','title':'Operaciones JOIN','target':15},
    {'id':'agregadas','title':'Funciones agregadas','target':15},
    {'id':'vistas','title':'Vistas SQL','target':5},
    {'id':'triggers','title':'Funciones y disparadores','target':5},
]

def P(name,label,kind,default):
    return {'name':name,'label':label,'kind':kind,'default':default}

def add(code,group,title,description,sql,params=None):
    if code in EXERCISES: raise ValueError('Ejercicio duplicado: '+code)
    EXERCISES[code]=Exercise(code,group,title,description,sql.strip(),params or [])

add('S01','simples','Inventario completo','Vehículos ordenados por marca y modelo.', '''
SELECT id_coche, marca, modelo, anio, color, precio_referencia
FROM coche ORDER BY marca, modelo LIMIT 100''')
add('S02','simples','Precio mínimo','Filtra vehículos a partir de un precio de referencia.', '''
SELECT marca, modelo, anio, precio_referencia FROM coche
WHERE precio_referencia >= :minimo ORDER BY precio_referencia DESC''',[P('minimo','Desde (MXN)','float',350000)])
add('S03','simples','Precio máximo','Encuentra coches dentro de un presupuesto.', '''
SELECT marca, modelo, anio, precio_referencia FROM coche
WHERE precio_referencia <= :maximo ORDER BY precio_referencia''',[P('maximo','Hasta (MXN)','float',300000)])
add('S04','simples','Buscar por marca','Comparación de marca sin distinción de mayúsculas.', '''
SELECT id_coche, marca, modelo, anio FROM coche
WHERE marca ILIKE :marca ORDER BY anio DESC''',[P('marca','Marca','string','Toyota')])
add('S05','simples','Buscar modelo','Búsqueda parcial con ILIKE.', '''
SELECT id_coche, marca, modelo, precio_referencia FROM coche
WHERE modelo ILIKE '%' || :texto || '%' ORDER BY modelo''',[P('texto','Contiene','string','CX')])
add('S06','simples','Año de fabricación','Lista vehículos de un año específico.', '''
SELECT marca, modelo, anio, color FROM coche
WHERE anio=:anio ORDER BY marca''',[P('anio','Año','int',2023)])
add('S07','simples','Vehículos recientes','Filtra vehículos fabricados desde un año.', '''
SELECT marca, modelo, anio FROM coche WHERE anio >= :anio ORDER BY anio DESC''',[P('anio','Desde el año','int',2022)])
add('S08','simples','Coches por color','Filtra colores registrados.', '''
SELECT marca, modelo, color, matricula FROM coche
WHERE color ILIKE :color ORDER BY marca''',[P('color','Color','string','Gris')])
add('S09','simples','Directorio de clientes','Listado general con datos ficticios.', '''
SELECT id_cliente, nombre, ciudad, activo FROM cliente ORDER BY nombre''')
add('S10','simples','Clientes activos','Filtra clientes activos.', '''
SELECT nombre, telefono, ciudad FROM cliente WHERE activo IS TRUE ORDER BY nombre''')
add('S11','simples','Clientes por ciudad','Selecciona clientes residentes en una ciudad.', '''
SELECT id_cliente, nombre, ciudad FROM cliente
WHERE ciudad ILIKE :ciudad ORDER BY nombre''',[P('ciudad','Ciudad','string','Zapopan')])
add('S12','simples','Proveedores activos','Directorio de proveedores habilitados.', '''
SELECT id_proveedor, nombre, ciudad FROM proveedor WHERE activo IS TRUE ORDER BY nombre''')
add('S13','simples','Personal interno','Proyección de nombre y rol del personal ficticio.', '''
SELECT id_usuario, nombre, rol, activo FROM usuario_interno ORDER BY rol, nombre''')
add('S14','simples','Personal mecánico','Filtrado por rol.', '''
SELECT id_usuario, nombre, activo FROM usuario_interno WHERE rol='mecanico' ORDER BY nombre''')
add('S15','simples','Ventas vigentes','Ventas registradas y no canceladas.', '''
SELECT id_venta, id_coche, fecha_venta, importe FROM venta
WHERE estado='registrada' ORDER BY fecha_venta DESC''')
add('S16','simples','Ventas canceladas','Historial de cancelaciones con motivo.', '''
SELECT id_venta, fecha_venta, importe, motivo_cancelacion FROM venta
WHERE estado='cancelada' ORDER BY fecha_venta DESC''')
add('S17','simples','Ventas desde una fecha','Filtro cronológico de ventas.', '''
SELECT id_venta, fecha_venta, importe, estado FROM venta
WHERE fecha_venta >= CAST(:fecha AS DATE) ORDER BY fecha_venta''',[P('fecha','Desde','date','2026-04-01')])
add('S18','simples','Ventas por importe','Filtra operaciones por importe mínimo.', '''
SELECT id_venta, importe, fecha_venta, estado FROM venta
WHERE importe >= :minimo ORDER BY importe DESC''',[P('minimo','Importe mínimo','float',300000)])
add('S19','simples','Revisiones recientes','Consulta cronológica del mantenimiento.', '''
SELECT id_revision, id_coche, fecha_revision, kilometraje FROM revision
ORDER BY fecha_revision DESC LIMIT 20''')
add('S20','simples','Revisiones con aceite','Revisiones que incluyen cambio de aceite.', '''
SELECT id_revision, id_coche, fecha_revision, cambio_aceite FROM revision
WHERE cambio_aceite IS TRUE ORDER BY fecha_revision DESC''')
add('S21','simples','Revisiones con frenos','Revisiones que incluyen cambio de frenos.', '''
SELECT id_revision, id_coche, kilometraje, cambio_frenos FROM revision
WHERE cambio_frenos IS TRUE ORDER BY kilometraje DESC''')
add('S22','simples','Kilometraje superior','Vehículos con revisiones por encima del umbral.', '''
SELECT id_revision, id_coche, kilometraje FROM revision
WHERE kilometraje > :km ORDER BY kilometraje DESC''',[P('km','Kilómetros mínimos','int',20000)])
add('S23','simples','Placas registradas','Vehículos con matrícula asignada.', '''
SELECT id_coche, marca, modelo, matricula FROM coche
WHERE matricula IS NOT NULL ORDER BY matricula''')
add('S24','simples','Rango de precios','Ejemplo de BETWEEN parametrizado.', '''
SELECT marca, modelo, precio_referencia FROM coche
WHERE precio_referencia BETWEEN :minimo AND :maximo
ORDER BY precio_referencia''',[P('minimo','Desde (MXN)','float',250000),P('maximo','Hasta (MXN)','float',400000)])
add('S25','simples','Orden del inventario','Clasificación descendente con límite.', '''
SELECT id_coche, marca, modelo, precio_referencia FROM coche
ORDER BY precio_referencia DESC, marca LIMIT 10''')

add('J01','joins','Coche y proveedor','INNER JOIN del inventario con su proveedor.', '''
SELECT c.marca, c.modelo, c.anio, p.nombre AS proveedor
FROM coche c JOIN proveedor p ON p.id_proveedor=c.id_proveedor
ORDER BY p.nombre,c.marca''')
add('J02','joins','Venta y cliente','Identifica al comprador de cada operación.', '''
SELECT v.id_venta, cl.nombre AS cliente, v.importe, v.estado
FROM venta v JOIN cliente cl ON cl.id_cliente=v.id_cliente ORDER BY v.id_venta''')
add('J03','joins','Venta y vehículo','Relaciona cada venta con el coche.', '''
SELECT v.id_venta, c.marca, c.modelo, c.anio, v.importe
FROM venta v JOIN coche c ON c.id_coche=v.id_coche ORDER BY v.id_venta''')
add('J04','joins','Venta y registrador','Identifica al usuario que registró cada venta.', '''
SELECT v.id_venta, u.nombre AS registrado_por, u.rol, v.fecha_venta
FROM venta v JOIN usuario_interno u ON u.id_usuario=v.registrado_por
ORDER BY v.fecha_venta DESC''')
add('J05','joins','Revisión y mecánico','Muestra el responsable de una revisión.', '''
SELECT r.id_revision, u.nombre AS mecanico, r.fecha_revision, r.kilometraje
FROM revision r JOIN usuario_interno u ON u.id_usuario=r.realizado_por
ORDER BY r.fecha_revision DESC''')
add('J06','joins','Revisión y coche','Historial técnico con descripción del vehículo.', '''
SELECT r.id_revision, c.marca, c.modelo, r.fecha_revision, r.kilometraje
FROM revision r JOIN coche c ON c.id_coche=r.id_coche ORDER BY r.id_revision''')
add('J07','joins','Factura administrativa','JOIN de venta, cliente y vehículo.', '''
SELECT v.id_venta, cl.nombre AS cliente, c.marca, c.modelo, v.importe, v.estado
FROM venta v JOIN cliente cl ON cl.id_cliente=v.id_cliente
JOIN coche c ON c.id_coche=v.id_coche ORDER BY v.id_venta''')
add('J08','joins','Quién canceló','LEFT JOIN con usuario cancelador; conserva ventas vigentes.', '''
SELECT v.id_venta, v.estado, u.nombre AS cancelado_por, v.motivo_cancelacion
FROM venta v LEFT JOIN usuario_interno u ON u.id_usuario=v.cancelado_por
ORDER BY v.id_venta''')
add('J09','joins','Última revisión por coche','LEFT JOIN LATERAL para la revisión más reciente.', '''
SELECT c.id_coche, c.marca, c.modelo, r.fecha_revision, r.kilometraje
FROM coche c LEFT JOIN LATERAL (
  SELECT fecha_revision,kilometraje FROM revision
  WHERE id_coche=c.id_coche ORDER BY fecha_revision DESC, id_revision DESC LIMIT 1
) r ON TRUE ORDER BY c.id_coche''')
add('J10','joins','Inventario por proveedor','LEFT JOIN conserva proveedores sin coches.', '''
SELECT p.nombre AS proveedor, c.marca, c.modelo, c.anio
FROM proveedor p LEFT JOIN coche c ON c.id_proveedor=p.id_proveedor
ORDER BY p.nombre,c.marca''')
add('J11','joins','Clientes y compras','LEFT JOIN conserva clientes sin ventas.', '''
SELECT cl.nombre AS cliente, v.id_venta, v.importe, v.estado
FROM cliente cl LEFT JOIN venta v ON v.id_cliente=cl.id_cliente
ORDER BY cl.nombre, v.id_venta''')
add('J12','joins','Autos sin ventas vigentes','LEFT JOIN más filtro NULL y condición en ON.', '''
SELECT c.id_coche, c.marca, c.modelo, c.precio_referencia
FROM coche c LEFT JOIN venta v ON v.id_coche=c.id_coche AND v.estado='registrada'
WHERE v.id_venta IS NULL ORDER BY c.id_coche''')
add('J13','joins','Personal y revisiones','LEFT JOIN conserva usuarios sin revisiones.', '''
SELECT u.nombre, u.rol, r.id_revision, r.fecha_revision
FROM usuario_interno u LEFT JOIN revision r ON r.realizado_por=u.id_usuario
ORDER BY u.nombre,r.fecha_revision''')
add('J14','joins','Personal y ventas','LEFT JOIN conserva usuarios sin ventas.', '''
SELECT u.nombre, u.rol, v.id_venta, v.importe
FROM usuario_interno u LEFT JOIN venta v ON v.registrado_por=u.id_usuario
ORDER BY u.nombre,v.id_venta''')
add('J15','joins','Ciclo comercial completo','JOIN múltiple coche, proveedor, venta y cliente.', '''
SELECT c.id_coche,c.marca,c.modelo,p.nombre AS proveedor,
       v.id_venta,v.estado,cl.nombre AS cliente
FROM coche c JOIN proveedor p ON p.id_proveedor=c.id_proveedor
LEFT JOIN venta v ON v.id_coche=c.id_coche
LEFT JOIN cliente cl ON cl.id_cliente=v.id_cliente ORDER BY c.id_coche''')

add('A01','agregadas','Número de vehículos','COUNT del inventario total.', '''SELECT count(*) AS total_coches FROM coche''')
add('A02','agregadas','Precios del inventario','MIN, MAX y AVG del precio de referencia.', '''
SELECT min(precio_referencia) AS minimo, max(precio_referencia) AS maximo,
round(avg(precio_referencia),2) AS promedio FROM coche''')
add('A03','agregadas','Coches por marca','GROUP BY y COUNT por fabricante.', '''
SELECT marca,count(*) AS unidades FROM coche GROUP BY marca ORDER BY unidades DESC,marca''')
add('A04','agregadas','Monto de ventas vigentes','SUM con filtro de estado registrada.', '''
SELECT coalesce(sum(importe),0) AS monto_vigente FROM venta WHERE estado='registrada' ''')
add('A05','agregadas','Ventas por mes','Agrupación temporal de operaciones.', '''
SELECT date_trunc('month',fecha_venta)::date AS mes, count(*) AS operaciones,
 coalesce(sum(importe),0) AS monto_total FROM venta GROUP BY 1 ORDER BY 1''')
add('A06','agregadas','Ventas por estado','Agrupación en registradas y canceladas.', '''
SELECT estado,count(*) AS operaciones, sum(importe) AS monto FROM venta GROUP BY estado ORDER BY estado''')
add('A07','agregadas','Clientes por ciudad','Distribución de clientes.', '''
SELECT ciudad,count(*) AS clientes FROM cliente GROUP BY ciudad ORDER BY clientes DESC''')
add('A08','agregadas','Volumen por proveedor','Recuento de vehículos por proveedor.', '''
SELECT p.nombre,count(c.id_coche) AS coches FROM proveedor p
LEFT JOIN coche c ON c.id_proveedor=p.id_proveedor
GROUP BY p.id_proveedor,p.nombre ORDER BY coches DESC''')
add('A09','agregadas','Precio promedio por marca','AVG redondeado por grupo.', '''
SELECT marca, round(avg(precio_referencia),2) AS promedio_mxn
FROM coche GROUP BY marca ORDER BY promedio_mxn DESC''')
add('A10','agregadas','Revisiones por mecánico','COUNT de trabajos realizados.', '''
SELECT u.nombre,count(r.id_revision) AS revisiones FROM usuario_interno u
LEFT JOIN revision r ON r.realizado_por=u.id_usuario
WHERE u.rol='mecanico' GROUP BY u.id_usuario,u.nombre ORDER BY revisiones DESC''')
add('A11','agregadas','Tipos de intervención','COUNT FILTER para cada servicio realizado.', '''
SELECT count(*) AS total_revisiones,
count(*) FILTER (WHERE cambio_aceite) AS cambios_aceite,
count(*) FILTER (WHERE cambio_filtro) AS cambios_filtro,
count(*) FILTER (WHERE cambio_frenos) AS cambios_frenos FROM revision''')
add('A12','agregadas','Inventario por año','GROUP BY del año modelo.', '''
SELECT anio,count(*) AS coches FROM coche GROUP BY anio ORDER BY anio DESC''')
add('A13','agregadas','Kilometraje medio por marca','JOIN y AVG.', '''
SELECT c.marca,round(avg(r.kilometraje),0) AS km_promedio,
 count(r.id_revision) AS revisiones FROM coche c JOIN revision r ON r.id_coche=c.id_coche
GROUP BY c.marca ORDER BY km_promedio DESC''')
add('A14','agregadas','Clientes con varias operaciones','HAVING para filtrar clientes por cantidad.', '''
SELECT cl.nombre,count(v.id_venta) AS operaciones FROM cliente cl
JOIN venta v ON v.id_cliente=cl.id_cliente GROUP BY cl.id_cliente,cl.nombre
HAVING count(v.id_venta)>=:minimo ORDER BY operaciones DESC''',[P('minimo','Operaciones mínimas','int',1)])
add('A15','agregadas','Operaciones por registrador','Agrupación de ventas por usuario.', '''
SELECT u.nombre,count(v.id_venta) AS ventas,
coalesce(sum(v.importe) FILTER (WHERE v.estado='registrada'),0) AS monto_vigente
FROM usuario_interno u LEFT JOIN venta v ON v.registrado_por=u.id_usuario
GROUP BY u.id_usuario,u.nombre ORDER BY ventas DESC''')

add('V01','vistas','Vehículos y proveedores','Vista con el inventario vinculado al proveedor.', '''
SELECT * FROM v_u5_autos_proveedor ORDER BY marca,modelo''')
add('V02','vistas','Historial comercial','Vista de ventas con cliente y coche.', '''
SELECT * FROM v_u5_ventas_clientes ORDER BY fecha_venta DESC''')
add('V03','vistas','Historial mecánico','Vista de revisiones y responsables.', '''
SELECT * FROM v_u5_historial_revisiones ORDER BY fecha_revision DESC''')
add('V04','vistas','Disponibilidad','Vista que distingue vendidos y disponibles.', '''
SELECT * FROM v_u5_disponibilidad ORDER BY situacion,marca''')
add('V05','vistas','Ingresos mensuales','Vista agregada del historial de ventas.', '''
SELECT * FROM v_u5_ventas_mensuales ORDER BY mes''')

for code,title,desc in [
('T01','Normalizar matrículas','BEFORE INSERT/UPDATE convierte serie y matrícula a mayúsculas.'),
('T02','Cliente activo','Bloquea ventas registradas a clientes inactivos.'),
('T03','Validar kilometraje','Impide ingresar kilometrajes inferiores al historial.'),
('T04','Revisión antes de vender','Bloquea una venta vigente de un vehículo no revisado.'),
('T05','Proteger venta histórica','Bloquea ediciones de importes y datos históricos y reactivaciones.'),
]:
    add(code,'triggers',title,desc,'Código PL/pgSQL disponible desde el catálogo. La prueba se revierte.')

def list_catalog():
    return {'groups':GROUPS,'exercises':[
        {'code':ex.code,'group':ex.group,'title':ex.title,
         'description':ex.description,'sql':ex.sql,'params':ex.params}
        for ex in EXERCISES.values()], 'total':len(EXERCISES)}
