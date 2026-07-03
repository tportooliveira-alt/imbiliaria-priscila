import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Proxy de DEV: em desenvolvimento, /api e /assets apontam para a produção
// (catálogo + fotos reais), evitando CORS. Em produção o site fica no mesmo
// domínio, então os mesmos caminhos relativos continuam funcionando.
const BACKEND = 'https://pvscelosimobiliaria.com'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
  ],
  // Em produção o site fica na RAIZ. O bundle vai pra /app/ (não /assets/) pra NÃO
  // colidir com /assets/ das fotos dos imóveis (servidas pelo nginx).
  build: { assetsDir: 'app' },
  server: {
    proxy: {
      '/api': { target: BACKEND, changeOrigin: true, secure: true },
      '/assets': { target: BACKEND, changeOrigin: true, secure: true },
    },
  },
})
