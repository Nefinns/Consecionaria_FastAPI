
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import * as reactRouterDom from "react-router-dom";

import { SuperTokensWrapper } from "supertokens-auth-react";
import { SessionAuth } from "supertokens-auth-react/recipe/session";

import { getSuperTokensRoutesForReactRouterDom } from "supertokens-auth-react/ui";

import { EmailPasswordPreBuiltUI } from "supertokens-auth-react/recipe/emailpassword/prebuiltui";

import UsuarioAutorizado from "@/components/auth/UsuarioAutorizado";
import type { UsuarioInterno } from "@/services/usuarios";

function Dashboard({ usuario }: { usuario: UsuarioInterno }) {
  return (
    <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
      <h1 className="text-3xl font-bold">AutoGest</h1>

      <p className="mt-4">
        Bienvenido, <strong>{usuario.nombre}</strong>.
      </p>

      <p className="mt-2">
        Rol: <strong>{usuario.rol}</strong>
      </p>

      <p className="mt-4 text-green-700">
        Tu cuenta está autenticada y autorizada.
      </p>
    </main>
  );
}

function DashboardProtegido() {
  return (
    <SessionAuth>
      <UsuarioAutorizado>
        {(usuario) => <Dashboard usuario={usuario} />}
      </UsuarioAutorizado>
    </SessionAuth>
  );
}

export default function App() {
  return (
    <SuperTokensWrapper>
      <BrowserRouter>
        <Routes>
          {getSuperTokensRoutesForReactRouterDom(
            reactRouterDom,
            [EmailPasswordPreBuiltUI]
          )}

          <Route
            path="/"
            element={<Navigate to="/dashboard" replace />}
          />

          <Route
            path="/dashboard"
            element={<DashboardProtegido />}
          />

          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />
        </Routes>
      </BrowserRouter>
    </SuperTokensWrapper>
  );
}