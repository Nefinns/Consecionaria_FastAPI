import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import {
  Activity, AlertTriangle, ArrowRightLeft, CheckCircle2, Database, Download,
  FileArchive, FileDown, FileUp, HardDrive, LoaderCircle, Plus, RefreshCw,
  Server, ShieldCheck, Table2, Upload, Users, XCircle,
} from 'lucide-react';
import { api, descargar, enviarArchivo } from '@/services/api';

type Modulo = 'bases' | 'esquema' | 'restricciones' | 'backup' | 'usuarios' | 'transferir';
type Esquema = { base_datos: string; tablas: string[]; restricciones: Array<{table_name: string; constraint_name: string; constraint_type: string}>;
  indices: Array<{tablename: string; indexname: string}>; total_tablas: number; total_restricciones: number; total_indices: number };
type Rol = { usuario: string; descripcion: string; tabla: string; operacion: string; existe?: boolean };
type Permiso = { table_name: string; privilege_type: string; is_grantable?: string };
type Archivo = { nombre: string; bytes: number; fecha: string };
type Tabla = { nombre: string; existe: boolean; registros: number; columnas: string[] };
type Migracion = { origen: { base: string; tablas: Record<string, number | null> }; mysql_configurado: boolean;
  destino?: {base: string; version: string; tablas_existentes: string[]; tablas: Record<string, number>} };
type BackupConfig = { base_origen: string | null; servidor_origen: string; restauracion_configurada: boolean;
  servidor_destino: string | null; base_destino: string | null; pg_dump_disponible: boolean; pg_restore_disponible: boolean };

const MODULOS: Array<{id: Modulo; nombre: string; subtitulo: string; icon: typeof Database}> = [
  { id: 'bases', nombre: 'Bases de datos', subtitulo: '4.1', icon: Database },
  { id: 'esquema', nombre: 'Tablas y esquema', subtitulo: '4.2', icon: Table2 },
  { id: 'restricciones', nombre: 'Restricciones', subtitulo: '4.3', icon: ShieldCheck },
  { id: 'backup', nombre: 'Respaldos', subtitulo: '4.4', icon: HardDrive },
  { id: 'usuarios', nombre: 'Usuarios y permisos', subtitulo: '4.5', icon: Users },
  { id: 'transferir', nombre: 'Importar y migrar', subtitulo: '4.6', icon: ArrowRightLeft },
];
const cssInput = 'w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-500';
const cssPrimary = 'inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-40';
const cssSecondary = 'inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40';
const cssBox = 'rounded-2xl border border-slate-200 bg-white p-5';

function mensajeError(error: unknown): string {
  return error instanceof Error ? error.message : 'Ocurrió un error inesperado.';
}

