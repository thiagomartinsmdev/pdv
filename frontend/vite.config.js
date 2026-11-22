import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Configuração do Vite: servidor de desenvolvimento e build do frontend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // a porta precisa ser esta, pois é a liberada no CORS da API
  },
})
