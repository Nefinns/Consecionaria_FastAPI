import { API_URL } from '@/config/api';

export type RolUsuario = 'administrador' | 'gerente' | 'mecanico';
export const roles: Record<RolUsuario, string> = {
  administrador: 'Administrador', gerente: 'Gerente', mecanico: 'Mecánico',
};
export interface UsuarioPerfil {
  id_usuario: number;
  nombre: string;
  rol: RolUsuario;
  activo: boolean;
}
export interface UsuarioInterno extends UsuarioPerfil { identidad_externa: string }
export interface ListaUsuarios { usuarios: UsuarioInterno[]; total: number }
export type UsuarioCrear = Pick<UsuarioInterno, 'identidad_externa' | 'nombre' | 'rol'>;
export type UsuarioModificar = Partial<Pick<UsuarioInterno, 'nombre' | 'rol' | 'activo'>>;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message); this.name = 'ApiError'; this.status = status;
  }
}

export const ACCESS_EVENT = 'autogest:access-changed';
// SuperTokens intercepts fetch: it attaches headers and renews expired sessions.
// Do not copy tokens into application state, logs, or a second storage mechanism.
export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init, cache: 'no-store',
      headers: { Accept: 'application/json', ...(init.body ? { 'Content-Type': 'application/json' } : {}), ...init.headers },
      signal: init.signal ? AbortSignal.any([init.signal, AbortSignal.timeout(20000)]) : AbortSignal.timeout(20000),
    });
  } catch (error) {
    if (init.signal?.aborted) throw error;
    throw new ApiError(0, 'No se pudo conectar. Comprueba la conexión e inténtalo de nuevo.');
  }
  if (!response.ok) {
    // Never echo an arbitrary server body: validation bodies can contain submitted values.
    const messages: Record<number, string> = {
      401: 'La sesión terminó. Inicia sesión de nuevo.',
      403: 'Tu cuenta no tiene permiso para esta operación.',
      404: 'El usuario solicitado ya no está disponible.',
      409: 'La identidad ya está vinculada o el cambio afecta a un administrador protegido.',
      422: 'Revisa los campos. Al vincular, la identidad debe existir en SuperTokens.',
      429: 'Demasiadas solicitudes. Espera un momento e inténtalo de nuevo.',
    };
    if ([401, 403].includes(response.status) && path !== '/usuarios/me') {
      window.dispatchEvent(new Event(ACCESS_EVENT));
    }
    throw new ApiError(response.status, messages[response.status] ?? 'El servicio no está disponible. Inténtalo de nuevo.');
  }
  return response.json() as Promise<T>;
}
export const obtenerUsuarioActual = (signal?: AbortSignal) => request<UsuarioPerfil>('/usuarios/me', { signal });
export const listarUsuarios = (offset = 0, limit = 20, signal?: AbortSignal) =>
  request<ListaUsuarios>(`/usuarios?offset=${offset}&limit=${limit}`, { signal });
export const consultarUsuario = (id: number, signal?: AbortSignal) => request<UsuarioInterno>(`/usuarios/${id}`, { signal });
export const crearUsuario = (datos: UsuarioCrear) => request<UsuarioInterno>('/usuarios', { method: 'POST', body: JSON.stringify(datos) });
export const modificarUsuario = (id: number, datos: UsuarioModificar) => request<UsuarioInterno>(`/usuarios/${id}`, { method: 'PATCH', body: JSON.stringify(datos) });
