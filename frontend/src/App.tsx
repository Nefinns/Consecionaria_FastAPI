import { useEffect, useState } from 'react';
import { BrowserRouter, Link, NavLink, Navigate, Outlet, Route, Routes, useLocation, useOutletContext } from 'react-router-dom';
import * as reactRouterDom from 'react-router-dom';
import { SuperTokensWrapper } from 'supertokens-auth-react';
import { SessionAuth } from 'supertokens-auth-react/recipe/session';
import { getSuperTokensRoutesForReactRouterDom } from 'supertokens-auth-react/ui';
import { EmailPasswordPreBuiltUI } from 'supertokens-auth-react/recipe/emailpassword/prebuiltui';
import { LayoutDashboard, Users, UserRound, ArrowUpRight, ShieldCheck, CarFront } from 'lucide-react';
import UsuarioAutorizado from '@/components/auth/UsuarioAutorizado';
import Salir from '@/components/auth/Salir';
import { Button } from '@/components/ui/button';
import { roles, request, type UsuarioPerfil } from '@/services/usuarios';
import { Usuarios, UsuarioEditor } from '@/pages/Usuarios';

function Shell({ usuario }: { usuario: UsuarioPerfil }) {
  const location = useLocation();
  useEffect(() => {
    document.title = `${location.pathname.startsWith('/usuarios') ? 'Usuarios' : location.pathname === '/perfil' ? 'Mi perfil' : 'Inicio'} · AutoGest`;
    document.getElementById('contenido')?.focus();
  }, [location.pathname]);
  return <div className="app-shell">
    <a className="skip-link" href="#contenido">Saltar al contenido</a>
    <aside className="sidebar"><Link className="brand" to="/dashboard"><CarFront aria-hidden="true" />Auto<span>Gest</span></Link><p className="sidebar-label">GESTIÓN DE CONCESIONARIA</p>
      <nav aria-label="Navegación principal"><NavLink to="/dashboard"><LayoutDashboard aria-hidden="true" />Inicio</NavLink>{usuario.rol === 'administrador' && <NavLink to="/usuarios"><Users aria-hidden="true" />Usuarios internos</NavLink>}<NavLink to="/perfil"><UserRound aria-hidden="true" />Mi perfil</NavLink></nav>
      <div className="sidebar-footer"><ShieldCheck aria-hidden="true" /><p>Tu espacio de trabajo<small>Acceso según tus permisos</small></p></div>
    </aside>
    <div className="workspace"><header className="topbar"><div><span className="avatar">{usuario.nombre.slice(0, 1).toUpperCase()}</span><div><strong>{usuario.nombre}</strong><small>{roles[usuario.rol]}</small></div></div><Salir /></header>
      <main id="contenido" tabIndex={-1}><Outlet context={usuario} /></main><footer className="footer">AutoGest <span>Personas, permisos y control.</span></footer>
    </div>
  </div>;
}

