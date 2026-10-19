const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

async function verificar(response: Response): Promise<Response> {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail ?? body?.message ?? `HTTP ${response.status}`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return response;
}

export async function api<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  const res = await verificar(await fetch(`${API_URL}${endpoint}`, { ...options, headers }));
  return await res.json() as T;
}

export async function enviarArchivo<T = unknown>(endpoint: string, file: File): Promise<T> {
  const body = new FormData();
  body.append('archivo', file);
  return api<T>(endpoint, { method: 'POST', body });
}

export async function descargar(endpoint: string, nombre: string): Promise<void> {
  const res = await verificar(await fetch(`${API_URL}${endpoint}`));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  try {
    const a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } finally {
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}
