import type { Catalog, DbState, RunResult } from './types'
const API = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response
  try { response = await fetch(`${API}${url}`, options) }
  catch { throw new Error(`No se pudo contactar al backend (${API}). Inicia FastAPI y revisa el puerto.`) }
  const json: unknown = await response.json().catch(() => ({}))
  if (!response.ok) {
    const error = json as {detail?: string}
    throw new Error(error.detail || `Error HTTP ${response.status}`)
  }
  return json as T
}
export const getCatalog = () => request<Catalog>('/api/catalogo')
export const getState = () => request<DbState>('/api/estado')
export const prepareDb = () => request<{ok:boolean;message:string;created_now:boolean;seed:object}>('/api/preparar', { method: 'POST' })
export const runExercise = (code:string, params:Record<string,string|number>) => request<RunResult>(`/api/ejecutar/${code}`, {
  method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({params})
})