function EstadoServicios() {
  const [revision, setRevision] = useState(0);
  const [states, setStates] = useState<Record<string, string>>({});
  useEffect(() => {
    const controller = new AbortController();
    for (const [key, path] of [['API', '/health'], ['Base de datos', '/health/db'], ['Autenticación', '/health/auth']]) {
      request<{ status: string }>(path, { signal: controller.signal }).then(r => {
        if (!controller.signal.aborted) setStates(v => ({ ...v, [key]: r.status === 'ok' ? 'Disponible' : 'No disponible' }));
      }).catch(() => { if (!controller.signal.aborted) setStates(v => ({ ...v, [key]: 'Sin conexión' })); });
    }
    return () => controller.abort();
  }, [revision]);
  return <section className="panel"><div className="section-heading"><h2>Estado de los servicios</h2><Button variant="outline" onClick={() => { setStates({}); setRevision(v => v + 1); }}>Comprobar</Button></div>
    <div className="service-grid" aria-live="polite">{['API', 'Base de datos', 'Autenticación'].map(key => <div key={key}><span className={`dot ${states[key] === 'Disponible' ? 'online' : ''}`} /><strong>{key}</strong><small>{states[key] ?? 'Comprobando…'}</small></div>)}</div>
  </section>;
}
function Dashboard() {
  const usuario = useOutletContext<UsuarioPerfil>();
  const admin = usuario.rol === 'administrador';
  return <>
    <div className="page-heading"><div><p className="eyebrow">TU ESPACIO DE TRABAJO</p><h1>Hola, {usuario.nombre.split(' ')[0]}.</h1><p>Bienvenido a AutoGest. Tu equipo, conectado.</p></div><span className="status">Acceso activo</span></div>
    <section className="welcome"><div><p className="eyebrow">{roles[usuario.rol]}</p><h2>{admin ? 'Un equipo bien organizado empieza aquí.' : usuario.rol === 'gerente' ? 'Tu espacio para dirigir con claridad.' : 'Listo para una nueva jornada.'}</h2><p>{admin ? 'Administra las cuentas internas y asigna el acceso que necesita cada persona.' : 'Consulta tu perfil y los permisos asociados a tu cuenta.'}</p><Link className="light-link" to={admin ? '/usuarios' : '/perfil'}>{admin ? 'Gestionar usuarios' : 'Consultar mi perfil'}<ArrowUpRight aria-hidden="true" /></Link></div><div className="welcome-art" aria-hidden="true"><CarFront /><span>AUTOGEST</span></div></section>
    <div className="dashboard-grid"><section className="panel"><p className="eyebrow">ACCESO DISPONIBLE</p><h2>{admin ? 'Gestión de usuarios' : 'Mi cuenta'}</h2><p>{admin ? 'Vincula identidades existentes, consulta el directorio y modifica roles o estados.' : `Tu rol es ${roles[usuario.rol].toLowerCase()}. Puedes consultar tu perfil y cerrar tu sesión.`}</p><Link className="text-link" to={admin ? '/usuarios' : '/perfil'}>Abrir <ArrowUpRight aria-hidden="true" /></Link></section><section className="panel"><p className="eyebrow">MÓDULOS DEL NEGOCIO</p><h2>Más funciones, próximamente</h2><p>Clientes, vehículos, ventas y taller todavía no están disponibles en esta versión.</p><span className="status inactive">Sin operaciones habilitadas</span></section></div>
    {admin && <EstadoServicios />}
  </>;
}
function Perfil() {
  const usuario = useOutletContext<UsuarioPerfil>();
  return <><div className="page-heading"><div><p className="eyebrow">MI CUENTA</p><h1>Mi perfil</h1><p>La información de tu acceso a AutoGest.</p></div></div><section className="panel editor"><dl className="profile"><div><dt>Nombre</dt><dd>{usuario.nombre}</dd></div><div><dt>Identificador interno</dt><dd>#{usuario.id_usuario}</dd></div><div><dt>Rol</dt><dd>{roles[usuario.rol]}</dd></div><div><dt>Estado</dt><dd><span className="status">Activo</span></dd></div></dl><p className="notice">Para cambiar tu nombre o permisos, solicita ayuda a un administrador.</p></section></>;
}
function AdminPage({ editor = false }: { editor?: boolean }) {
  const usuario = useOutletContext<UsuarioPerfil>();
  const location = useLocation();
  if (usuario.rol !== 'administrador') return <section className="panel"><h1>Acceso restringido</h1><p>Solo un administrador puede gestionar los usuarios internos.</p><Link className="text-link" to="/dashboard">Volver al inicio</Link></section>;
  return editor ? <UsuarioEditor key={location.pathname} actual={usuario} /> : <Usuarios />;
}
function AuthLayout() {
  return <div className="auth-layout"><section className="auth-intro"><Link className="brand" to="/">Auto<span>Gest</span></Link><p className="eyebrow">GESTIÓN DE CONCESIONARIA</p><h1>Todo comienza con un buen equipo.</h1><p>Accede a tu espacio de trabajo con seguridad y claridad.</p><CarFront className="auth-car" aria-hidden="true" /><small>El registro de una cuenta requiere autorización interna para acceder.</small></section><main className="auth-form"><Outlet /></main></div>;
}
export default function App() {
  return <SuperTokensWrapper><BrowserRouter><Routes>
    <Route element={<AuthLayout />}>{getSuperTokensRoutesForReactRouterDom(reactRouterDom, [EmailPasswordPreBuiltUI])}</Route>
    <Route element={<SessionAuth><UsuarioAutorizado>{usuario => <Shell usuario={usuario} />}</UsuarioAutorizado></SessionAuth>}>
      <Route index element={<Navigate to="/dashboard" replace />} /><Route path="dashboard" element={<Dashboard />} /><Route path="perfil" element={<Perfil />} />
      <Route path="usuarios" element={<AdminPage />} /><Route path="usuarios/nuevo" element={<AdminPage editor />} /><Route path="usuarios/:id" element={<AdminPage editor />} />
      <Route path="*" element={<section className="panel"><h1>Página no encontrada</h1><Link className="text-link" to="/dashboard">Volver al inicio</Link></section>} />
    </Route>
  </Routes></BrowserRouter></SuperTokensWrapper>;
}
