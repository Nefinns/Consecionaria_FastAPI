# Dependencias y seguridad — AutoGest Unidad 5

## Objetivo

Conservar React 19, TypeScript 6, Vite 8, Tailwind 4 y componentes Base UI/shadcn (preset Nova) con Node 22; evitar arrastrar al laboratorio el problema `minimatch` de la herramienta ESLint del ZIP anterior.

## Decisión aplicada

- El frontend mantiene las dependencias de **ejecución** y las herramientas de construcción provenientes del `package.json` y `package-lock.json` de DaVinciMusic, con las versiones fijadas en el lockfile de referencia.
- Se eliminaron las dependencias **de desarrollo** `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh` y `globals`, que formaban la cadena que llevaba a `minimatch@10.2.6`.
- El lockfile del laboratorio fue reconstruido con los paquetes alcanzables desde las dependencias vigentes. El archivo resultante **no incluye `minimatch`** ni ESLint.
- `npm run lint` realiza `tsc --noEmit -p tsconfig.app.json` (verificación estática de tipos). **No sustituye una revisión completa de reglas ESLint**. Si en el futuro necesitas lint semántico, habrá que elegir un linter y comprobar su árbol de dependencias con `npm audit`.
- NO se fuerza `minimatch@11` a través de `overrides`, ya que ESLint 10.12 declaró compatibilidad con `^10.2.5` y el salto de versión mayor no estaba garantizado.

Referencia del aviso `GHSA-g3hv-75wg-m249` (publicado en octubre de 2026): https://github.com/advisories/GHSA-g3hv-75wg-m249. Versión corregida de minimatch: `11.0.1`.

## Backend

Se proporciona `requirements_proyecto_original.txt`, copia íntegra de lo entregado para la concesionaria. El `requirements.txt` **ejecutable del laboratorio** utiliza el subconjunto de esas mismas versiones fijadas que realmente requiere su API de consultas: FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary y python-dotenv. SuperTokens y SQLModel permanecen en el proyecto comercial original, pero no tienen una función en este laboratorio educativo sin autenticación ni modelos ORM.

**No se han declarado estas versiones libres de vulnerabilidades:** debe realizarse una auditoría actualizada al instalarlas. Una forma de evaluar Python es instalar y ejecutar `pip-audit` en un entorno aislado cuando haya acceso al registro.

## Verificación local obligatoria (Windows)

```powershell
cd frontend
npm ci
npm run build
npm run lint
npm ls minimatch eslint typescript-eslint
npm audit
npm audit --omit=dev
```

Es esperable que `npm ls minimatch eslint typescript-eslint` indique que esos paquetes **no están instalados**. El resultado real de `npm audit` dependerá de los avisos publicados al momento de instalar. No se ejecutó `npm ci` durante la generación del ZIP porque el entorno no podía resolver `registry.npmjs.org`; se conservaron los metadatos, versiones e integridades originales de los demás paquetes en el lockfile.
