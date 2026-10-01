consultas_31 = {

    # SELECCIÓN

    "seleccion_1": """
        SELECT *
        FROM cliente
        WHERE ciudad = 'Guadalajara';
    """,

    "seleccion_2": """
        SELECT *
        FROM cliente
        WHERE nif = '45120378K';
    """,

    "seleccion_3": """
        SELECT *
        FROM coche
        WHERE color = 'Rojo';
    """,

    "seleccion_4": """
        SELECT *
        FROM coche
        WHERE precio_venta > 350000;
    """,

    "seleccion_5": """
        SELECT *
        FROM revision
        WHERE cambio_aceite = 'S' AND cambio_frenos = 'S';
    """,


    # PROYECCIÓN

    "proyeccion_1": """
        SELECT nombre_cliente
        FROM cliente;
    """,

    "proyeccion_2": """
        SELECT nombre_cliente, ciudad
        FROM cliente;
    """,

    "proyeccion_3": """
        SELECT marca, modelo
        FROM coche;
    """,

    "proyeccion_4": """
        SELECT matricula, precio_venta
        FROM coche;
    """,

    "proyeccion_5": """
        SELECT matricula, cambio_aceite, cambio_frenos
        FROM revision;
    """,


    # JOIN

    "join_1": """
        SELECT c.nombre_cliente, co.matricula
        FROM cliente c
        JOIN coche co ON c.codigo_cliente = co.codigo_cliente;
    """,

    "join_2": """
        SELECT co.matricula, co.marca, co.modelo,
               r.fecha_revision, r.cambio_filtro, r.cambio_aceite, r.cambio_frenos, r.otros
        FROM coche co
        JOIN revision r ON co.matricula = r.matricula;
    """,

    "join_3": """
        SELECT c.nombre_cliente, co.matricula, co.marca, co.modelo,
               r.fecha_revision, r.cambio_aceite, r.cambio_frenos
        FROM cliente c
        JOIN coche co ON c.codigo_cliente = co.codigo_cliente
        JOIN revision r ON co.matricula = r.matricula;
    """,

    "join_4": """
        SELECT c.nombre_cliente, co.matricula, co.marca, co.modelo
        FROM cliente c
        JOIN coche co ON c.codigo_cliente = co.codigo_cliente
        WHERE co.marca = 'Toyota';
    """,

    "join_5": """
        SELECT co.matricula, co.marca, co.modelo, r.fecha_revision, r.cambio_aceite
        FROM coche co
        JOIN revision r ON co.matricula = r.matricula
        WHERE r.cambio_aceite = 'S';
    """,


    # UNIÓN
    # Nota: union_1/union_3/union_5 y union_2/union_4 comparten la misma
    # fórmula porque el documento teórico repite esos dos patrones (solo
    # hay dos pares de columnas compatibles entre las tres tablas).

    "union_1": """
        SELECT codigo_cliente FROM cliente
        UNION
        SELECT codigo_cliente FROM coche;
    """,

    "union_2": """
        SELECT matricula FROM coche
        UNION
        SELECT matricula FROM revision;
    """,

   "union_3": """
        SELECT nombre_cliente FROM cliente WHERE ciudad = 'Tonalá'
        UNION
        SELECT nombre_cliente FROM cliente WHERE ciudad = 'Zapopan';
    """,

    "union_4": """
        SELECT matricula FROM coche WHERE color = 'Rojo'
        UNION
        SELECT matricula FROM coche WHERE precio_venta > 400000;
    """,

    "union_5": """
        SELECT matricula FROM revision WHERE cambio_aceite = 'S'
        UNION
        SELECT matricula FROM revision WHERE cambio_frenos = 'S';
    """,

    # INTERSECCIÓN

    "interseccion_1": """
        SELECT codigo_cliente FROM cliente
        INTERSECT
        SELECT codigo_cliente FROM coche;
    """,

    "interseccion_2": """
        SELECT matricula FROM coche
        INTERSECT
        SELECT matricula FROM revision;
    """,

    "interseccion_3": """
        SELECT codigo_cliente FROM cliente
        INTERSECT
        SELECT codigo_cliente FROM coche WHERE marca = 'Toyota';
    """,

    "interseccion_4": """
        SELECT matricula FROM coche
        INTERSECT
        SELECT matricula FROM revision WHERE cambio_aceite = 'S';
    """,

    "interseccion_5": """
        SELECT matricula FROM coche
        INTERSECT
        SELECT matricula FROM revision WHERE cambio_frenos = 'S';
    """,


    # DIFERENCIA (EXCEPT)

    "diferencia_1": """
        SELECT codigo_cliente FROM cliente
        EXCEPT
        SELECT codigo_cliente FROM coche;
    """,

    "diferencia_2": """
        SELECT matricula FROM coche
        EXCEPT
        SELECT matricula FROM revision;
    """,

    "diferencia_3": """
        SELECT codigo_cliente FROM cliente
        EXCEPT
        SELECT codigo_cliente FROM coche WHERE marca = 'Toyota';
    """,

    "diferencia_4": """
        SELECT matricula FROM coche
        EXCEPT
        SELECT matricula FROM revision WHERE cambio_aceite = 'S';
    """,

    "diferencia_5": """
        SELECT matricula FROM coche
        EXCEPT
        SELECT matricula FROM revision WHERE cambio_frenos = 'S';
    """
}


