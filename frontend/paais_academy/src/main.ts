import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.ts'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
// Import Bootstrap Icons CSS
import 'bootstrap-icons/font/bootstrap-icons.css'
import './styles/global.css'
import './styles/responsive.css'

// Create app
const app = createApp(App)

// Create pinia store
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)

// Global configuration
app.config.globalProperties.$apiURL = import.meta.env.VITE_API_URL || '/api/v1'
app.config.globalProperties.$appName = import.meta.env.VITE_APP_NAME || 'PAAIS Academy'

// Development mode
// Vue DevTools are enabled automatically in development builds.

// Production error handling
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err, info)

  // You can send errors to Sentry or logging service
  // Sentry.captureException(err)
}

// Mount app
app.mount('#app')
