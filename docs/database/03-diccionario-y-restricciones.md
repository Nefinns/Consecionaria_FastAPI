# Diccionario y reglas de la propuesta de base de datos

Estado: diseño propuesto, sin ejecutar SQL ni modificar el repositorio del backend.
Destino previsto: PostgreSQL. Los diagramas describen el modelo; no crean restricciones.

## Alcance y decisiones

- Una sola sucursal. Administración interna, sin portal de clientes o proveedores.
- Proveedores de vehículos. Un coche tiene un proveedor de origen obligatorio.
- Se registran vehículos de la concesionaria y revisiones de esos mismos vehículos, antes o después de venderlos. No se incluye recepción de coches externos al inventario histórico.
- Una venta corresponde a un coche y un comprador. Solo una venta no cancelada por coche.
- Cancelar una venta significa corregir/anular un registro, no procesar devoluciones o reembolsos.
- No hay recompras, reventas del mismo coche, pagos, facturación, refacciones, órdenes de compra ni varias monedas. Todos los importes son MXN.
- El comprador se obtiene de la venta vigente. No representa un registro legal de propietarios posteriores.
- Cada usuario interno tiene un rol fijo del conjunto administrador, gerente o mecanico. La identidad externa pertenece a un solo proveedor/instancia de autenticación.
- Todas las tablas están conectadas por claves foráneas con significado operativo. Esto no obliga a que todo cliente o proveedor tenga operaciones desde su alta.

## Convenciones

PK = clave primaria; FK = clave foránea; UQ = unicidad.
Todos los campos son NOT NULL salvo los marcados como opcionales.
Todas las PK son INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY.
Las FK apuntan a las PK indicadas, con ON DELETE RESTRICT y ON UPDATE RESTRICT.
Los identificadores son inmutables.
Los textos obligatorios deben cumplir CHECK (btrim(campo) <> '').
Los textos opcionales se guardan como NULL cuando no hay información; si tienen valor, tampoco admiten solo espacios.
No se usan valores ficticios como SIN DATO o una cadena vacía.
El teléfono es texto, no un número para operaciones aritméticas.
El nombre se maneja como etiqueta completa, sin necesidad de consultar apellidos por separado.
La dirección representa calle, número y complemento; la ciudad se almacena por separado.
Correo y teléfono no son únicos: varias personas o empresas pueden compartirlos.

## CLIENTE

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_cliente | INTEGER | No | PK, identidad | Identificador del cliente. |
| nombre | VARCHAR(120) | No | No vacío | Nombre completo. |
| telefono | VARCHAR(25) | No | No vacío | Un teléfono principal de contacto. |
| correo | VARCHAR(254) | Sí | Sin default | Un correo principal; formato validado por la API. |
| direccion | VARCHAR(200) | Sí | Sin default | Calle, número y complemento. |
| ciudad | VARCHAR(80) | Sí | Sin default | Ciudad de contacto, sin default geográfico. |
| activo | BOOLEAN | No | DEFAULT TRUE | Permite usarlo en nuevas ventas; conserva el historial. |

## PROVEEDOR

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_proveedor | INTEGER | No | PK, identidad | Identificador del proveedor. |
| nombre | VARCHAR(120) | No | No vacío | Nombre o razón social del suministrador de vehículos. |
| telefono | VARCHAR(25) | No | No vacío | Un teléfono principal. |
| correo | VARCHAR(254) | Sí | Sin default | Un correo principal, validado por la API. |
| direccion | VARCHAR(200) | Sí | Sin default | Calle, número y complemento. |
| ciudad | VARCHAR(80) | Sí | Sin default | Ciudad de contacto. |
| activo | BOOLEAN | No | DEFAULT TRUE | Habilita su selección para nuevos vehículos. |

## USUARIO_INTERNO

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_usuario | INTEGER | No | PK, identidad | Identificador interno del empleado. |
| identidad_externa | VARCHAR(255) | No | UQ, no vacío | Identificador estable del proveedor de autenticación; no el correo. |
| nombre | VARCHAR(120) | No | No vacío | Nombre de trabajo administrado localmente. |
| rol | VARCHAR(20) | No | CHECK IN ('administrador','gerente','mecanico'); sin default | Un rol por usuario, asignado explícitamente. |
| activo | BOOLEAN | No | DEFAULT TRUE | La API rechaza acceso de usuarios inactivos. |

No almacena contraseñas ni tokens. Los usuarios se incorporan por un proceso administrativo; autenticarse con el proveedor externo no crea ni autoriza automáticamente un usuario interno.

