import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

type RecordData = Record<string, any>
type NotificationData = RecordData & { is_read?: boolean }

// ===== USER STORE =====
export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const isAuthenticated = computed(() => !!accessToken.value)
  const profile = ref(null)
  const notifications = ref<NotificationData[]>([])
  const unreadNotificationsCount = computed(() =>
    notifications.value.filter((notification) => !notification.is_read).length,
  )

  const setUser = (userData) => {
    user.value = userData
  }

  const setTokens = (access, refresh) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  const setAccessToken = (access) => {
    accessToken.value = access
    localStorage.setItem('accessToken', access)
  }

  const setProfile = (profileData) => {
    profile.value = profileData
  }

  const setNotifications = (notifs) => {

    notifications.value = Array.isArray(notifs)
        ? notifs
        : notifs.results || []

}

  const logout = () => {
    user.value = null
    profile.value = null
    accessToken.value = null
    refreshToken.value = null
    notifications.value = []
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    profile,
    notifications,
    unreadNotificationsCount,
    setUser,
    setTokens,
    setAccessToken,
    setProfile,
    setNotifications,
    logout,
  }
})

// ===== COURSES STORE =====
export const useCourseStore = defineStore('courses', () => {
  const tracks = ref<RecordData[]>([])
  const currentTrack = ref<RecordData | null>(null)
  const lessons = ref<RecordData[]>([])
  const userProgress = ref<RecordData | null>(null)
  const certificates = ref<RecordData[]>([])
  const lessonProgress = ref<Record<string, RecordData>>({})

  const setTracks = (tracksData) => {
    tracks.value = Array.isArray(tracksData) ? tracksData : tracksData?.results || []
  }

  const setCurrentTrack = (trackData) => {
    currentTrack.value = trackData
  }

  const setLessons = (lessonsData) => {
    lessons.value = Array.isArray(lessonsData) ? lessonsData : lessonsData?.results || []
  }

  const setUserProgress = (progressData) => {
    userProgress.value = progressData
  }

  const setCertificates = (certsData) => {
    certificates.value = Array.isArray(certsData) ? certsData : certsData?.results || []
  }

  const setLessonProgress = (lessonId, progressData) => {
    lessonProgress.value[lessonId] = progressData
  }

  const getTrackById = (trackId) => {
    return tracks.value.find((t) => String(t.id) === String(trackId))
  }

  const getLessonsByTrack = (trackId) => {
    return lessons.value.filter((l) => String(l.track) === String(trackId))
  }

  const getProgressByLesson = (lessonId) => {
    return lessonProgress.value[lessonId]
  }

  return {
    tracks,
    currentTrack,
    lessons,
    userProgress,
    certificates,
    lessonProgress,
    setTracks,
    setCurrentTrack,
    setLessons,
    setUserProgress,
    setCertificates,
    setLessonProgress,
    getTrackById,
    getLessonsByTrack,
    getProgressByLesson,
  }
})

// ===== SETTINGS STORE =====
export const useSettingsStore = defineStore('settings', () => {
  const platformSettings = ref({
    site_name: 'PAAIS Academy',
    site_description: 'Learn the AI tools that do your everyday work',
    primary_color: '#0A0A33',
    secondary_color: '#E900FF',
    accent_color: '#2EE6D6',
    enable_paystack: true,
    enable_ai_features: true,
    enable_certificates: true,
  })

  const theme = ref({
    navy: '#0A0A33',
    navyDeep: '#06061F',
    magenta: '#E900FF',
    purple: '#7B2FF2',
    cyan: '#2EE6D6',
    lav: '#F3F2FA',
    ink: '#1B1B3A',
  })

  const setPlatformSettings = (settings) => {
    platformSettings.value = settings
    // Update CSS variables
    if (settings.primary_color) {
      document.documentElement.style.setProperty('--primary-color', settings.primary_color)
    }
    if (settings.secondary_color) {
      document.documentElement.style.setProperty('--secondary-color', settings.secondary_color)
    }
    if (settings.accent_color) {
      document.documentElement.style.setProperty('--accent-color', settings.accent_color)
    }
  }

  return {
    platformSettings,
    theme,
    setPlatformSettings,
  }
})

// ===== PAYMENT STORE =====
export const usePaymentStore = defineStore('payments', () => {
  const transactions = ref([])
  const currentTransaction = ref(null)
  const paymentLoading = ref(false)

  const setTransactions = (txns) => {
    transactions.value = txns
  }

  const setCurrentTransaction = (txn) => {
    currentTransaction.value = txn
  }

  const setPaymentLoading = (loading) => {
    paymentLoading.value = loading
  }

  return {
    transactions,
    currentTransaction,
    paymentLoading,
    setTransactions,
    setCurrentTransaction,
    setPaymentLoading,
  }
})

// ===== UI STORE =====
export const useUIStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const error = ref(null)
  const success = ref(null)
  const sidebarOpen = ref(true)

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const setError = (errorMsg) => {
    error.value = errorMsg
    if (errorMsg) {
      setTimeout(() => {
        error.value = null
      }, 5000)
    }
  }

  const setSuccess = (successMsg) => {
    success.value = successMsg
    if (successMsg) {
      setTimeout(() => {
        success.value = null
      }, 3000)
    }
  }

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  return {
    isLoading,
    error,
    success,
    sidebarOpen,
    setLoading,
    setError,
    setSuccess,
    toggleSidebar,
  }
})
