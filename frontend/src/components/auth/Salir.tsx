import { useState } from 'react';
import Session from 'supertokens-auth-react/recipe/session';
import { Button } from '@/components/ui/button';

export default function Salir() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  async function salir() {
    setBusy(true); setError(false);
    try { await Session.signOut(); window.location.replace('/auth'); }
    catch { setError(true); setBusy(false); }
  }
  return <div><Button variant="outline" disabled={busy} onClick={() => void salir()}>{busy ? 'Cerrando sesión…' : 'Cerrar sesión'}</Button>
    {error && <p role="alert">No se pudo cerrar la sesión. Reintenta.</p>}</div>;
}