consultas_32 = {

    # INSERT - CLIENTE

    "insert_cliente_1": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('45120378K', 'Laura Ramírez Gómez', 'Av. Hidalgo 245', 'Tonalá', '3312457890');
    """,

    "insert_cliente_2": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('38294011T', 'Miguel Ángel Torres Vega', 'Calle Juárez 87', 'Guadalajara', '3314820366');
    """,

    "insert_cliente_3": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('51003467M', 'Ana Sofía Delgado Ruiz', 'Priv. Colón 12', 'Zapopan', '3339015744');
    """,

    "insert_cliente_4": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('29845173P', 'Roberto Núñez Salas', 'Av. Tonaltecas 310', 'Tonalá', '3327148055');
    """,

    "insert_cliente_5": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('60712394D', 'Carmen Ibarra Luna', 'Calle Morelos 58', 'Tlaquepaque', '3318604921');
    """,

    "insert_cliente_6": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('47038261H', 'Javier Peña Castro', 'Av. Patria 1204', 'Zapopan', '3345209183');
    """,

    "insert_cliente_7": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('55901728B', 'Daniela Fuentes Mora', 'Calle Reforma 76', 'Guadalajara', '3311937642');
    """,

    "insert_cliente_8": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('31674508R', 'Óscar Beltrán Ríos', 'Av. Río Nilo 902', 'Tonalá', '3350782314');
    """,

    "insert_cliente_9": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('62185043W', 'Silvia Aguilar Pérez', 'Calle Allende 33', 'Tlajomulco', '3323610478');
    """,

    "insert_cliente_10": """
        INSERT INTO cliente
        (nif, nombre_cliente, direccion, ciudad, telefono)
        VALUES
        ('40536912G', 'Héctor Villaseñor Cruz', 'Av. López Mateos 640', 'Zapopan', '3336059127');
    """,


    # INSERT - COCHE

    "insert_coche_1": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JGR4821',
        'Nissan',
        'Versa',
        'Rojo',
        289900.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '45120378K')
    );
""",

    "insert_coche_2": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JHT9054',
        'Volkswagen',
        'Jetta',
        'Blanco',
        412500.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '38294011T')
    );
""",

    "insert_coche_3": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JKM1637',
        'Chevrolet',
        'Aveo',
        'Gris',
        265000.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '51003467M')
    );
""",

    "insert_coche_4": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JLP7742',
        'Nissan',
        'Sentra',
        'Negro',
        398000.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '51003467M')
    );
""",

    "insert_coche_5": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JMR2018',
        'Kia',
        'Río',
        'Azul',
        315750.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '29845173P')
    );
""",

    "insert_coche_6": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JNS5490',
        'Toyota',
        'Yaris',
        'Plata',
        342000.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '60712394D')
    );
""",

    "insert_coche_7": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JPB6123',
        'Mazda',
        'Mazda 3',
        'Rojo',
        455900.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '47038261H')
    );
""",

    "insert_coche_8": """
    INSERT INTO coche
    (matricula, marca, modelo, color, precio_venta, codigo_cliente)
    VALUES
    (
        'JQC8357',
        'Honda',
        'City',
        'Blanco',
        389400.00,
        (SELECT codigo_cliente FROM cliente WHERE nif = '31674508R')
    );
""",
    "insert_coche_9": """
        INSERT INTO coche
        (matricula, marca, modelo, color, precio_venta, codigo_cliente)
        VALUES
        ('JRD3269', 'Hyundai', 'Grand i10', 'Verde', 248900.00, NULL);
    """,

    "insert_coche_10": """
        INSERT INTO coche
        (matricula, marca, modelo, color, precio_venta, codigo_cliente)
        VALUES
        ('JSF9805', 'Volkswagen', 'Polo', 'Negro', 327600.00, NULL);
    """,


    # INSERT - REVISION

    "insert_revision_1": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-02-10', 'S', 'S', 'N', 'Revisión de 5000 km', 'JGR4821');
    """,

    "insert_revision_2": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-06-18', 'N', 'S', 'S', 'Alineación y balanceo', 'JGR4821');
    """,

    "insert_revision_3": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-03-04', 'S', 'S', 'N', NULL, 'JHT9054');
    """,

    "insert_revision_4": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-03-22', 'N', 'N', 'S', 'Cambio de balatas traseras', 'JKM1637');
    """,

    "insert_revision_5": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-04-08', 'S', 'S', 'S', 'Revisión de suspensión', 'JLP7742');
    """,

    "insert_revision_6": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-04-27', 'S', 'N', 'N', NULL, 'JMR2018');
    """,

    "insert_revision_7": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-05-13', 'N', 'S', 'N', 'Cambio de anticongelante', 'JNS5490');
    """,

    "insert_revision_8": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-05-30', 'S', 'S', 'N', 'Revisión de 10000 km', 'JPB6123');
    """,

    "insert_revision_9": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-06-11', 'N', 'S', 'S', NULL, 'JQC8357');
    """,

    "insert_revision_10": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-07-09', 'S', 'S', 'N', 'Cambio de bujías', 'JGR4821');
    """,

    "insert_revision_11": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-08-02', 'N', 'S', 'N', 'Recarga de aire acondicionado', 'JLP7742');
    """,

    "insert_revision_12": """
        INSERT INTO revision
        (fecha_revision, cambio_filtro, cambio_aceite, cambio_frenos, otros, matricula)
        VALUES
        ('2026-08-25', 'S', 'S', 'S', 'Revisión general de frenos', 'JHT9054');
    """
}
