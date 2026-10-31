import Session from "supertokens-auth-react/recipe/session";

const API_URL = import.meta.env.VITE_API_URL;

export type RolUsuario = "administrador" | "gerente" | "mecanico";

export interface UsuarioInterno {
  id_usuario: number;
  identidad_externa: string;
  nombre: string;
  rol: RolUsuario;
  activo: boolean;
}

export class ApiError extends Error {
  public status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function obtenerUsuarioActual(): Promise<UsuarioInterno> {
  const token = await Session.getAccessToken();

  if (!token) {
    throw new ApiError(401, "No existe una sesión activa.");
  }

  const response = await fetch(`${API_URL}/usuarios/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new ApiError(
      response.status,
      `No se pudo consultar el usuario: ${response.status}`
    );
  }

  return response.json() as Promise<UsuarioInterno>;
}