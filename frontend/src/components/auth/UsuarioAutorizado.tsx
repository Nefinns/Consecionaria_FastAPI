import { useEffect, useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ACCESS_EVENT, ApiError, obtenerUsuarioActual, type UsuarioPerfil } from '@/services/usuarios';
import { Button } from '@/components/ui/button';
import Salir from './Salir';

type Estado = { tipo: 'cargando' } | { tipo: 'ok'; usuario: UsuarioPerfil } |
{ tipo: 'denegado' | 'sesion' | 'error'; mensaje: string };

export default function UsuarioAutorizado({ children }: { children: (usuario: UsuarioPerfil) => ReactNode }) {
  const [estado, setEstado] = useState<Estado>({ tipo: 'cargando' });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let checking = false;
    async function verificar() {
      if (checking) return;
      checking = true;
      try {
        const usuario = await obtenerUsuarioActual(controller.signal);
        if (!controller.signal.aborted) setEstado(usuario.activo ? { tipo: 'ok', usuario } :
          { tipo: 'denegado', mensaje: 'Solicita al administrador que revise tu autorización.' });
      } catch (error) {
        if (controller.signal.aborted) return;
        const status = error instanceof ApiError ? error.status : 0;
        setEstado({
          tipo: status === 401 ? 'sesion' : status === 403 ? 'denegado' : 'error',
          mensaje: status === 403 ? 'Tu cuenta todavía no está habilitada o fue desactivada. Solicita al administrador que revise tu acceso.' :
            error instanceof Error ? error.message : 'No se pudo verificar el acceso.'
        });
      } finally { checking = false; }
    }
    void verificar();
    const refresh = () => { if (!document.hidden) void verificar(); };
    window.addEventListener('focus', refresh);
    window.addEventListener(ACCESS_EVENT, refresh);
    const timer = window.setInterval(refresh, 60000);
    return () => { controller.abort(); clearInterval(timer); window.removeEventListener('focus', refresh); window.removeEventListener(ACCESS_EVENT, refresh); };
  }, [revision]);

  if (estado.tipo === 'ok') return children(estado.usuario);
  return <main className="access-screen"><section className="panel access-card">
    <Link className="brand" to="/dashboard">Auto<span>Gest</span></Link>
    <p className="eyebrow">ACCESO AL SISTEMA</p>
    <h1>{estado.tipo === 'cargando' ? 'Verificando tu acceso…' : estado.tipo === 'denegado' ? 'Acceso no habilitado' : estado.tipo === 'sesion' ? 'Sesión finalizada' : 'No pudimos verificar tu acceso'}</h1>
    {estado.tipo === 'cargando' ? <p role="status">Consultando tus permisos.</p> : <>
      <p role="alert">{estado.mensaje}</p>
      <div className="actions">{estado.tipo === 'sesion' ? <Link className="action-link" to="/auth">Iniciar sesión</Link> :
        <Button onClick={() => { setEstado({ tipo: 'cargando' }); setRevision(v => v + 1); }}>Volver a comprobar</Button>}<Salir /></div>
    </>}
  </section></main>;
}
