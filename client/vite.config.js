import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/calculate_route': {
        target: 'http://127.0.0.1:8800',  // Flask server
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/calculate_route/, '/calculate_route')
      },
    },
  },
})
