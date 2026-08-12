<template>
  <div id="app" class="app-container">
    <!-- Navigation Bar -->
    <Navigation v-if="!isAuthPage" />

    <div class="app-body" :class="{ 'has-sidebar': showGlobalSidebar }">
      <button
        v-if="showGlobalSidebar"
        class="mobile-sidebar-toggle"
        type="button"
        :aria-label="uiStore.sidebarOpen ? 'Close navigation menu' : 'Open navigation menu'"
        :aria-expanded="uiStore.sidebarOpen"
        @click="uiStore.toggleSidebar"
      >
        <i :class="uiStore.sidebarOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
      </button>

      <div
        v-if="showGlobalSidebar && uiStore.sidebarOpen"
        class="sidebar-backdrop"
        aria-hidden="true"
        @click="uiStore.toggleSidebar"
      ></div>

      <GlobalSidebar v-if="showGlobalSidebar" />

      <!-- Main Content -->
      <main :class="{ 'with-nav': !isAuthPage }">
        <!-- Alert Messages -->
      <div v-if="uiStore.error" class="alert alert-danger alert-dismissible fade show" role="alert">
        <strong>Error:</strong> {{ uiStore.error }}
        <button type="button" class="btn-close" @click="uiStore.setError(null)"></button>
      </div>

      <div
        v-if="uiStore.success"
        class="alert alert-success alert-dismissible fade show"
        role="alert"
      >
        <strong>Success!</strong> {{ uiStore.success }}
        <button type="button" class="btn-close" @click="uiStore.setSuccess(null)"></button>
      </div>

      <!-- Loading Overlay -->
      <div v-if="uiStore.isLoading" class="loading-overlay">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Router View -->
        <RouterView />
      </main>
    </div>

    <!-- Footer -->
    <Footer v-if="!isAuthPage" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/store'
import { useUIStore } from './stores/store'
import { useSettingsStore } from './stores/store'
import Navigation from './components/Navigation.vue'
import GlobalSidebar from './components/GlobalSidebar.vue'
import Footer from './components/Footer.vue'
import apiClient from './utils/api_client'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const uiStore = useUIStore()
const settingsStore = useSettingsStore()

// Check if current page is auth page (login/register)
const isAuthPage = computed(() => {
  return ['Login', 'Register'].includes(route.name)
})

const showGlobalSidebar = computed(() => {
  return userStore.isAuthenticated && route.name !== 'Home' && !isAuthPage.value
})

// Initialize app on mount
onMounted(async () => {
  // Load platform settings
  try {
    const response = await apiClient.getPlatformSettings()
    settingsStore.setPlatformSettings(response.data)
  } catch (error) {
    console.error('Failed to load platform settings:', error)
  }

  // If user is logged in, load profile and notifications
  if (userStore.isAuthenticated) {
    try {
      const profileResponse = await apiClient.getProfile()
      userStore.setProfile(profileResponse.data)

      const notificationsResponse =
          await apiClient.getNotifications()


      userStore.setNotifications(
          notificationsResponse.data.results ??
          notificationsResponse.data
      )
    } catch (error) {
      console.error('Failed to load user data:', error)
      if (error.response?.status === 401) {
        userStore.logout()
        router.push({ name: 'Login' })
      }
    }
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #ffffff;
}

.app-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  min-height: calc(100vh - 70px);
}

.app-body.has-sidebar {
  grid-template-columns: minmax(180px, 2fr) minmax(0, 10fr);
  align-items: start;
}

main {
  min-width: 0;
  position: relative;
}

main.with-nav {
  margin-top: 0 !important;
}

.mobile-sidebar-toggle,
.sidebar-backdrop {
  display: none;
}

@media (max-width: 991px) {
  .app-body.has-sidebar {
    grid-template-columns: minmax(0, 1fr);
  }

  .mobile-sidebar-toggle {
    position: fixed;
    top: 5.25rem;
    left: 1rem;
    z-index: 1040;
    display: grid;
    width: 42px;
    height: 42px;
    place-items: center;
    padding: 0;
    border: 0;
    border-radius: 50%;
    color: var(--navy);
    background: var(--cyan);
    box-shadow: 0 6px 18px rgba(6, 6, 31, 0.2);
    cursor: pointer;
    font-size: 1.35rem;
  }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1045;
    display: block;
    background: rgba(6, 6, 31, 0.5);
  }

  body:has(.sidebar-backdrop) {
    overflow: hidden;
  }

  main.with-nav {
    width: 100%;
  }
}

@media (max-width: 575px) {
  .mobile-sidebar-toggle {
    top: 4.75rem;
    left: 0.75rem;
  }
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.alert {
  margin: 1rem;
  border-radius: 8px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
