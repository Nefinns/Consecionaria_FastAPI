import os
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

ventana = tk.Tk()
ventana.title("Concesionaria - DDL y DCL")
ventana.geometry("900x700")
ventana.minsize(800, 600)
ventana.configure(bg="#eef3f8")

# Colores
COLOR_FONDO = "#eef3f8"
COLOR_AZUL = "#1f4e78"
COLOR_AZUL_CLARO = "#2f75b5"
COLOR_TURQUESA = "#168aad"
COLOR_BLANCO = "#ffffff"
COLOR_TEXTO = "#243447"
COLOR_SQL = "#1e293b"
COLOR_RESULTADO = "#f8fafc"
COLOR_BORDE = "#cbd5e1"

# Estilos
estilo = ttk.Style()
estilo.theme_use("clam")

estilo.configure(
    "TNotebook",
    background=COLOR_FONDO,
    borderwidth=0
)

estilo.configure(
    "TNotebook.Tab",
    background="#dbe7f2",
    foreground=COLOR_TEXTO,
    padding=(20, 10),
    font=("Segoe UI", 10, "bold")
)

estilo.map(
    "TNotebook.Tab",
    background=[("selected", COLOR_AZUL)],
    foreground=[("selected", COLOR_BLANCO)]
)

estilo.configure(
    "TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(12, 8),
    background=COLOR_AZUL_CLARO,
    foreground=COLOR_BLANCO,
    borderwidth=0
)

estilo.map(
    "TButton",
    background=[
        ("active", COLOR_TURQUESA),
        ("pressed", COLOR_AZUL)
    ]
)

estilo.configure(
    "TCombobox",
    padding=6,
    font=("Segoe UI", 10)
)

estilo.configure(
    "TLabel",
    background=COLOR_FONDO,
    foreground=COLOR_TEXTO,
    font=("Segoe UI", 10)
)

estilo.configure(
    "TLabelframe",
    background=COLOR_FONDO,
    bordercolor=COLOR_BORDE
)

estilo.configure(
    "TLabelframe.Label",
    background=COLOR_FONDO,
    foreground=COLOR_AZUL,
    font=("Segoe UI", 10, "bold")
)

# Título
titulo = tk.Label(
    ventana,
    text="Sistema de Concesionaria",
    font=("Segoe UI", 20, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_AZUL
)
titulo.pack(pady=(20, 4))

subtitulo = tk.Label(
    ventana,
    text="Gestión de operaciones DDL y DCL",
    font=("Segoe UI", 10),
    bg=COLOR_FONDO,
    fg="#64748b"
)
subtitulo.pack(pady=(0, 15))

# Pestañas
pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="both", expand=True, padx=20, pady=(0, 20))

pestana_ddl = ttk.Frame(pestanas, padding=15)
pestana_dcl = ttk.Frame(pestanas, padding=15)

pestanas.add(pestana_ddl, text="  DDL  ")
pestanas.add(pestana_dcl, text="  DCL  ")

# Funciones


def mostrar_sql(texto):
    area_sql.delete("1.0", tk.END)
    area_sql.insert(tk.END, texto)
    area_sql_dcl.delete("1.0", tk.END)
    area_sql_dcl.insert(tk.END, texto)


def mostrar_resultado(texto):
    resultado.delete("1.0", tk.END)
    resultado.insert(tk.END, texto)
    resultado_dcl.delete("1.0", tk.END)
    resultado_dcl.insert(tk.END, texto)


def manejar_error(error):
    try:
        mensaje = error.response.json().get("detail", "Error desconocido")
    except Exception:
        mensaje = str(error)

    mostrar_resultado(mensaje)
    messagebox.showerror("Error", mensaje)


def obtener_sql_ddl():
    operacion = combo_operacion.get().lower()
    tabla = combo_tabla.get()

    try:
        respuesta = requests.get(
            f"{API_URL}/dcl/ddl/sql/{operacion}/{tabla}"
        )
        respuesta.raise_for_status()
        mostrar_sql(respuesta.json()["SQL"])
    except requests.RequestException as error:
        manejar_error(error)


def ejecutar_ddl():
    operacion = combo_operacion.get().lower()
    tabla = combo_tabla.get()

    try:
        if operacion == "create":
            respuesta = requests.post(f"{API_URL}/ddl/create/{tabla}")
        elif operacion == "alter":
            respuesta = requests.put(f"{API_URL}/ddl/alter/{tabla}")
        else:
            respuesta = requests.delete(f"{API_URL}/ddl/drop/{tabla}")

        respuesta.raise_for_status()
        datos = respuesta.json()

        mostrar_resultado(datos["Mensaje:"])
        obtener_sql_ddl()

    except requests.RequestException as error:
        manejar_error(error)