## COCHE

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_coche | INTEGER | No | PK, identidad | Identificador estable del vehículo. |
| id_proveedor | INTEGER | No | FK → proveedor.id_proveedor | Proveedor de origen del vehículo. |
| numero_serie | VARCHAR(30) | No | UQ, no vacío, mayúsculas sin espacios exteriores | Identificación única de la unidad; no supone una validación legal de VIN. |
| matricula | VARCHAR(15) | Sí | UQ, mayúsculas sin espacios exteriores | Matrícula actual, si está disponible. UNIQUE permite varios NULL en PostgreSQL. |
| marca | VARCHAR(50) | No | No vacío | Marca comercial. |
| modelo | VARCHAR(60) | No | No vacío | Nombre comercial del modelo; no es un identificador de catálogo. |
| anio | SMALLINT | No | CHECK BETWEEN 1886 AND 9999 | Año modelo; la API impide valores superiores al año actual + 1. |
| color | VARCHAR(40) | No | No vacío | Descripción simple del color. |
| precio_referencia | NUMERIC(12,2) | No | CHECK > 0; sin default | Precio de referencia actual en MXN. No sustituye al importe vendido. |

No tiene id_cliente, disponible ni vendido. El comprador y la existencia de una venta vigente se consultan en VENTA. No se modela un inventario con múltiples estados de operación.

## VENTA

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_venta | INTEGER | No | PK, identidad | Identificador de la operación registrada. |
| id_coche | INTEGER | No | FK → coche.id_coche; unicidad parcial para estado registrada | Vehículo objeto de la venta. |
| id_cliente | INTEGER | No | FK → cliente.id_cliente | Comprador de esta operación histórica. |
| registrado_por | INTEGER | No | FK → usuario_interno.id_usuario | Empleado autenticado que registra la operación. |
| fecha_venta | DATE | No | Sin default | Fecha real de venta, que puede ser anterior a la captura. |
| importe | NUMERIC(12,2) | No | CHECK > 0; sin default | Importe final acordado en MXN. No implica cobro electrónico. |
| estado | VARCHAR(10) | No | DEFAULT 'registrada'; CHECK IN ('registrada','cancelada') | Vigencia del registro. |
| cancelado_por | INTEGER | Sí | FK → usuario_interno.id_usuario | Empleado que cancela; obligatorio si está cancelada. |
| fecha_cancelacion | TIMESTAMPTZ | Sí | Sin default | Instante de cancelación; obligatorio si está cancelada. |
| motivo_cancelacion | VARCHAR(250) | Sí | No vacío cuando tiene valor | Motivo obligatorio al cancelar. |

Restricción de fila: si estado = registrada, los tres campos de cancelación son NULL. Si estado = cancelada, los tres son NOT NULL y el motivo no está vacío.
Índice UNIQUE parcial: venta(id_coche) WHERE estado = 'registrada'.
Esto permite conservar cancelaciones sin admitir dos ventas vigentes del mismo coche, incluso ante solicitudes simultáneas.
Una venta cancelada no se reactiva. Una corrección se registra mediante cancelación y nueva venta en una transacción, cuando corresponda.
No se permite borrar ventas. Los campos comerciales de una venta registrada no se sobrescriben: la corrección conserva el registro anterior.

## REVISION

| Campo | Tipo PostgreSQL | Nulo | Restricción/default | Significado |
|---|---|---|---|---|
| id_revision | INTEGER | No | PK, identidad | Identificador de la revisión realizada. |
| id_coche | INTEGER | No | FK → coche.id_coche | Vehículo atendido. |
| realizado_por | INTEGER | No | FK → usuario_interno.id_usuario | Empleado responsable de realizar la revisión. |
| fecha_revision | DATE | No | Sin default | Día de realización; no es una cita futura. |
| kilometraje | INTEGER | No | CHECK >= 0; sin default | Lectura observada; cero solo cuando es real. |
| cambio_filtro | BOOLEAN | No | Sin default | Indica explícitamente si se cambió el filtro. |
| cambio_aceite | BOOLEAN | No | Sin default | Indica explícitamente si se cambió el aceite. |
| cambio_frenos | BOOLEAN | No | Sin default | Indica explícitamente si se cambiaron los frenos. |
| observaciones | VARCHAR(500) | Sí | No vacío cuando tiene valor | Comentario técnico, no una lista estructurada de refacciones o servicios. |

