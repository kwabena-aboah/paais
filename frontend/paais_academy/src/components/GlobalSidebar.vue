<template>
  <aside
    class="global-sidebar"
    :class="{ collapsed: !uiStore.sidebarOpen }"
    aria-label="Learning navigation"
  >
    <button class="sidebar-toggle" type="button" @click="uiStore.toggleSidebar" aria-label="Toggle sidebar">
      <i :class="uiStore.sidebarOpen ? 'bi bi-chevron-left' : 'bi bi-chevron-right'"></i>
    </button>

    <div v-if="uiStore.sidebarOpen" class="sidebar-content">
      <div class="sidebar-user">
        <div class="avatar">{{ initials }}</div>
        <div>
          <strong>{{ displayName }}</strong>
          <small>Learning workspace</small>
        </div>
      </div>

      <nav class="sidebar-nav" aria-label="Learning navigation" @click="closeOnMobileNavigation">
        <router-link to="/dashboard" class="sidebar-link">
          <i class="bi bi-grid-1x2-fill"></i><span>Dashboard</span>
        </router-link>
        <router-link to="/profile" class="sidebar-link">
          <i class="bi bi-person-fill"></i><span>My Profile</span>
        </router-link>
        <router-link to="/tracks" class="sidebar-link">
          <i class="bi bi-collection-play-fill"></i><span>Available Tracks</span>
        </router-link>
        <router-link to="/certificates" class="sidebar-link">
          <i class="bi bi-award-fill"></i><span>Certificates</span>
        </router-link>
        <router-link to="/community" class="sidebar-link">
          <i class="bi bi-people-fill"></i><span>Community</span>
        </router-link>
        <router-link to="/support" class="sidebar-link">
          <i class="bi bi-heart-fill"></i><span>Support the cause</span>
        </router-link>
        <router-link v-if="userStore.user?.is_staff" to="/admin" class="sidebar-link">
          <i class="bi bi-shield-lock-fill"></i><span>Admin Panel</span>
        </router-link>
      </nav>

      <router-link to="/" class="sidebar-home-link" @click="closeOnMobileNavigation">
        <i class="bi bi-arrow-left"></i> Back to home
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore, useUIStore } from '../stores/store'

const userStore = useUserStore()
const uiStore = useUIStore()
const displayName = computed(() => userStore.user?.first_name || userStore.user?.username || 'Learner')
const initials = computed(() => displayName.value.slice(0, 2).toUpperCase())

const closeOnMobileNavigation = () => {
  if (window.innerWidth <= 991 && uiStore.sidebarOpen) {
    uiStore.toggleSidebar()
  }
}
</script>

<style scoped>
.global-sidebar {
  position: sticky;
  top: 0;
  z-index: 40;
  width: 100%;
  min-height: calc(120vh - 70px);
  padding: 1.25rem 1rem;
  color: white;
  background: var(--navy-deep);
  box-shadow: 4px 0 18px rgba(6, 6, 31, 0.16);
  transition: width 0.2s ease;
}
.global-sidebar.collapsed { width: 100%; }
.global-sidebar.collapsed .sidebar-toggle { right: 1rem; }
.sidebar-toggle {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 50%;
  color: var(--navy);
  background: var(--cyan);
  cursor: pointer;
}
.sidebar-content { padding-top: 1.5rem; }
.sidebar-user { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; }
.avatar { display: grid; place-items: center; width: 40px; height: 40px; border-radius: 50%; color: var(--navy); background: var(--cyan); font-weight: 800; }
.sidebar-user strong, .sidebar-user small { display: block; }
.sidebar-user small { color: rgba(255,255,255,.6); font-size: .75rem; }
.sidebar-nav { display: grid; gap: .5rem; }
.sidebar-link, .sidebar-home-link { display: flex; align-items: center; gap: .75rem; padding: .75rem .8rem; border-radius: 8px; color: rgba(255,255,255,.78); text-decoration: none; }
.sidebar-link:hover, .sidebar-link.router-link-active { color: white; background: rgba(46,230,214,.14); }
.sidebar-link.router-link-active { box-shadow: inset 3px 0 var(--cyan); }
.sidebar-home-link { position: absolute; bottom: 1.5rem; left: 1rem; font-size: .85rem; color: var(--cyan); }

@media (max-width: 991px) {
  .global-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1050;
    width: min(82vw, 320px);
    height: 100dvh;
    min-height: 100dvh;
    transform: translateX(-105%);
    transition: transform 0.25s ease;
  }

  .global-sidebar:not(.collapsed) {
    transform: translateX(0);
  }

  .global-sidebar.collapsed {
    width: min(82vw, 320px);
    transform: translateX(-105%);
  }

  .sidebar-home-link {
    bottom: 1rem;
  }
}
</style>