def ejecutar_dcl():
    usuario = entrada_usuario.get()
    password = entrada_contrasena.get()
    operacion = combo_operacion_dcl.get()

    if not usuario:
        messagebox.showwarning("Aviso", "Selecciona un usuario.")
        return

    if operacion == "Crear usuario" and not password:
        messagebox.showwarning("Aviso", "Escribe una contraseña.")
        return

    try:
        if operacion == "Crear usuario":
            respuesta = requests.post(
                f"{API_URL}/dcl/crear_usuario",
                json={"usuario": usuario, "password": password}
            )
        elif operacion == "Eliminar usuario":
            respuesta = requests.delete(
                f"{API_URL}/dcl/borrar_usuario/{usuario}"
            )
        elif operacion == "Otorgar permiso":
            respuesta = requests.post(f"{API_URL}/dcl/grant/{usuario}")
        else:
            respuesta = requests.post(f"{API_URL}/dcl/revoke/{usuario}")

        respuesta.raise_for_status()
        datos = respuesta.json()

        mostrar_resultado(datos["Mensaje"])
        obtener_sql_dcl()

    except requests.RequestException as error:
        manejar_error(error)


def obtener_sql_dcl():
    usuario = entrada_usuario.get()
    password = entrada_contrasena.get()
    operacion = combo_operacion_dcl.get()

    if not usuario:
        return

    operaciones = {
        "Crear usuario": "crear_usuario",
        "Eliminar usuario": "eliminar_usuario",
        "Otorgar permiso": "otorgar_permiso",
        "Quitar permiso": "quitar_permiso"
    }

    try:
        respuesta = requests.post(
            f"{API_URL}/dcl/sql/{operaciones[operacion]}",
            json={
                "usuario": usuario,
                "password": password
            }
        )

        respuesta.raise_for_status()
        mostrar_sql(respuesta.json()["SQL"])

    except requests.RequestException as error:
        manejar_error(error)


def consultar_usuarios():
    try:
        respuesta = requests.get(f"{API_URL}/dcl/usuarios")
        respuesta.raise_for_status()

        usuarios = respuesta.json()["usuarios"]

        mostrar_resultado(
            "\n".join(usuarios) if usuarios else "No hay usuarios registrados."
        )

    except requests.RequestException as error:
        manejar_error(error)


def consultar_permisos():
    usuario = entrada_usuario.get()

    if not usuario:
        messagebox.showwarning("Aviso", "Selecciona un usuario.")
        return

    try:
        respuesta = requests.get(
            f"{API_URL}/dcl/permisos/{usuario}"
        )
        respuesta.raise_for_status()

        permisos = respuesta.json()["permisos"]

        if not permisos:
            mostrar_resultado(f"El usuario '{usuario}' no tiene permisos.")
            return

        texto = ""

        for permiso in permisos:
            texto += (
                f"Tabla: {permiso['tabla']}    "
                f"Privilegio: {permiso['privilegio']}\n"
            )

        mostrar_resultado(texto)

    except requests.RequestException as error:
        manejar_error(error)


# Interfaz DDL
marco_ddl = ttk.LabelFrame(
    pestana_ddl,
    text="Operaciones DDL",
    padding=15
)
marco_ddl.pack(fill="x", pady=(0, 15))

ttk.Label(marco_ddl, text="Operación").grid(
    row=0, column=0, padx=8, pady=8, sticky="w"
)

combo_operacion = ttk.Combobox(
    marco_ddl,
    values=["CREATE", "ALTER", "DROP"],
    state="readonly",
    width=18
)
combo_operacion.current(0)
combo_operacion.grid(row=0, column=1, padx=8, pady=8)

ttk.Label(marco_ddl, text="Tabla").grid(
    row=0, column=2, padx=8, pady=8, sticky="w"
)

combo_tabla = ttk.Combobox(
    marco_ddl,
    values=[
        "cliente",
        "coche",
        "revision",
        "proveedor",
        "servicio"
    ],
    state="readonly",
    width=20
)
combo_tabla.current(0)
combo_tabla.grid(row=0, column=3, padx=8, pady=8)

boton_ver_sql_ddl = ttk.Button(
    marco_ddl,
    text="Ver SQL",
    command=obtener_sql_ddl
)
boton_ver_sql_ddl.grid(row=1, column=0, columnspan=2, padx=8, pady=8)

boton_ejecutar_ddl = ttk.Button(
    marco_ddl,
    text="Ejecutar operación",
    command=ejecutar_ddl
)
boton_ejecutar_ddl.grid(row=1, column=2, columnspan=2, padx=8, pady=8)

# Área SQL
marco_sql = ttk.LabelFrame(
    pestana_ddl,
    text="Consulta SQL",
    padding=10
)
marco_sql.pack(fill="both", expand=True, pady=(0, 15))

