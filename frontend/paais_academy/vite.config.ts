import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  
  server: {
    port: 8080,
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static/rest_framework': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/bootstrap')) return 'bootstrap'
          if (id.includes('node_modules')) return 'vendor'
          return undefined
        },
      }
    }
  },
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  
  define: {
    '__DEV__': true,
    '__VERSION__': JSON.stringify('1.0.0'),
  }
})
