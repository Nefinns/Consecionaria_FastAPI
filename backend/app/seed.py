"""Registros ficticios para practicar; no representan operaciones reales ni usuarios autenticados."""
from datetime import date, datetime
from sqlalchemy import text

NOMBRES = ['Andrea López', 'Mauricio Ortega', 'Fernanda Ruiz', 'Daniel Serrano',
    'Valeria Campos', 'Diego Medina', 'Sofía Navarro', 'Jorge Salinas',
    'Renata Solís', 'Leonardo Cruz', 'Camila Paredes', 'Eduardo Rojas',
    'Lucía Aguilar', 'Emiliano Vega', 'Paola Jiménez', 'Iván Morales',
    'Mariana Flores', 'Carlos Zúñiga']
PROVEEDORES = ['Autos del Bajío', 'Distribuidora Norte', 'Vehículos Occidente',
    'Movilidad del Pacífico', 'Grupo Automotor Central', 'Lotes del Centro']
CATALOGO = [
    ('Toyota','Corolla',2023,'Gris',325000),('Nissan','Versa',2022,'Blanco',232000),
    ('Honda','Civic',2024,'Azul',418000),('Mazda','Mazda 3',2021,'Rojo',285000),
    ('Volkswagen','Jetta',2020,'Negro',255000),('Kia','Rio',2023,'Blanco',248000),
    ('Hyundai','Elantra',2022,'Plata',278000),('Chevrolet','Onix',2024,'Azul',289000),
    ('Ford','Escape',2021,'Gris',369000),('Toyota','RAV4',2023,'Rojo',468000),
    ('Nissan','Sentra',2024,'Blanco',342000),('Honda','CR-V',2022,'Negro',455000),
    ('Mazda','CX-30',2023,'Gris',419000),('Volkswagen','Taos',2024,'Plata',479000),
    ('Kia','Seltos',2022,'Azul',355000),('Hyundai','Creta',2023,'Rojo',339000),
    ('Chevrolet','Tracker',2021,'Blanco',298000),('Ford','Mustang',2020,'Negro',680000),
    ('Toyota','Yaris',2022,'Gris',259000),('Nissan','Kicks',2023,'Azul',319000),
    ('Honda','City',2021,'Plata',268000),('Mazda','CX-5',2024,'Blanco',510000),
    ('Volkswagen','Virtus',2023,'Rojo',312000),('Kia','Sportage',2024,'Gris',539000),
    ('Hyundai','Tucson',2022,'Negro',419000),('Chevrolet','Aveo',2023,'Plata',234000),
    ('Ford','Ranger',2021,'Azul',560000),('Toyota','Hilux',2022,'Blanco',585000),
    ('Nissan','March',2020,'Rojo',189000),('Mazda','Mazda 2',2024,'Gris',324000),
]

def seed_demo(conn):
    for i, nombre in enumerate(NOMBRES, 1):
        conn.execute(text('''INSERT INTO cliente (nombre,telefono,correo,direccion,ciudad,activo)
            VALUES (:nombre,:tel,:correo,:dir,:ciudad,:activo)'''), {
            'nombre':nombre,'tel':f'33-5550-{i:04d}',
            'correo':f'cliente{i:02d}@example.test','dir':f'Calle Demostración {i*7}',
            'ciudad': ['Guadalajara','Zapopan','Tlaquepaque','Tonalá'][i%4],
            'activo':i not in (17,18)})
    for i, nombre in enumerate(PROVEEDORES,1):
        conn.execute(text('''INSERT INTO proveedor(nombre,telefono,correo,direccion,ciudad,activo)
            VALUES (:nom,:tel,:correo,:dir,:ciudad,:activo)'''), {
            'nom': nombre,'tel':f'33-5880-{i:04d}', 'correo':f'proveedor{i:02d}@example.test',
            'dir':f'Av. Inventada {i*40}', 'ciudad':'Guadalajara','activo':i!=6})
    personas = [('Administrador Demo','administrador'),('Gerente Demo','gerente'),
        ('Mecánico Uno','mecanico'),('Mecánico Dos','mecanico'),('Gerente Inactivo','gerente')]
    for i,(nombre,rol) in enumerate(personas,1):
        conn.execute(text('''INSERT INTO usuario_interno(identidad_externa,nombre,rol,activo)
            VALUES (:ident,:nombre,:rol,:activo)'''),{
            'ident':f'AUTOGEST-DEMO-NO-AUTH-{i:03d}', 'nombre':nombre,'rol':rol, 'activo':i!=5})
    for i, (marca,modelo,anio,color,precio) in enumerate(CATALOGO,1):
        conn.execute(text('''INSERT INTO coche(id_proveedor,numero_serie,matricula,marca,modelo,anio,color,precio_referencia)
            VALUES (:pro,:serie,:placa,:marca,:modelo,:anio,:color,:precio)'''), {
            'pro': (i-1)%5+1, 'serie':f'AUTOGESTVIN{i:017d}', 'placa':f'JAL-{i:04d}',
            'marca':marca,'modelo':modelo,'anio':anio,'color':color,'precio':precio})
    for i in range(1,29):
        for j in range(1, 2+(i%3==0)):
            conn.execute(text('''INSERT INTO revision(id_coche,realizado_por,fecha_revision,kilometraje,
                    cambio_filtro,cambio_aceite,cambio_frenos,observaciones)
                    VALUES (:coche,:por,:fecha,:km,:filtro,:aceite,:frenos,:obs)'''),{
                'coche':i, 'por':3 if i%2 else 4,
                'fecha':date(2026,1+(i%6),min(26,4+i%19+j)),
                'km': 8000+i*890+j*1500, 'filtro':i%3==0,
                'aceite':i%2==0, 'frenos':i%5==0,
                'obs':'Revisión programada con datos ficticios.'})
    for i in range(1,18):
        canceled = i in (5,10,14,16)
        base_date = date(2026,3+(i%3),10+(i%12))
        conn.execute(text('''INSERT INTO venta(id_coche,id_cliente,registrado_por,fecha_venta,importe,estado,
                cancelado_por,fecha_cancelacion,motivo_cancelacion)
            VALUES (:coche,:cliente,:por,:fecha,:importe,:estado,:cancelado_por,:cancelacion,:motivo)'''),{
            'coche':i,'cliente':(i%16)+1,'por':1 if i%2 else 2,
            'fecha':base_date, 'importe':CATALOGO[i-1][4]-5000+(i%4)*1500,
            'estado':'cancelada' if canceled else 'registrada',
            'cancelado_por':2 if canceled else None,
            'cancelacion': datetime(2026,8,10,14,0) if canceled else None,
            'motivo':'Operación cancelada por demostración' if canceled else None})
    return {'clientes':len(NOMBRES),'proveedores':len(PROVEEDORES),
            'usuarios_internos':len(personas), 'coches':len(CATALOGO),
            'ventas':17,'revisiones':sum(1+(i%3==0) for i in range(1,29))}