area_sql = tk.Text(
    marco_sql,
    height=8,
    bg=COLOR_SQL,
    fg="#e2e8f0",
    insertbackground=COLOR_BLANCO,
    font=("Consolas", 10),
    relief="flat",
    padx=12,
    pady=10
)
area_sql.pack(fill="both", expand=True)

# Área resultado
marco_resultado = ttk.LabelFrame(
    pestana_ddl,
    text="Resultado",
    padding=10
)
marco_resultado.pack(fill="both", expand=True)

resultado = tk.Text(
    marco_resultado,
    height=6,
    bg=COLOR_RESULTADO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 10),
    relief="flat",
    padx=12,
    pady=10
)
resultado.pack(fill="both", expand=True)

# Interfaz DCL
marco_dcl = ttk.LabelFrame(
    pestana_dcl,
    text="Control de usuarios y permisos",
    padding=15
)
marco_dcl.pack(fill="x", pady=(0, 15))

ttk.Label(marco_dcl, text="Usuario").grid(
    row=0, column=0, padx=8, pady=8, sticky="w"
)

entrada_usuario = ttk.Combobox(
    marco_dcl,
    values=[
        "gerente",
        "vendedor",
        "vendedor_02",
        "recepcion",
        "mecanico",
        "mecanico_02",
        "asesor_servicio",
        "almacen",
        "contador",
        "compras",
        "administrador",
        "supervisor",
        "proveedores",
        "inventario",
        "auditor"
    ],
    state="readonly",
    width=22
)
entrada_usuario.grid(row=0, column=1, padx=8, pady=8)

ttk.Label(marco_dcl, text="Contraseña").grid(
    row=0, column=2, padx=8, pady=8, sticky="w"
)

entrada_contrasena = ttk.Entry(
    marco_dcl,
    show="*",
    width=22
)
entrada_contrasena.grid(row=0, column=3, padx=8, pady=8)

ttk.Label(marco_dcl, text="Operación").grid(
    row=1, column=0, padx=8, pady=8, sticky="w"
)

combo_operacion_dcl = ttk.Combobox(
    marco_dcl,
    values=[
        "Crear usuario",
        "Eliminar usuario",
        "Otorgar permiso",
        "Quitar permiso"
    ],
    state="readonly",
    width=22
)
combo_operacion_dcl.current(0)
combo_operacion_dcl.grid(row=1, column=1, padx=8, pady=8)

boton_ejecutar_dcl = ttk.Button(
    marco_dcl,
    text="Ejecutar operación",
    command=ejecutar_dcl
)
boton_ejecutar_dcl.grid(
    row=1, column=2, columnspan=2, padx=8, pady=8
)

marco_botones_dcl = ttk.Frame(pestana_dcl)
marco_botones_dcl.pack(fill="x", pady=(0, 15))

boton_sql_dcl = ttk.Button(
    marco_botones_dcl,
    text="Ver SQL",
    command=obtener_sql_dcl
)
boton_sql_dcl.pack(side="left", padx=5)

boton_usuarios = ttk.Button(
    marco_botones_dcl,
    text="Consultar usuarios",
    command=consultar_usuarios
)
boton_usuarios.pack(side="left", padx=5)

boton_permisos = ttk.Button(
    marco_botones_dcl,
    text="Consultar permisos",
    command=consultar_permisos
)
boton_permisos.pack(side="left", padx=5)

marco_sql_dcl = ttk.LabelFrame(
    pestana_dcl,
    text="Consulta SQL",
    padding=10
)
marco_sql_dcl.pack(fill="both", expand=True, pady=(0, 15))

area_sql_dcl = tk.Text(
    marco_sql_dcl,
    height=5,
    bg=COLOR_SQL,
    fg="#e2e8f0",
    insertbackground=COLOR_BLANCO,
    font=("Consolas", 10),
    relief="flat",
    padx=12,
    pady=10
)
area_sql_dcl.pack(fill="both", expand=True)

marco_resultado_dcl = ttk.LabelFrame(
    pestana_dcl,
    text="Resultado",
    padding=10
)
marco_resultado_dcl.pack(fill="both", expand=True)

scroll_resultado_dcl = ttk.Scrollbar(marco_resultado_dcl, orient="vertical")
scroll_resultado_dcl.pack(side="right", fill="y")

resultado_dcl = tk.Text(
    marco_resultado_dcl,
    height=6,
    bg=COLOR_RESULTADO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 10),
    relief="flat",
    padx=12,
    pady=10,
    yscrollcommand=scroll_resultado_dcl.set
)
resultado_dcl.pack(side="left", fill="both", expand=True)

scroll_resultado_dcl.config(command=resultado_dcl.yview)

ventana.mainloop()
