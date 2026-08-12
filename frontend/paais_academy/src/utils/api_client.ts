import axios from 'axios'
import { useUserStore } from '../stores/store'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.accessToken || localStorage.getItem('accessToken')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor - Handle token refresh and errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Token expired - try to refresh
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/token/refresh/')
    ) {

      try {
        const userStore = useUserStore()
        const refreshToken = userStore.refreshToken || localStorage.getItem('refreshToken')

        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          userStore.setAccessToken(access)
          localStorage.setItem('accessToken', access)

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - logout
        const userStore = useUserStore()
        userStore.logout()
      }
    }

    return Promise.reject(error)
  },
)

// API Methods
export default {
  // ===== AUTHENTICATION =====

  sendOTP(contact: string, checkExisting = true) {
    const contactType = contact.includes('@') ? 'email' : 'phone'
    return apiClient.post('/auth/register/send-otp/', {
      contact,
      contact_type: contactType,
      check_existing: checkExisting,
    })
  },

  verifyOTP(contact, otp) {
    return apiClient.post('/auth/register/verify-otp/', {
      contact,
      otp_code: otp,
    })
  },

  refreshToken(refreshToken) {
    return apiClient.post('/auth/token/refresh/', {
      refresh: refreshToken,
    })
  },

  // ===== TRACKS & LESSONS =====

  getTracks(params = {}) {
    return apiClient.get('/tracks/', { params })
  },

  getTrackDetail(trackId) {
    return apiClient.get(`/tracks/${trackId}/`)
  },

  getTrackLessons(trackId) {
    return apiClient.get(`/tracks/${trackId}/lessons/`)
  },

  getTrackProgress(trackId) {
    return apiClient.get(`/tracks/${trackId}/progress/`)
  },

  getLessons(params = {}) {
    return apiClient.get('/lessons/', { params })
  },

  getLessonDetail(lessonId) {
    return apiClient.get(`/lessons/${lessonId}/`)
  },

  startLesson(lessonId) {
    return apiClient.post(`/lessons/${lessonId}/start/`)
  },

  submitQuiz(lessonId, answers) {
    return apiClient.post(`/lessons/${lessonId}/submit_quiz/`, { answers })
  },

  completeLesson(lessonId, quizScore = null) {
    return apiClient.post(`/lessons/${lessonId}/complete/`, {
      quiz_score: quizScore,
    })
  },

  getAssessmentAttempts() {
    return apiClient.get('/assessment-attempts/')
  },

  getUserProgress() {
    return apiClient.get('/progress/')
  },

  // ===== USER PROFILE =====

  getProfile() {
    return apiClient.get('/user/profile/')
  },

  updateProfile(profileData) {
    return apiClient.put('/user/profile/', profileData)
  },

  deleteProfile() {
    return apiClient.delete('/user/profile/')
  },

  getDashboard() {
    return apiClient.get('/user/dashboard/')
  },

  getGamification() {
    return apiClient.get('/user/gamification/')
  },

  getAnalytics() {
    return apiClient.get('/user/analytics/')
  },

  // ===== CERTIFICATES =====

  getCertificates() {
    return apiClient.get('/certificates/')
  },

  getCertificateDetail(certificateId) {
    return apiClient.get(`/certificates/${certificateId}/`)
  },

  verifyCertificate(certificateId) {
    return apiClient.get(`/certificates/${certificateId}/verify/`)
  },

  makeCertificatePublic(certificateId) {
    return apiClient.post(`/certificates/${certificateId}/make-public/`)
  },

  // ===== PAYMENTS =====

  initializePayment(trackId, credentialType = 'starter') {
    return apiClient.post('/payments/initialize/', {
      track_id: trackId,
      credential_type: credentialType,
    })
  },

  verifyPayment(reference) {
    return apiClient.get(`/payments/verify/${reference}/`)
  },

  // ===== DONATIONS =====

  initializeDonation(amount, message = '') {
    return apiClient.post('/donations/initialize/', {
      amount,
      message,
      callback_url: `${window.location.origin}/support/`,
    })
  },

  verifyDonation(reference) {
    return apiClient.get(`/payments/verify/${reference}/`)
  },

  // ===== SETTINGS =====

  getPlatformSettings() {
    return apiClient.get('/settings/')
  },

  // ===== NOTIFICATIONS =====

  getNotifications() {
    return apiClient.get('/notifications/')
  },

  markNotificationAsRead(notificationId) {
    return apiClient.post(`/notifications/${notificationId}/mark_as_read/`)
  },

  markAllNotificationsAsRead() {
    return apiClient.post('/notifications/mark_all_as_read/')
  },

  // ===== COMMUNITY =====

  getCommunityPosts() {
    return apiClient.get('/community/posts/')
  },

  createCommunityPost(postData) {
    return apiClient.post('/community/posts/', postData)
  },

  toggleCommunityLike(postId) {
    return apiClient.post(`/community/posts/${postId}/like/`)
  },

  addCommunityComment(postId, body) {
    return apiClient.post(`/community/posts/${postId}/comment/`, { body })
  },

  // ===== ADMIN (if user is admin) =====

  createTrack(trackData) {
    return apiClient.post('/admin/tracks/', trackData)
  },

  updateTrack(trackId, trackData) {
    return apiClient.put(`/admin/tracks/${trackId}/`, trackData)
  },

  deleteTrack(trackId) {
    return apiClient.delete(`/admin/tracks/${trackId}/`)
  },

  createLesson(trackId, lessonData) {
    return apiClient.post(`/admin/tracks/${trackId}/lessons/`, lessonData)
  },

  updateLesson(trackId, lessonId, lessonData) {
    return apiClient.put(`/admin/tracks/${trackId}/lessons/${lessonId}/`, lessonData)
  },

  deleteLesson(trackId, lessonId) {
    return apiClient.delete(`/admin/tracks/${trackId}/lessons/${lessonId}/`)
  },

  updatePlatformSettings(settingsData) {
    return apiClient.put('/admin/settings/', settingsData)
  },
}