export default function App() {
  const [modulo, setModulo] = useState<Modulo>('bases');
  const [bases, setBases] = useState<string[]>([]);
  const [seleccionada, setSeleccionada] = useState('');
  const [baseNueva, setBaseNueva] = useState('');
  const [esquema, setEsquema] = useState<Esquema | null>(null);
  const [datosPrueba, setDatosPrueba] = useState<{total_registros:number;puede_cargar:boolean}|null>(null);
  const [estadoApi, setEstadoApi] = useState<'pendiente' | 'ok' | 'error'>('pendiente');
  const [roles, setRoles] = useState<Rol[]>([]);
  const [usuario, setUsuario] = useState('gerente');
  const [contrasena, setContrasena] = useState('');
  const [permisos, setPermisos] = useState<Permiso[]>([]);
  const [archivos, setArchivos] = useState<Archivo[]>([]);
  const [archivoRestore, setArchivoRestore] = useState('');
  const [backupConfig, setBackupConfig] = useState<BackupConfig | null>(null);
  const [tablasCsv, setTablasCsv] = useState<Tabla[]>([]);
  const [tablaCsv, setTablaCsv] = useState('cliente');
  const [archivoCsv, setArchivoCsv] = useState<File | null>(null);
  const [migracion, setMigracion] = useState<Migracion | null>(null);
  const [ocupado, setOcupado] = useState('');
  const [exito, setExito] = useState('');
  const [error, setError] = useState('');

  async function ejecutar<T>(etiqueta: string, operacion: () => Promise<T>, terminado?: (respuesta: T) => void): Promise<T | undefined> {
    setOcupado(etiqueta); setError(''); setExito('');
    try {
      const resultado = await operacion();
      terminado?.(resultado);
      return resultado;
    } catch (e) {
      setError(mensajeError(e));
      return undefined;
    } finally {
      setOcupado('');
    }
  }

  async function actualizarBasico() {
    const [b, e] = await Promise.all([
      api<{bases_datos: string[]; seleccionada: string}>('/db/listar'),
      api<Esquema>('/ddl/estado'),
    ]);
    setBases(b.bases_datos); setSeleccionada(b.seleccionada || ''); setEsquema(e); setEstadoApi('ok');
    if (e.total_tablas >= 8) { const d = await api<{total_registros:number;puede_cargar:boolean}>('/ddl/datos-prueba/estado'); setDatosPrueba(d); } else setDatosPrueba(null);
  }

  async function actualizarUsuarios() {
    const [u, p] = await Promise.all([
      api<{usuarios: Rol[]}>('/dcl/usuarios'),
      api<{permisos: Permiso[]}>(`/dcl/permisos/${usuario}`),
    ]);
    setRoles(u.usuarios); setPermisos(p.permisos);
  }

  async function actualizarBackup() {
    const [a, config] = await Promise.all([
      api<{archivos: Archivo[]}>('/backup/listar'),
      api<BackupConfig>('/backup/configuracion'),
    ]);
    setArchivos(a.archivos); setBackupConfig(config);
    setArchivoRestore(prev => prev && a.archivos.some(x => x.nombre === prev) ? prev : a.archivos[0]?.nombre || '');
  }

  async function actualizarTransferir() {
    const t = await api<{tablas: Tabla[]}>('/transfer/tablas');
    setTablasCsv(t.tablas);
    // Si MySQL aún no está configurado, este endpoint devuelve el estado del origen.
    const m = await api<Migracion>('/transfer/migracion/estado');
    setMigracion(m);
  }

  useEffect(() => {
    void (async () => {
      try { await actualizarBasico(); }
      catch (e) { setEstadoApi('error'); setError(mensajeError(e)); }
    })();
  }, []);

  async function cambiarModulo(destino: Modulo) {
    setModulo(destino); setError(''); setExito('');
    if (destino === 'usuarios') await ejecutar('usuarios', actualizarUsuarios);
    if (destino === 'backup') await ejecutar('respaldos', actualizarBackup);
    if (destino === 'transferir') await ejecutar('importaciones', actualizarTransferir);
    if (destino === 'esquema' || destino === 'restricciones') await ejecutar('esquema', actualizarBasico);
  }

  async function refrescar() {
    if (modulo === 'usuarios') await ejecutar('usuarios', actualizarUsuarios);
    else if (modulo === 'backup') await ejecutar('respaldos', actualizarBackup);
    else if (modulo === 'transferir') await ejecutar('transferencias', actualizarTransferir);
    else await ejecutar('bases', actualizarBasico);
  }

  async function seleccionarBase() {
    const b = seleccionada;
    if (!b) return setError('Selecciona una base de datos.');
    const r = await ejecutar('seleccionar base', () => api(`/db/seleccionar/${encodeURIComponent(b)}`, { method: 'POST' }));
    if (r) { await refrescar(); setExito(`Base seleccionada: ${b}`); }
  }

  async function crearBase(e: FormEvent) {
    e.preventDefault();
    if (!/^[a-z][a-z0-9_]{2,62}$/.test(baseNueva)) return setError('Nombre inválido: usa minúsculas y guion bajo.');
    const b = baseNueva;
    const r = await ejecutar('crear base', () => api('/db/crear', { method: 'POST', body: JSON.stringify({nombre:b}) }));
    if (r) { setBaseNueva(''); await refrescar(); setExito(`Base ${b} creada y seleccionada.`); }
  }

  async function crearEsquema() {
    if (!seleccionada) return setError('Selecciona una base de datos.');
    if (!window.confirm(`¿Crear las ocho tablas y sus índices en «${seleccionada}»?\nSolo funciona si la base está vacía.`)) return;
    const r = await ejecutar('crear esquema', () => api<{mensaje:string}>('/ddl/create-all', {method:'POST'}));
    if (r) { await refrescar(); setExito(r.mensaje); }
  }

  async function cargarDatos() {
    if (!window.confirm('¿Insertar los 43 registros de prueba originales de Concesionaria? Solo en tablas vacías.')) return;
    const r = await ejecutar('datos de prueba', () => api<{mensaje:string}>('/ddl/datos-prueba', {method:'POST'}));
    if (r) { await refrescar(); setExito(r.mensaje); }
  }

  async function crearBackup() {
    const r = await ejecutar('crear respaldo', () => api<{nombre:string;bytes:number;mensaje:string}>('/backup/crear', {method:'POST'}));
    if (r) { await actualizarBackup(); setExito(`${r.mensaje} Archivo: ${r.nombre} (${r.bytes.toLocaleString()} bytes).`); }
  }

  async function restaurar() {
    if (!archivoRestore) return setError('Selecciona un respaldo.');
    if (!backupConfig?.restauracion_configurada) return setError('Configura RESTORE_DATABASE_URL en el backend.');
    const texto = window.prompt(`RESTAURACIÓN DESTRUCTIVA en ${backupConfig.base_destino} (${backupConfig.servidor_destino}).\nSe reemplazarán las tablas del destino. Escribe RESTAURAR_DESTINO:`);
    if (texto !== 'RESTAURAR_DESTINO') return;
    const r = await ejecutar('restaurar respaldo', () => api<{mensaje:string}>('/backup/restaurar', {
      method:'POST', body:JSON.stringify({nombre:archivoRestore,confirmacion:texto}),
    }));
    if (r) setExito(r.mensaje);
  }

  async function crearUsuario() {
    if (contrasena.length < 12) return setError('La contraseña debe tener al menos 12 caracteres.');
    const r = await ejecutar('crear usuario', () => api<{mensaje:string}>('/dcl/crear_usuario', {
      method:'POST', body:JSON.stringify({usuario,contrasena}),
    }));
    setContrasena('');
    if (r) { await actualizarUsuarios(); setExito(r.mensaje); }
  }

  async function permiso(accion: 'grant'|'revoke') {
    const rol = roles.find(r => r.usuario === usuario);
    if (!rol) return setError('Selecciona un rol configurado.');
    const r = await ejecutar(accion, () => api<{mensaje:string}>(`/dcl/${accion}`, {
      method:'POST', body:JSON.stringify({usuario, tabla:rol.tabla, operacion:rol.operacion}),
    }));
    if (r) { await actualizarUsuarios(); setExito(r.mensaje); }
  }

  async function cambiarUsuario(nombre: string) {
    setUsuario(nombre); setPermisos([]);
    await ejecutar('permisos', () => api<{permisos:Permiso[]}>(`/dcl/permisos/${nombre}`), r => setPermisos(r.permisos));
  }

  async function importarCsv() {
    if (!archivoCsv) return setError('Selecciona un CSV con cabeceras.');
    const r = await ejecutar('importar CSV', () => enviarArchivo<{mensaje:string;registros_importados:number}>(`/transfer/importar/${tablaCsv}`, archivoCsv));
    if (r) { setArchivoCsv(null); await actualizarTransferir(); setExito(`${r.mensaje} Filas: ${r.registros_importados}.`); }
  }

  async function exportarCsv() {
    const r = await ejecutar('exportar CSV', async () => { await descargar(`/transfer/exportar/${tablaCsv}`, `concesionaria_${tablaCsv}.csv`); return true; });
    if (r) setExito(`Archivo CSV de ${tablaCsv} descargado.`);
  }

  async function ejecutarMigracion() {
    const escrito = window.prompt('La migración requiere una base MySQL VACÍA y creará ocho tablas. Escribe MIGRAR_CONCESIONARIA:');
    if (escrito !== 'MIGRAR_CONCESIONARIA') return;
    const r = await ejecutar('migrar a MySQL', () => api<{mensaje:string;total_registros:number}>('/transfer/migracion/ejecutar', {
      method:'POST', body:JSON.stringify({confirmacion:escrito}),
    }));
    if (r) { await actualizarTransferir(); setExito(`${r.mensaje} ${r.total_registros} registros validados.`); }
  }

  const seleccionado = roles.find(r => r.usuario === usuario);
  const activo = MODULOS.find(m => m.id === modulo)!;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-3 text-white"><Database size={24}/></div>
            <div><h1 className="text-xl font-bold tracking-tight">Concesionaria · Administración de BD</h1>
              <p className="text-sm text-slate-500">Unidad 4 · PostgreSQL/Neon · MySQL · FastAPI</p></div>
          </div>
          <div className="flex items-center gap-2 rounded-full border px-3 py-2 text-sm">
            {estadoApi === 'ok' ? <CheckCircle2 size={17} className="text-emerald-600"/> : estadoApi === 'error' ? <XCircle size={17} className="text-red-600"/> : <Activity size={17}/>}
            {estadoApi === 'ok' ? 'API disponible' : estadoApi === 'error' ? 'API sin conexión' : 'Verificando API'}
          </div>
        </div>
      </header>
      <main className="mx-auto grid max-w-7xl gap-6 px-5 py-7 md:grid-cols-[235px_minmax(0,1fr)]">
        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-3">
          <p className="px-3 pb-3 pt-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Módulos</p>
          <nav className="space-y-1">{MODULOS.map(m => <button key={m.id} type="button" onClick={()=>void cambiarModulo(m.id)}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${modulo===m.id?'bg-indigo-50 text-indigo-700':'text-slate-600 hover:bg-slate-50'}`}>
            <m.icon size={19}/><span className="flex-1">{m.nombre}</span><span className="text-xs opacity-50">{m.subtitulo}</span></button>)}</nav>
          <div className="mt-5 rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-500">Base PostgreSQL seleccionada</p>
            <p className="mt-1 break-words text-sm font-semibold">{seleccionada || 'Ninguna'}</p></div>
          <p className="mt-4 px-2 text-xs leading-5 text-amber-800">Panel administrativo solo para desarrollo local. No publicar en Internet.</p>
        </aside>
        <section className="min-w-0 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div><h2 className="text-2xl font-bold">{activo.nombre}</h2><p className="mt-1 text-sm text-slate-500">Actividad {activo.subtitulo} · Concesionaria</p></div>
            <button className={cssSecondary} disabled={!!ocupado} onClick={()=>void refrescar()}><RefreshCw size={17}/>Actualizar</button>
          </div>
          {error && <div role="alert" className="flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"><AlertTriangle size={19} className="shrink-0"/><span className="flex-1 break-words">{error}</span><button onClick={()=>setError('')} aria-label="Cerrar error">×</button></div>}
          {exito && <div role="status" className="flex gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800"><CheckCircle2 size={18} className="shrink-0"/>{exito}</div>}
          {ocupado && <div className="flex items-center gap-2 text-sm text-slate-600"><LoaderCircle size={18} className="animate-spin"/>Procesando: {ocupado}...</div>}

          {modulo === 'bases' && <>
            <div className="grid gap-4 sm:grid-cols-3">
              <MiniDato titulo="Bases listadas" valor={bases.length} icon={Database}/>
              <MiniDato titulo="Tablas en public" valor={esquema?.total_tablas ?? '—'} icon={Table2}/>
              <MiniDato titulo="Estado" valor={estadoApi === 'ok' ? 'Conectada' : 'Sin verificar'} icon={Server}/>
            </div>
            <div className="grid gap-5 xl:grid-cols-2">
              <article className={cssBox}><h3 className="font-semibold">Seleccionar base de datos</h3>
                <p className="mt-2 text-sm text-slate-500">La selección afecta a las consultas, respaldos y operaciones administrativas.</p>
                <label className="mt-4 block text-sm font-medium">Bases disponibles</label>
                <select className={`mt-2 ${cssInput}`} value={seleccionada} onChange={e=>setSeleccionada(e.target.value)}>
                  <option value="">Selecciona una base</option>{bases.map(b=><option key={b} value={b}>{b}</option>)}
                </select><button disabled={!!ocupado || !seleccionada} className={`mt-4 w-full ${cssPrimary}`} onClick={()=>void seleccionarBase()}>Seleccionar base</button>
              </article>
              <article className={cssBox}><h3 className="font-semibold">Crear base de prácticas</h3>
                <p className="mt-2 text-sm text-slate-500">Requiere permiso CREATEDB en PostgreSQL. Neon puede limitarlo.</p>
                <form className="mt-4 space-y-3" onSubmit={e=>void crearBase(e)}>
                  <label className="block text-sm font-medium">Nombre nuevo</label>
                  <input className={cssInput} value={baseNueva} onChange={e=>setBaseNueva(e.target.value)} placeholder="concesionaria_prueba"/>
                  <button disabled={!!ocupado || !baseNueva.trim()} className={`w-full ${cssPrimary}`} type="submit"><Plus size={17}/>Crear base</button>
                </form>
              </article>
            </div>
          </>}

          {modulo === 'esquema' && <>
            <div className="grid gap-4 sm:grid-cols-3"><MiniDato titulo="Tablas" valor={esquema?.total_tablas ?? 0} icon={Table2}/>
              <MiniDato titulo="Restricciones" valor={esquema?.total_restricciones ?? 0} icon={ShieldCheck}/>
              <MiniDato titulo="Índices" valor={esquema?.total_indices ?? 0} icon={Database}/></div>
            <article className={cssBox}><h3 className="font-semibold">Crear esquema completo de Concesionaria</h3>
              <p className="mt-2 text-sm text-slate-500">Crea las ocho tablas y ocho índices explícitos. No inserta datos de prueba. Solo en una base completamente vacía.</p>
              <button className={`mt-4 ${cssPrimary}`} disabled={!!ocupado || !seleccionada || (esquema?.total_tablas ?? 0)>0} onClick={()=>void crearEsquema()}><Plus size={17}/>Crear las 8 tablas</button>
              {(esquema?.total_tablas ?? 0)>0 && <p className="mt-2 text-xs text-amber-700">La base ya contiene tablas; la creación está bloqueada para evitar duplicados.</p>}
              <div className="mt-5 border-t border-slate-200 pt-4">
                <h4 className="font-semibold">Insertar datos de prueba del SQL original</h4>
                <p className="mt-2 text-sm text-slate-500">43 registros repartidos entre las ocho tablas (clientes, coches, proveedores, órdenes, etc.).</p>
                <button className={`mt-3 ${cssSecondary}`} disabled={!!ocupado || !datosPrueba?.puede_cargar} onClick={()=>void cargarDatos()}><Plus size={16}/>Cargar los 43 registros</button>
                {datosPrueba && <p className="mt-2 text-xs text-slate-500">Registros actuales: {datosPrueba.total_registros}. {datosPrueba.puede_cargar ? 'Listo para cargar.' : 'No se cargan duplicados.'}</p>}
              </div>
            </article>
            <article className={cssBox}><h3 className="mb-4 font-semibold">Tablas detectadas</h3>
              {esquema?.tablas.length ? <div className="grid gap-2 sm:grid-cols-2">{esquema.tablas.map(t=><div key={t} className="flex items-center gap-2 rounded-xl border p-3 text-sm"><Table2 size={17} className="text-indigo-600"/>{t}</div>)}</div>
              : <p className="text-sm text-slate-500">No hay tablas. Selecciona una base vacía y crea el esquema.</p>}</article>
          </>}

          {modulo === 'restricciones' && <>
            <div className="grid gap-4 sm:grid-cols-2"><MiniDato titulo="Restricciones" valor={esquema?.total_restricciones ?? 0} icon={ShieldCheck}/>
              <MiniDato titulo="Índices" valor={esquema?.total_indices ?? 0} icon={Database}/></div>
            <article className={cssBox}><h3 className="mb-3 font-semibold">Claves y restricciones (PK, FK, UNIQUE, CHECK)</h3>
              <div className="max-h-96 overflow-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b text-slate-500"><th className="p-2">Tabla</th><th className="p-2">Restricción</th><th className="p-2">Tipo</th></tr></thead>
                <tbody>{(esquema?.restricciones ?? []).map(r=><tr key={`${r.table_name}-${r.constraint_name}`} className="border-b border-slate-100"><td className="p-2">{r.table_name}</td><td className="p-2 font-mono text-xs">{r.constraint_name}</td><td className="p-2">{r.constraint_type}</td></tr>)}</tbody></table></div>
            </article>
            <article className={cssBox}><h3 className="mb-3 font-semibold">Índices</h3>
              <div className="grid gap-2 sm:grid-cols-2">{(esquema?.indices ?? []).map(x=><div className="rounded-lg bg-slate-50 p-3 text-xs" key={x.indexname}><strong className="block font-mono">{x.indexname}</strong><span className="text-slate-500">{x.tablename}</span></div>)}</div>
            </article>
          </>}

          {modulo === 'backup' && <>
            <div className="grid gap-5 xl:grid-cols-2">
              <article className={cssBox}><h3 className="flex items-center gap-2 font-semibold"><FileArchive size={19}/>Crear respaldo PostgreSQL</h3>
                <p className="mt-2 text-sm text-slate-500">Origen: {backupConfig?.servidor_origen || '—'} / {backupConfig?.base_origen || '—'}. Formato comprimido .backup (pg_dump).</p>
                <p className="mt-2 text-xs text-slate-500">Herramienta pg_dump: {backupConfig?.pg_dump_disponible ? 'detectada' : 'configurar PG_DUMP_PATH'}</p>
                <button disabled={!!ocupado} className={`mt-4 ${cssPrimary}`} onClick={()=>void crearBackup()}><FileDown size={18}/>Crear respaldo</button>
              </article>
              <article className={cssBox}><h3 className="flex items-center gap-2 font-semibold"><HardDrive size={19}/>Restaurar en PostgreSQL de prácticas</h3>
                <p className="mt-2 break-words text-sm text-slate-500">Destino: {backupConfig?.restauracion_configurada ? `${backupConfig.servidor_destino}/${backupConfig.base_destino}` : 'RESTORE_DATABASE_URL sin configurar'}</p>
                <p className="mt-2 text-xs text-amber-700">La restauración limpia objetos existentes del DESTINO y requiere confirmación escrita.</p>
                <label className="mt-3 block text-sm font-medium">Archivo guardado</label>
                <select className={`mt-2 ${cssInput}`} value={archivoRestore} onChange={e=>setArchivoRestore(e.target.value)}>
                  <option value="">Selecciona un respaldo</option>{archivos.map(a=><option key={a.nombre} value={a.nombre}>{a.nombre}</option>)}
                </select>
                <button disabled={!!ocupado || !backupConfig?.restauracion_configurada || !archivoRestore} className={`mt-4 ${cssSecondary}`} onClick={()=>void restaurar()}><Upload size={17}/>Restaurar respaldo</button>
              </article>
            </div>
            <article className={cssBox}><h3 className="mb-3 font-semibold">Respaldos generados</h3>
              {!archivos.length && <p className="text-sm text-slate-500">No hay respaldos todavía.</p>}
              <div className="space-y-2">{archivos.map(a=><div key={a.nombre} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border p-3">
                <div className="min-w-0"><p className="break-all font-mono text-xs font-medium">{a.nombre}</p><p className="text-xs text-slate-500">{(a.bytes/1024).toFixed(1)} KB · {new Date(a.fecha).toLocaleString()}</p></div>
                <button className={cssSecondary} disabled={!!ocupado} onClick={()=>void ejecutar('descargar respaldo',()=>descargar(`/backup/descargar/${a.nombre}`,a.nombre))}><Download size={16}/>Descargar</button>
              </div>)}</div>
            </article>
          </>}

          {modulo === 'usuarios' && <>
            <div className="grid gap-5 xl:grid-cols-2">
              <article className={cssBox}><h3 className="font-semibold">Crear rol de PostgreSQL</h3>
                <p className="mt-2 text-sm text-slate-500">Configuración basada en los 15 usuarios del ejercicio 4.5.</p>
                <label className="mt-4 block text-sm font-medium">Usuario</label>
                <select className={`mt-2 ${cssInput}`} value={usuario} onChange={e=>void cambiarUsuario(e.target.value)}>
                  {roles.map(u=><option key={u.usuario} value={u.usuario}>{u.usuario} {u.existe ? '✓' : '· pendiente'}</option>)}
                </select>
                <label className="mt-4 block text-sm font-medium">Contraseña del nuevo rol (mínimo 12 caracteres)</label>
                <input className={`mt-2 ${cssInput}`} type="password" autoComplete="new-password" value={contrasena} onChange={e=>setContrasena(e.target.value)} placeholder="Contraseña solo para crear el rol"/>
                <button className={`mt-4 ${cssPrimary}`} disabled={!!ocupado || !!seleccionado?.existe || contrasena.length<12} onClick={()=>void crearUsuario()}><Plus size={17}/>Crear usuario y GRANT USAGE</button>
              </article>
              <article className={cssBox}><h3 className="font-semibold">Conceder y revocar permisos</h3>
                {seleccionado ? <>
                  <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm"><p><strong>Rol:</strong> {seleccionado.usuario}</p>
                    <p className="mt-2"><strong>Tabla:</strong> {seleccionado.tabla}</p><p className="mt-2"><strong>Operación:</strong> {seleccionado.operacion}</p></div>
                  <div className="mt-4 flex flex-wrap gap-2"><button className={cssPrimary} disabled={!!ocupado || !seleccionado.existe} onClick={()=>void permiso('grant')}>GRANT</button>
                    <button className={cssSecondary} disabled={!!ocupado || !seleccionado.existe} onClick={()=>void permiso('revoke')}>REVOKE</button></div>
                  <h4 className="mt-5 font-semibold">Permisos actuales</h4>
                  {permisos.length ? <div className="mt-2 space-y-2">{permisos.map((p,i)=><p className="rounded-lg bg-slate-50 p-3 text-xs" key={`${p.table_name}-${p.privilege_type}-${i}`}>{p.privilege_type} · {p.table_name}</p>)}</div>
                  : <p className="mt-2 text-sm text-slate-500">No hay permisos directos detectados.</p>}
                </> : <p className="mt-4 text-sm text-slate-500">Selecciona un rol para ver sus permisos.</p>}
              </article>
            </div>
            <article className={cssBox}><h3 className="mb-3 font-semibold">Usuarios esperados (15)</h3>
              <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">{roles.map(r=><button key={r.usuario} onClick={()=>void cambiarUsuario(r.usuario)}
                className={`rounded-xl border p-3 text-left text-sm ${usuario===r.usuario ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:bg-slate-50'}`}>
                <strong className="block">{r.usuario}</strong><span className="text-xs text-slate-500">{r.tabla} · {r.operacion}</span>
                <span className={`mt-2 block text-xs ${r.existe?'text-emerald-700':'text-amber-700'}`}>{r.existe?'Creado':'Pendiente'}</span>
              </button>)}</div>
            </article>
          </>}

          {modulo === 'transferir' && <>
            <div className="grid gap-5 xl:grid-cols-2">
              <article className={cssBox}><h3 className="flex items-center gap-2 font-semibold"><FileDown size={19}/>Exportar datos CSV</h3>
                <p className="mt-2 text-sm text-slate-500">Descarga las filas de una tabla PostgreSQL con sus encabezados.</p>
                <label className="mt-4 block text-sm font-medium">Tabla</label>
                <select value={tablaCsv} onChange={e=>{setTablaCsv(e.target.value);setArchivoCsv(null);}} className={`mt-2 ${cssInput}`}>
                  {tablasCsv.map(t=><option key={t.nombre} value={t.nombre}>{t.nombre} ({t.registros} filas)</option>)}
                </select>
                <button className={`mt-4 ${cssPrimary}`} disabled={!!ocupado || !tablasCsv.find(t=>t.nombre===tablaCsv)?.existe} onClick={()=>void exportarCsv()}><Download size={17}/>Exportar CSV</button>
              </article>
              <article className={cssBox}><h3 className="flex items-center gap-2 font-semibold"><FileUp size={19}/>Importar datos CSV</h3>
                <p className="mt-2 text-sm text-slate-500">Carga datos a la tabla seleccionada. Una transacción revierte filas si hay PK/FK/CHECK inválidos. Para evitar duplicados, importa primero a tablas vacías.</p>
                <label className="mt-4 block text-sm font-medium">Archivo con columnas válidas de {tablaCsv}</label>
                <input className={`mt-2 ${cssInput}`} type="file" accept=".csv,text/csv" onChange={e=>setArchivoCsv(e.target.files?.[0]??null)}/>
                <button className={`mt-4 ${cssPrimary}`} disabled={!!ocupado || !archivoCsv} onClick={()=>void importarCsv()}><Upload size={17}/>Importar CSV</button>
              </article>
            </div>
            <article className={cssBox}><h3 className="flex items-center gap-2 font-semibold"><ArrowRightLeft size={19}/>Migración PostgreSQL → MySQL 8</h3>
              <p className="mt-2 text-sm text-slate-500">Convierte el esquema y transfiere los registros respetando el orden de claves foráneas. El destino MySQL debe ser una base nueva, sin tablas.</p>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs text-slate-500">Origen PostgreSQL</p><p className="mt-1 break-words font-semibold">{migracion?.origen.base||'—'}</p>
                  <p className="mt-2 text-xs text-slate-600">{Object.values(migracion?.origen.tablas??{}).reduce<number>((acc,n)=>acc+(n??0),0)} registros en tablas configuradas</p></div>
                <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs text-slate-500">Destino MySQL</p><p className="mt-1 break-words font-semibold">{migracion?.destino?.base??(migracion?.mysql_configurado?'Sin verificar':'MYSQL_URL no configurada')}</p>
                  <p className="mt-2 text-xs text-slate-600">{migracion?.destino?.tablas_existentes.length??0} tablas ya existentes</p></div>
              </div>
              <p className="mt-4 text-xs text-amber-700">Se requiere MySQL 8.0.16+ (restricciones CHECK). Si la migración falla a mitad de camino, crea otra base de destino vacía para reintentar.</p>
              <button className={`mt-4 ${cssPrimary}`} disabled={!!ocupado || !migracion?.mysql_configurado || (migracion?.destino?.tablas_existentes.length??0)>0}
                onClick={()=>void ejecutarMigracion()}><ArrowRightLeft size={17}/>Migrar las 8 tablas a MySQL</button>
            </article>
            <article className={cssBox}><h3 className="mb-3 font-semibold">Conteo comparativo de registros</h3>
              <div className="max-w-full overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b text-slate-500"><th className="p-2">Tabla</th><th className="p-2">PostgreSQL</th><th className="p-2">MySQL</th></tr></thead>
                <tbody>{tablasCsv.map(t=><tr key={t.nombre} className="border-b border-slate-100"><td className="p-2 font-medium">{t.nombre}</td><td className="p-2">{t.existe ? t.registros : 'No existe'}</td><td className="p-2">{migracion?.destino?.tablas[t.nombre] ?? '—'}</td></tr>)}</tbody>
              </table></div>
            </article>
          </>}
          <footer className="border-t border-slate-200 py-4 text-xs text-slate-500">Panel académico Concesionaria · Solo localhost · API {import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}</footer>
        </section>
      </main>
    </div>
  );
}

function MiniDato({titulo, valor, icon: Icon}: {titulo:string; valor:number|string;icon: typeof Database}) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-5"><div className="flex justify-between"><p className="text-sm text-slate-500">{titulo}</p><Icon className="text-indigo-600" size={20}/></div>
    <p className="mt-3 text-2xl font-bold">{valor}</p></div>;
}
