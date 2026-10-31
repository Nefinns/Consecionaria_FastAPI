// Only the public API origin belongs in the browser. Never include credentials.
const configured = import.meta.env.VITE_API_URL?.trim() || 'http://localhost:8000';
const origin = new URL(configured);
if (!['http:', 'https:'].includes(origin.protocol) || origin.username || origin.password ||
    origin.search || origin.hash || !['', '/'].includes(origin.pathname) ||
    (origin.protocol === 'http:' && !['localhost', '127.0.0.1'].includes(origin.hostname))) {
  throw new Error('VITE_API_URL debe ser un origen HTTPS o localhost, sin rutas ni credenciales.');
}
export const API_URL = origin.origin;
