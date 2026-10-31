// Validation only: no dotenv loading, public assets, or application server.
import { build } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath, URL } from 'node:url';

await build({
  root: fileURLToPath(new URL('.', import.meta.url)),
  configFile: false,
  envDir: false,
  envPrefix: 'AUTOGEST_VALIDATION_UNUSED_',
  publicDir: false,
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  define: { 'import.meta.env.VITE_API_URL': JSON.stringify('http://localhost:8000') },
  build: { outDir: 'dist-validacion', emptyOutDir: false, sourcemap: false },
});
