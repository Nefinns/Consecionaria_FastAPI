import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import {
  ApiError,
  obtenerUsuarioActual,
  type UsuarioInterno,
} from "@/services/usuarios";

type Estado =
  | { tipo: "cargando" }
  | { tipo: "autorizado"; usuario: UsuarioInterno }
  | { tipo: "pendiente" }
  | { tipo: "inactivo" }
  | { tipo: "error"; mensaje: string };

interface Props {
  children: (usuario: UsuarioInterno) => ReactNode;
}

export default function UsuarioAutorizado({ children }: Props) {
  const [estado, setEstado] = useState<Estado>({
    tipo: "cargando",
  });

  useEffect(() => {
    let activo = true;

    async function verificar() {
      try {
        const usuario = await obtenerUsuarioActual();

        if (!activo) return;

        if (!usuario.activo) {
          setEstado({ tipo: "inactivo" });
          return;
        }

        setEstado({ tipo: "autorizado", usuario });
      } catch (error) {
        if (!activo) return;

        if (error instanceof ApiError) {
          if (error.status === 403 || error.status === 404) {
            setEstado({ tipo: "pendiente" });
            return;
          }
        }

        setEstado({
          tipo: "error",
          mensaje:
            error instanceof Error
              ? error.message
              : "Error desconocido.",
        });
      }
    }

    void verificar();

    return () => {
      activo = false;
    };
  }, []);

  if (estado.tipo === "cargando") {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Verificando permisos de acceso...</p>
      </main>
    );
  }

  if (estado.tipo === "pendiente") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <h1 className="text-2xl font-bold">Acceso pendiente</h1>
        <p>
          Tu cuenta está registrada, pero todavía no tiene
          autorización para utilizar AutoGest.
        </p>
        <p className="text-sm text-muted-foreground">
          Solicita al administrador que habilite tu cuenta.
        </p>
      </main>
    );
  }

  if (estado.tipo === "inactivo") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <h1 className="text-2xl font-bold">Cuenta desactivada</h1>
        <p>Tu acceso a AutoGest está deshabilitado.</p>
      </main>
    );
  }

  if (estado.tipo === "error") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <h1 className="text-2xl font-bold">
          No se pudo verificar el acceso
        </h1>
        <p>{estado.mensaje}</p>
      </main>
    );
  }

  return <>{children(estado.usuario)}</>;
}