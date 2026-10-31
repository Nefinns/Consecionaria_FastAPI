import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { consultarUsuario, crearUsuario, listarUsuarios, modificarUsuario, roles,
  type ListaUsuarios, type RolUsuario, type UsuarioInterno, type UsuarioModificar, type UsuarioPerfil } from '@/services/usuarios';

const message = (error: unknown) => error instanceof Error ? error.message : 'No se pudo completar la operación.';

export function Usuarios() {
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [data, setData] = useState<ListaUsuarios>();
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    listarUsuarios(offset, 20, controller.signal).then(result => {
      if (!controller.signal.aborted) setData(result);
    }).catch(e => { if (!controller.signal.aborted) setError(message(e)); });
    return () => controller.abort();
  }, [offset, revision]);
  return <>
    <div className="page-heading"><div><p className="eyebrow">ADMINISTRACIÓN</p><h1>Usuarios internos</h1><p>Controla quién puede acceder y con qué permisos.</p></div>
      <Link className="action-link" to="/usuarios/nuevo">+ Vincular usuario</Link></div>
    <section className="panel">
      <div className="section-heading"><h2>Directorio del equipo</h2><Button variant="outline" onClick={() => { setData(undefined); setError(''); setRevision(v => v + 1); }}>Actualizar</Button></div>
      {error ? <div role="alert" className="notice error">{error}<Button variant="outline" onClick={() => { setError(''); setRevision(v => v + 1); }}>Reintentar</Button></div> : !data ?
        <p role="status">Cargando usuarios…</p> : <>
        <p className="muted">{data.total} usuarios registrados · {data.total === 0 ? 'Sin resultados' : `Mostrando ${offset + 1}–${Math.min(offset + 20, data.total)}`}</p>
        {data.usuarios.length ? <div className="table-scroll"><table><caption className="sr-only">Usuarios internos y permisos</caption><thead><tr><th>Usuario</th><th>Rol</th><th>Estado</th><th><span className="sr-only">Acciones</span></th></tr></thead>
          <tbody>{data.usuarios.map(u => <tr key={u.id_usuario}><td><strong>{u.nombre}</strong><small>Usuario #{u.id_usuario}</small></td><td>{roles[u.rol]}</td><td><span className={`status ${u.activo ? '' : 'inactive'}`}>{u.activo ? 'Activo' : 'Inactivo'}</span></td><td><Link className="text-link" to={`/usuarios/${u.id_usuario}`} aria-label={`Consultar y editar a ${u.nombre}`}>Ver detalle →</Link></td></tr>)}</tbody></table></div> : <div className="empty"><h3>No hay usuarios en esta página</h3><p>Vincula una identidad registrada para dar acceso al equipo.</p></div>}
        <div className="pagination"><Button variant="outline" disabled={offset === 0} onClick={() => { setData(undefined); setOffset(v => Math.max(0, v - 20)); }}>Anterior</Button><span>Página {Math.floor(offset / 20) + 1}</span><Button variant="outline" disabled={offset + 20 >= data.total} onClick={() => { setData(undefined); setOffset(v => v + 20); }}>Siguiente</Button></div>
      </>}
    </section>
  </>;
}

export function UsuarioEditor({ actual }: { actual: UsuarioPerfil }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const nuevo = id === undefined;
  const [original, setOriginal] = useState<UsuarioInterno>();
  const [nombre, setNombre] = useState('');
  const [identidad, setIdentidad] = useState('');
  const [rol, setRol] = useState<RolUsuario>('mecanico');
  const [activo, setActivo] = useState(true);
  const [loading, setLoading] = useState(!nuevo);
  const [busy, setBusy] = useState(false);
  const saving = useRef(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState('');
  const [revision, setRevision] = useState(0);
  const [confirm, setConfirm] = useState(false);
  const propio = original?.id_usuario === actual.id_usuario;
  useEffect(() => {
    if (nuevo) return;
    const controller = new AbortController();
    if (!/^\d+$/.test(id!) || !Number.isSafeInteger(Number(id)) || Number(id) < 1) {
      setError('El identificador del usuario no es válido.'); setLoading(false); return;
    }
    consultarUsuario(Number(id), controller.signal).then(u => {
      if (controller.signal.aborted) return;
      setOriginal(u); setNombre(u.nombre); setRol(u.rol); setActivo(u.activo); setIdentidad(u.identidad_externa);
    }).catch(e => { if (!controller.signal.aborted) setError(message(e)); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [id, nuevo, revision]);

  const cambios: UsuarioModificar = {};
  if (original) {
    if (nombre.trim() !== original.nombre) cambios.nombre = nombre.trim();
    if (rol !== original.rol) cambios.rol = rol;
    if (activo !== original.activo) cambios.activo = activo;
  }
  async function guardar() {
    if (saving.current) return;
    saving.current = true; setBusy(true); setError(''); setSaved('');
    try {
      const u = nuevo ? await crearUsuario({ nombre: nombre.trim(), identidad_externa: identidad.trim(), rol }) :
        await modificarUsuario(original!.id_usuario, cambios);
      if (nuevo) navigate(`/usuarios/${u.id_usuario}`, { replace: true });
      else {
        setOriginal(u); setNombre(u.nombre); setRol(u.rol); setActivo(u.activo);
        setSaved('Cambios guardados.');
        window.dispatchEvent(new Event('autogest:access-changed'));
      }
    } catch (e) { setError(message(e)); }
    finally { saving.current = false; setBusy(false); setConfirm(false); }
  }
  function submit(e: FormEvent) {
    e.preventDefault();
    if (!nombre.trim() || (nuevo && !identidad.trim())) { setError('Completa los campos sin utilizar solo espacios.'); return; }
    if (!nuevo && !Object.keys(cambios).length) return;
    if (original && (cambios.rol !== undefined || cambios.activo !== undefined)) setConfirm(true);
    else void guardar();
  }
  return <>
    <Link className="text-link" to="/usuarios">← Volver al directorio</Link>
    <div className="page-heading"><div><p className="eyebrow">ADMINISTRACIÓN</p><h1>{nuevo ? 'Vincular usuario' : 'Detalle del usuario'}</h1><p>{nuevo ? 'Autoriza una cuenta que ya existe en SuperTokens.' : 'Consulta y actualiza el acceso de tu equipo.'}</p></div></div>
    <section className="panel editor">
      {loading ? <p role="status">Consultando usuario…</p> : <>
        {error && <p role="alert" className="notice error">{error}</p>}
        {saved && <p role="status" className="notice">{saved}</p>}
        {(!nuevo && !original) ? <Button onClick={() => { setLoading(true); setError(''); setRevision(v => v + 1); }}>Reintentar consulta</Button> : <form onSubmit={submit}>
          <fieldset disabled={busy}>
            <label htmlFor="nombre">Nombre completo<Input id="nombre" autoComplete="name" value={nombre} onChange={e => setNombre(e.target.value)} required maxLength={120} /></label>
            <label htmlFor="identidad">Identidad externa<Input id="identidad" value={identidad} onChange={e => setIdentidad(e.target.value)} required maxLength={255} readOnly={!nuevo} aria-describedby="identidad-ayuda" /></label>
            <p id="identidad-ayuda" className="muted">{nuevo ? 'Usa el identificador de la cuenta registrada en SuperTokens. No es el correo ni una contraseña.' : 'La identidad vinculada no se puede cambiar.'}</p>
            <label htmlFor="rol">Rol<select id="rol" value={rol} disabled={propio} onChange={e => setRol(e.target.value as RolUsuario)}>{Object.entries(roles).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
            {!nuevo && <label className="check-label"><input type="checkbox" checked={activo} disabled={propio} onChange={e => setActivo(e.target.checked)} />Acceso activo</label>}
            {propio && <p className="muted">Puedes actualizar tu nombre. No puedes quitarte permisos ni desactivar tu propia cuenta.</p>}
            {nuevo && <p className="notice">El usuario se vinculará con acceso activo. Esta acción no crea ni cambia su contraseña.</p>}
            <div className="actions"><Button type="submit" disabled={busy || (!nuevo && !Object.keys(cambios).length)}>{busy ? 'Guardando…' : nuevo ? 'Vincular usuario' : 'Guardar cambios'}</Button><Link to="/usuarios" className="text-link">Volver al listado</Link></div>
          </fieldset>
        </form>}
      </>}
    </section>
    <Dialog open={confirm} onOpenChange={open => { if (!busy) setConfirm(open); }}>
      <DialogContent showCloseButton={false}><DialogTitle>Confirmar cambio de acceso</DialogTitle><DialogDescription>Se actualizarán los permisos de {nombre}. El cambio se aplicará a sus próximas solicitudes.</DialogDescription>
        <p>Rol: <strong>{roles[rol]}</strong> · Estado: <strong>{activo ? 'Activo' : 'Inactivo'}</strong></p>
        <div className="actions"><Button disabled={busy} onClick={() => void guardar()}>{busy ? 'Guardando…' : 'Confirmar cambios'}</Button><Button variant="outline" disabled={busy} onClick={() => setConfirm(false)}>Cancelar</Button></div>
      </DialogContent>
    </Dialog>
  </>;
}
