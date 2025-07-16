import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '172.16.0.2',
      'coach-outreach-dashboard-tunnel-ooubd4ji.devinapps.com',
      '.devinapps.com'
    ]
  }
})
