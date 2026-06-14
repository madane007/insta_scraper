import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite dev server config.
// The /api proxy forwards frontend requests to the Flask backend during
// development so you don't run into CORS issues and don't need to hardcode
// the backend URL in the client.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
