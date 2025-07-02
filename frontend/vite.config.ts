import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true
    },
    allowedHosts: [
      'casewisemd.org',
      'www.casewisemd.org',
      'app.casewisemd.org',
      'api.casewisemd.org',
      'viewer.casewisemd.org',
      'dicom.casewisemd.org'
    ],
    hmr: {
      protocol: 'wss',
      host: 'app.casewisemd.org'
    }
  }
})
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true
    },
    allowedHosts: [
      'casewisemd.org',
      'www.casewisemd.org',
      'app.casewisemd.org',
      'api.casewisemd.org',
      'viewer.casewisemd.org',
      'dicom.casewisemd.org'
    ],
    hmr: {
      protocol: 'wss',
      host: 'app.casewisemd.org'
    }
  }
})