La revisión no requiere una venta previa: puede hacerse antes de vender el coche.
Los tres indicadores son propiedades distintas de la revisión, no grupos repetidos ni listas.
No hay estado de reparación porque únicamente se registran revisiones ya realizadas.

## Reglas entre registros y de acceso

Estas reglas requieren lógica transaccional de FastAPI o triggers, no simples CHECK que lean otras tablas:

1. Solo usuarios internos activos acceden a la API. Un token válido sin autorización local es insuficiente.
2. Administrador: gestiona usuarios/roles y todos los módulos.
3. Gerente: gestiona clientes, proveedores, coches, ventas y revisiones, pero no usuarios/roles.
4. Mecánico: consulta vehículos e historial técnico; registra revisiones propias y edita únicamente las propias. No consulta precios, ventas ni contactos comerciales; usar respuestas con campos limitados.
5. registrado_por y cancelado_por se obtienen de la sesión autenticada, no se aceptan como una identidad libre enviada por el cliente.
6. El mecánico solo puede asignarse a sí mismo como realizado_por. Administrador/gerente pueden asignar a otro usuario activo que realice trabajo técnico. Esta FK identifica al ejecutor, no necesariamente a quien captura.
7. Solo administrador/gerente registran o cancelan ventas. El cambio posterior de rol de un empleado no invalida su historial.
8. Nuevas ventas requieren cliente activo y un coche sin venta vigente. Nuevos coches requieren proveedor activo.
9. fecha_venta y fecha_revision no pueden ser futuras, usando la fecha de America/Mexico_City. fecha_cancelacion se establece desde el servidor y su fecha local no puede preceder a fecha_venta.
10. La validación de año modelo se realiza al crear/corregir el vehículo; no se usa un CHECK dependiente del paso del tiempo.
11. No se elimina historial en cascada. Clientes, proveedores y usuarios se desactivan. Los coches con historial no se borran.
12. Las revisiones se conservan; las correcciones permitidas son actualizaciones controladas. Una bitácora completa de cambios queda fuera de esta versión.

## Índices previstos

- Índices de PK y UNIQUE para identidad_externa, numero_serie y matricula.
- Índice en coche(id_proveedor).
- Índice UNIQUE parcial en venta(id_coche) WHERE estado = 'registrada'.
- Índices en venta(id_coche), venta(id_cliente), venta(registrado_por), venta(cancelado_por), venta(fecha_venta).
- Índice compuesto en revision(id_coche, fecha_revision).
- Índice en revision(realizado_por).

El índice completo de venta(id_coche) permite consultar también cancelaciones; el parcial protege la unicidad vigente.
Las FK no crean automáticamente índices sobre sus columnas en PostgreSQL.

## Justificación de normalización

1FN: cada fila identifica una entidad u operación, cada campo contiene un valor de su dominio, sin listas de vehículos, usuarios, teléfonos o servicios.
2FN: todas las claves candidatas son de un solo atributo; no hay dependencias parciales de una clave compuesta.
3FN: los atributos no clave dependen de las claves de su propia entidad. Una venta referencia cliente, coche y empleados sin copiar sus nombres o contactos. El coche referencia al proveedor sin repetir su información.
No se almacena el comprador duplicado en COCHE ni un estado vendido derivado de VENTA. El importe de venta depende de la operación y puede diferir del precio de referencia actual.
El rol es un dominio cerrado sin descripciones ni permisos almacenados en USUARIO_INTERNO, por lo que no exige una tabla de roles para este alcance. Los permisos se definen en la aplicación.
La ciudad no determina la dirección ni el nombre del cliente. El nombre de modelo no se trata como un código global que determine la marca; un catálogo de modelos sería una ampliación distinta.
Esta evaluación depende de las reglas de negocio declaradas; añadir sucursales, varios proveedores por unidad o reventas requiere revisar el diseño.

## Lectura de diagramas

01-entidad-relacion.mmd: vista conceptual resumida con rectángulos (entidades), rombos (relaciones) y óvalos (identificadores). Los atributos completos están en el modelo relacional y este diccionario. Las etiquetas min..max indican cuántas veces participa una instancia de la entidad adyacente.
02-modelo-relacional.mmd: tablas, atributos, PK, FK y UK en notación pata de cuervo. Las líneas discontinuas representan relaciones no identificadoras: las FK no forman parte de las PK.
COCHE tiene 0..N ventas históricas porque se conservan las canceladas. La regla de una sola venta vigente se expresa con el índice parcial, no con la cardinalidad histórica.
Mermaid no ejecuta ni demuestra CHECK, defaults, políticas de acceso, índices parciales ni normalización.

