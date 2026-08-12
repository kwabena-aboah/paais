<template>
  <nav  class="list-unstyled m-0 p-0">
      <div class="nav-inner">
        <div class="logo">
          <router-link to="/">
          <img class="mark" src="data:image/png;base64,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" alt="PAAIS mark">
          {{ platformSettings.site_name || 'PAAIS' }}
        </router-link>
        </div>
        <template v-if="userStore.isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard" @click="closeNavbar"
                ><i class="bi bi-house"></i> Dashboard</router-link
              >
            </li>

            <!-- Notifications -->
            <li class="nav-item dropdown">
              <button
                class="nav-link dropdown-toggle position-relative"
                type="button"
                @click="toggleDropdown('notifications')"
              >
                <i class="bi bi-bell-fill"></i> Notifications
                <span v-if="userStore.unreadNotificationsCount > 0" class="badge badge-danger">
                  {{ userStore.unreadNotificationsCount }}
                </span>
              </button>
              <ul v-if="dropdowns.notifications" class="dropdown-menu dropdown-menu-end show">
                <li v-if="userStore.notifications.length === 0" class="px-3 py-2">
                  <small class="text-muted">No notifications</small>
                </li>
                <li
                  v-for="notif in userStore.notifications.slice(0, 5)"
                  :key="notif.id"
                  class="dropdown-item"
                >
                  <small>{{ notif.title }}</small>
                </li>
              </ul>
            </li>

            <!-- Admin Menu -->
            <li v-if="userStore.user?.is_staff" class="nav-item">
              <router-link class="nav-link" to="/admin" @click="closeNavbar"><i class="bi bi-person-fill-gear"></i> Admin</router-link>
            </li>

            <!-- User Menu -->
            <li class="nav-item dropdown">
              <button
                class="nav-link dropdown-toggle"
                type="button"
                @click="toggleDropdown('user')"
              >
                <i class="bi bi-sliders"></i> My Account
              </button>
              <ul v-if="dropdowns.user" class="dropdown-menu dropdown-menu-end show">
                <li>
                  <router-link class="dropdown-item" to="/profile" @click="closeNavbar"
                    > <i class="bi bi-person-fill"></i> Profile</router-link
                  >
                </li>
                <li>
                  <router-link class="dropdown-item" to="/certificates" @click="closeNavbar"
                    ><i class="bi bi-award"></i> Certificates</router-link
                  >
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout"><i class="bi bi-box-arrow-right"></i> Logout</a>
                </li>
              </ul>
            </li>
          </template>

          <!-- Unauthenticated Links -->
          <template v-else>
            <div class="nav-links">
              <a href="#how">How it works</a>
              <a href="#tracks">Tracks</a>
              <a href="#credentials">Credentials</a>
              <router-link to="/login">Login</router-link>
            </div>
            <a class="btn btn-primary" style="padding:10px 22px;font-size:.85rem" href="#signup">Start free</a>
          </template>
      </div>
    </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/store'
import { useSettingsStore } from '../stores/store'

const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

const navbarOpen = ref(false)
const dropdowns = ref({
  user: false,
  notifications: false,
})

const platformSettings = computed(() => settingsStore.platformSettings)

const toggleNavbar = () => {
  navbarOpen.value = !navbarOpen.value
}

const closeNavbar = () => {
  navbarOpen.value = false
}

const toggleDropdown = (name) => {
  dropdowns.value[name] = !dropdowns.value[name]
  // Close other dropdowns
  Object.keys(dropdowns.value).forEach((key) => {
    if (key !== name) {
      dropdowns.value[key] = false
    }
  })
}

const logout = async () => {
  userStore.logout()
  await router.push({ name: 'Home' })
  closeNavbar()
}
</script>

<style scoped>

@media (max-width: 991px) {
  .navbar,
  .nav-inner {
    width: 100%;
  }

  .nav-inner {
    gap: 0.75rem;
    padding: 0.75rem 1rem;
  }

  .navbar-brand {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .nav-actions {
    flex-wrap: nowrap;
  }
}

@media (max-width: 575px) {
  .nav-inner {
    padding-inline: 0.75rem;
  }

  .nav-actions .btn,
  .nav-actions .nav-link span {
    font-size: 0.8rem;
  }
}
nav {
  position: relative;
  z-index: 100;
  overflow: visible;
}

.nav-inner {
  position: relative;
}

.nav-item.dropdown {
  position: relative;
}

.nav-item.dropdown .dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  left: auto;
  z-index: 1100;
  min-width: 220px;
  max-width: min(320px, calc(100vw - 2rem));
  max-height: min(420px, calc(100vh - 90px));
  overflow-y: auto;
  padding: 0.5rem;
  margin: 0;
}

.nav-item.dropdown .dropdown-item {
  display: block;
  width: 100%;
  padding: 0.65rem 0.75rem;
  border-radius: 6px;
  white-space: normal;
}

.nav-item.dropdown .nav-link {
  border: 0;
  background: transparent;
  cursor: pointer;
}

.nav-item.dropdown .nav-link:focus-visible {
  outline: 2px solid var(--cyan);
  outline-offset: 2px;
}

.navbar {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.navbar-brand {
  font-family: var(--font-poppins);
  font-weight: 700;
  font-size: 1.5rem;
  color: white !important;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.navbar-brand:hover {
  color: var(--cyan) !important;
  transform: scale(1.05);
}

.brand-icon {
  font-size: 2rem;
  color: var(--magenta);
}

.nav-link {
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 500;
  transition: all 0.2s ease;
  position: relative;
  margin: 0 0.5rem;
}

.nav-link:hover {
  color: var(--cyan) !important;
}

.nav-link.router-link-active {
  color: var(--magenta) !important;
  border-bottom: 2px solid var(--magenta);
}

.dropdown-menu {
  background-color: var(--navy-deep);
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dropdown-item {
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: rgba(233, 0, 255, 0.2);
  color: var(--cyan);
}

.dropdown-divider {
  border-color: rgba(255, 255, 255, 0.1);
}

.badge-danger {
  background-color: #ef4444;
  font-size: 0.65rem;
  padding: 0.25rem 0.5rem;
  position: absolute;
  top: -5px;
  right: -10px;
}

.material-icons {
  font-size: 1.25rem;
  vertical-align: middle;
}

@media (max-width: 991px) {
  .nav-inner {
    width: 100%;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
  }

  .logo {
    min-width: 0;
    max-width: 55%;
  }

  .logo a {
    display: flex;
    min-width: 0;
    align-items: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .logo a img {
    flex: 0 0 auto;
  }

  .nav-item.dropdown .dropdown-menu {
    position: static;
    width: 100%;
    max-width: none;
    max-height: none;
    margin-top: 0.25rem;
  }

  .navbar-nav {
    margin-top: 1rem;
  }

  .nav-link {
    padding: 0.5rem 0 !important;
    margin: 0.5rem 0;
  }

  .btn-primary {
    margin-top: 0.5rem;
  }
}

@media (max-width: 575px) {
  .nav-inner {
    padding-inline: 0.75rem;
  }

  .logo {
    max-width: 48%;
    font-size: 1rem;
  }

  .mark {
    height: 30px;
  }

  .nav-link {
    font-size: 0.8rem;
  }
}
</style>
