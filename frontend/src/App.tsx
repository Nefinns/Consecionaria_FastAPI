
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Database,
  LoaderCircle,
  Plus,
  RefreshCw,
  ShieldCheck,
  Table2,
  Wifi,
  XCircle,
} from "lucide-react";
import { api } from "@/services/api";

type Json = Record<string, any>;

function getList(data: any): any[] {
  if (Array.isArray(data)) return data;
  if (!data || typeof data !== "object") return [];

  for (const key of [
    "bases_datos",
    "bases",
    "databases",
    "tablas",
    "restricciones",
    "indices",
    "índices",
    "items",
    "results",
  ]) {
    if (Array.isArray(data[key])) return data[key];
  }

  return [];
}

function getDatabaseName(item: any): string {
  if (typeof item === "string") return item;

  return String(
    item?.nombre ??
      item?.name ??
      item?.datname ??
      item?.database ??
      ""
  );
}

function formatValue(value: any): string {
  if (value == null) return "Sin información";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

export default function App() {
  const [bases, setBases] = useState<string[]>([]);
  const [seleccionada, setSeleccionada] = useState("");
  const [nombreNueva, setNombreNueva] = useState("");
  const [estado, setEstado] = useState<Json | null>(null);
  const [conexion, setConexion] = useState<"ok" | "error" | "pendiente">(
    "pendiente"
  );
  const [cargando, setCargando] = useState(false);
  const [operacion, setOperacion] = useState("");
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [modulo, setModulo] = useState<"bases" | "tablas" | "restricciones">(
    "bases"
  );

  const ejecutar = useCallback(
    async <T,>(nombre: string, accion: () => Promise<T>): Promise<T | null> => {
      setCargando(true);
      setOperacion(nombre);
      setError("");
      setMensaje("");

      try {
        return await accion();
      } catch (e) {
        const texto =
          e instanceof Error ? e.message : "Ocurrió un error inesperado.";
        setError(texto);
        return null;
      } finally {
        setCargando(false);
        setOperacion("");
      }
    },
    []
  );

  const cargarBases = useCallback(async () => {
    const data = await ejecutar("bases", () => api<any>("/db/listar"));

    if (data == null) return;

    const lista = getList(data)
      .map(getDatabaseName)
      .filter(Boolean);

    setBases(lista);

    const actual =
      typeof data.seleccionada === "string"
        ? data.seleccionada
        : typeof data.base_seleccionada === "string"
          ? data.base_seleccionada
          : typeof data.nombre_seleccionado === "string"
            ? data.nombre_seleccionado
            : "";

    if (actual) setSeleccionada(actual);
    setMensaje("Lista de bases de datos actualizada.");
  }, [ejecutar]);

  const probarConexion = useCallback(async () => {
    const data = await ejecutar("conexion", () => api<any>("/db/test"));

    if (data != null) {
      setConexion("ok");
      setMensaje("La API respondió correctamente a la prueba de conexión.");
    } else {
      setConexion("error");
    }
  }, [ejecutar]);

  const cargarEstado = useCallback(
    async (mostrarMensaje = true) => {
      const data = await ejecutar("estado", () => api<Json>("/ddl/estado"));

      if (data != null) {
        setEstado(data);
        if (mostrarMensaje) setMensaje("Estado del esquema actualizado.");
      }
    },
    [ejecutar]
  );

  const cargarSeleccion = useCallback(async () => {
    const data = await ejecutar("seleccionada", () =>
      api<any>("/db/seleccionada")
    );

    if (data == null) return;

    const nombre =
      typeof data === "string"
        ? data
        : data.nombre ??
          data.base_datos ??
          data.seleccionada ??
          data.database ??
          "";

    if (nombre) setSeleccionada(String(nombre));
  }, [ejecutar]);

  useEffect(() => {
    void (async () => {
      await cargarBases();
      await probarConexion();
      await cargarSeleccion();
    })();
  }, [cargarBases, probarConexion, cargarSeleccion]);

  const seleccionarBase = async () => {
    if (!seleccionada) {
      setError("Selecciona una base de datos.");
      return;
    }

    const data = await ejecutar("seleccionar", () =>
      api<any>(`/db/seleccionar/${encodeURIComponent(seleccionada)}`, {
        method: "POST",
      })
    );

    if (data == null) return;

    setMensaje(`Base seleccionada: ${seleccionada}`);
    await cargarEstado(false);
  };

  const crearBase = async (e: React.FormEvent) => {
    e.preventDefault();

    const nombre = nombreNueva.trim();

    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(nombre)) {
      setError(
        "Usa un nombre válido: letras, números y guion bajo; no comiences con un número."
      );
      return;
    }

    const data = await ejecutar("crear", () =>
      api<any>("/db/crear", {
        method: "POST",
        body: JSON.stringify({ nombre }),
      })
    );

    if (data == null) return;

    setNombreNueva("");
    setMensaje(`Solicitud de creación completada para ${nombre}.`);
    await cargarBases();
  };

  const crearEsquema = async () => {
    const confirmado = window.confirm(
      "¿Crear el esquema completo en la base seleccionada? Revisa que sea la base correcta."
    );

    if (!confirmado) return;

    const data = await ejecutar("crear-esquema", () =>
      api<any>("/ddl/create-all", { method: "POST" })
    );

    if (data == null) return;

    setMensaje("La operación de creación del esquema terminó correctamente.");
    await cargarEstado(false);
  };

  const tablas = getList(estado?.tablas);
  const restricciones = getList(estado?.restricciones);
  const indices = getList(estado?.indices ?? estado?.índices);

  const totalTablas =
    estado?.total_tablas ?? estado?.totalTablas ?? tablas.length;
  const totalRestricciones =
    estado?.total_restricciones ??
    estado?.totalRestricciones ??
    restricciones.length;
  const totalIndices =
    estado?.total_indices ??
    estado?.totalIndices ??
    indices.length;

  const menu = [
    { id: "bases" as const, label: "Bases de datos", icon: Database },
    { id: "tablas" as const, label: "Tablas y esquema", icon: Table2 },
    {
      id: "restricciones" as const,
      label: "Restricciones",
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-3 text-white">
              <Database size={25} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                DavinciMusic: Panel de administración para bases de datos
              </h1>
              <p className="text-sm text-slate-500">
                Actividades 4.1 · 4.2 · 4.3
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border px-3 py-2 text-sm">
            {conexion === "ok" ? (
              <CheckCircle2 size={17} className="text-emerald-600" />
            ) : conexion === "error" ? (
              <XCircle size={17} className="text-red-600" />
            ) : (
              <Wifi size={17} className="text-slate-400" />
            )}
            <span>
              {conexion === "ok"
                ? "API disponible"
                : conexion === "error"
                  ? "Error de conexión"
                  : "Sin verificar"}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-5 py-7 md:grid-cols-[230px_minmax(0,1fr)]">
        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-3">
          <p className="px-3 pb-3 pt-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Módulos
          </p>

          <nav className="space-y-1">
            {menu.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setModulo(id)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${
                  modulo === id
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Icon size={19} />
                {label}
              </button>
            ))}
          </nav>

          <div className="mt-5 rounded-xl bg-slate-50 p-3">
            <p className="text-xs text-slate-500">Base seleccionada</p>
            <p className="mt-1 break-words text-sm font-semibold">
              {seleccionada || "Ninguna"}
            </p>
          </div>
        </aside>

        <section className="min-w-0 space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-2xl font-bold">
                {menu.find((item) => item.id === modulo)?.label}
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Gestiona tu entorno PostgreSQL desde una sola interfaz.
              </p>
            </div>

            <button
              onClick={() => {
                void cargarBases();
                void cargarEstado();
                void probarConexion();
              }}
              disabled={cargando}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              <RefreshCw size={16} />
              Actualizar
            </button>
          </div>

          {error && (
            <div
              role="alert"
              className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
            >
              <XCircle size={19} className="mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold">No se pudo completar la operación</p>
                <p className="mt-1 break-words">{error}</p>
              </div>
              <button
                onClick={() => setError("")}
                className="ml-auto"
                aria-label="Cerrar error"
              >
                ×
              </button>
            </div>
          )}

          {mensaje && !error && (
            <div
              role="status"
              className="flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800"
            >
              <CheckCircle2 size={18} className="shrink-0" />
              {mensaje}
            </div>
          )}

          {cargando && (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <LoaderCircle size={17} className="animate-spin" />
              Procesando operación...
            </div>
          )}

          {modulo === "bases" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {[
                  {
                    label: "Bases disponibles",
                    value: bases.length,
                    icon: Database,
                  },
                  {
                    label: "Tablas detectadas",
                    value: totalTablas,
                    icon: Table2,
                  },
                  {
                    label: "Estado de conexión",
                    value: conexion === "ok" ? "Conectada" : "Pendiente",
                    icon: Activity,
                  },
                ].map(({ label, value, icon: Icon }) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-slate-200 bg-white p-5"
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-slate-500">{label}</p>
                      <Icon size={20} className="text-indigo-600" />
                    </div>
                    <p className="mt-3 text-2xl font-bold">{value}</p>
                  </div>
                ))}
              </div>

              <div className="grid gap-5 xl:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <h3 className="font-semibold">Seleccionar base de datos</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Selecciona la base antes de consultar o crear el esquema.
                  </p>

                  <label className="mt-5 block text-sm font-medium">
                    Bases disponibles
                  </label>
                  <select
                    value={seleccionada}
                    onChange={(e) => setSeleccionada(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-indigo-500"
                  >
                    <option value="">Selecciona una base...</option>
                    {bases.map((base) => (
                      <option key={base} value={base}>
                        {base}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={() => void seleccionarBase()}
                    disabled={cargando || !seleccionada}
                    className="mt-4 w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Seleccionar base
                  </button>

                  <button
                    onClick={() => void cargarBases()}
                    disabled={cargando}
                    className="mt-2 w-full rounded-xl border px-4 py-3 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
                  >
                    Actualizar lista
                  </button>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <h3 className="font-semibold">Crear base de datos</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Utiliza un nombre nuevo para tu entorno de prácticas.
                  </p>

                  <form onSubmit={crearBase}>
                    <label className="mt-5 block text-sm font-medium">
                      Nombre de la nueva base
                    </label>
                    <input
                      value={nombreNueva}
                      onChange={(e) => setNombreNueva(e.target.value)}
                      placeholder="ejemplo_unidad4"
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-indigo-500"
                    />
                    <button
                      type="submit"
                      disabled={cargando || !nombreNueva.trim()}
                      className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-50"
                    >
                      <Plus size={17} />
                      Crear base
                    </button>
                  </form>

                  <p className="mt-3 text-xs text-slate-500">
                    La creación depende de los permisos del usuario de PostgreSQL.
                  </p>
                </div>
              </div>
            </>
          )}

          {modulo === "tablas" && (
            <>
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="font-semibold">Esquema de la base</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Base: {seleccionada || "ninguna seleccionada"}
                    </p>
                  </div>

                  <button
                    onClick={() => void cargarEstado()}
                    disabled={cargando || !seleccionada}
                    className="rounded-xl border px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
                  >
                    Consultar esquema
                  </button>
                </div>

                <div className="mt-5 flex flex-wrap gap-3">
                  <div className="rounded-xl bg-slate-50 px-4 py-3">
                    <p className="text-xs text-slate-500">Tablas</p>
                    <p className="text-xl font-bold">{totalTablas}</p>
                  </div>
                  <div className="rounded-xl bg-slate-50 px-4 py-3">
                    <p className="text-xs text-slate-500">Restricciones</p>
                    <p className="text-xl font-bold">{totalRestricciones}</p>
                  </div>
                  <div className="rounded-xl bg-slate-50 px-4 py-3">
                    <p className="text-xs text-slate-500">Índices</p>
                    <p className="text-xl font-bold">{totalIndices}</p>
                  </div>
                </div>

                <button
                  onClick={() => void crearEsquema()}
                  disabled={cargando || !seleccionada}
                  className="mt-5 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  Crear esquema completo
                </button>
                <p className="mt-2 text-xs text-slate-500">
                  Ejecuta la operación definida en el backend. Verifica la base seleccionada antes de continuar.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <h3 className="mb-4 font-semibold">Tablas detectadas</h3>
                {tablas.length ? (
                  <div className="space-y-2">
                    {tablas.map((tabla, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-3 rounded-xl border border-slate-100 p-3"
                      >
                        <Table2 size={18} className="text-indigo-600" />
                        <span className="break-all text-sm">
                          {typeof tabla === "string"
                            ? tabla
                            : tabla.nombre ??
                              tabla.name ??
                              tabla.tabla ??
                              JSON.stringify(tabla)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    Sin datos para mostrar. Selecciona una base y consulta el esquema.
                  </p>
                )}
              </div>
            </>
          )}

          {modulo === "restricciones" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Restricciones reportadas</p>
                  <p className="mt-2 text-3xl font-bold">{totalRestricciones}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Índices reportados</p>
                  <p className="mt-2 text-3xl font-bold">{totalIndices}</p>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="font-semibold">Restricciones e índices</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Información devuelta por el backend.
                    </p>
                  </div>
                  <button
                    onClick={() => void cargarEstado()}
                    disabled={cargando || !seleccionada}
                    className="rounded-xl border px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
                  >
                    Actualizar
                  </button>
                </div>

                <h4 className="mb-2 mt-5 text-sm font-semibold">Restricciones</h4>
                <pre className="max-h-96 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                  {restricciones.length
                    ? formatValue(restricciones)
                    : "No hay restricciones disponibles en la respuesta actual."}
                </pre>

                <h4 className="mb-2 mt-5 text-sm font-semibold">Índices</h4>
                <pre className="max-h-96 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                  {indices.length
                    ? formatValue(indices)
                    : "No hay índices disponibles en la respuesta actual."}
                </pre>

                <details className="mt-5">
                  <summary className="cursor-pointer text-sm font-medium">
                    Ver respuesta completa del backend
                  </summary>
                  <pre className="mt-3 max-h-96 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                    {estado
                      ? formatValue(estado)
                      : "Primero consulta el estado del esquema."}
                  </pre>
                </details>
              </div>
            </>
          )}

          <footer className="flex items-center justify-between gap-3 border-t border-slate-200 py-4 text-xs text-slate-500">
            <span>Panel académico · PostgreSQL</span>
            <span>API: {import.meta.env.VITE_API_URL || "127.0.0.1:8000"}</span>
          </footer>
        </section>
      </main>
    </div>
  );
}
