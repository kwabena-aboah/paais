<template>
  <div class="admin-panel">
    <section class="admin-header">
      <div class="container-fluid">
        <h1>Admin Dashboard</h1>
        <p>Manage platform content and settings</p>
      </div>
    </section>

    <section class="admin-content">
      <div class="container-fluid">
        <!-- Tabs Navigation -->
        <ul class="nav nav-tabs mb-4" role="tablist">
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'tracks' }"
              @click="activeTab = 'tracks'"
              type="button"
            >
              Tracks
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'lessons' }"
              @click="activeTab = 'lessons'"
              type="button"
            >
              Lessons
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'settings' }"
              @click="activeTab = 'settings'"
              type="button"
            >
              Platform Settings
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'users' }"
              @click="activeTab = 'users'"
              type="button"
            >
              Users
            </button>
          </li>
        </ul>

        <!-- Tracks Tab -->
        <div v-show="activeTab === 'tracks'" class="tab-content">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Manage Tracks</h3>
            <button class="btn btn-primary" @click="showTrackForm = true">
              <i class="fas fa-plus"></i> Add Track
            </button>
          </div>

          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Track Name</th>
                  <th>Function</th>
                  <th>Lessons</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="track in tracks" :key="track.id">
                  <td>
                    <strong>{{ track.name }}</strong>
                  </td>
                  <td>{{ track.function }}</td>
                  <td>{{ getLessonCount(track.id) }}</td>
                  <td>
                    <span v-if="track.is_active" class="badge badge-success">Active</span>
                    <span v-else class="badge badge-warning">Inactive</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-2" @click="editTrack(track)">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteTrack(track.id)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Lessons Tab -->
        <div v-show="activeTab === 'lessons'" class="tab-content">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Manage Lessons</h3>
            <button class="btn btn-primary" @click="showLessonForm = true">
              <i class="fas fa-plus"></i> Add Lesson
            </button>
          </div>

          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Lesson Title</th>
                  <th>Track</th>
                  <th>Level</th>
                  <th>Duration</th>
                  <th>Published</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lesson in lessons" :key="lesson.id">
                  <td>
                    <strong>{{ lesson.title }}</strong>
                  </td>
                  <td>{{ getTrackName(lesson.track) }}</td>
                  <td>{{ lesson.level }}</td>
                  <td>{{ lesson.duration_minutes }} min</td>
                  <td>
                    <span v-if="lesson.is_published" class="badge badge-success">Published</span>
                    <span v-else class="badge badge-secondary">Draft</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-2" @click="editLesson(lesson)">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteLesson(lesson.id)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-show="activeTab === 'settings'" class="tab-content">
          <div class="row">
            <div class="col-lg-8">
              <div class="card">
                <div class="card-header">
                  <h5>Platform Settings</h5>
                </div>
                <div class="card-body">
                  <form @submit.prevent="updateSettings">
                    <div class="mb-3">
                      <label class="form-label">Site Name</label>
                      <input
                        v-model="platformSettings.site_name"
                        type="text"
                        class="form-control"
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Site Description</label>
                      <textarea
                        v-model="platformSettings.site_description"
                        class="form-control"
                        rows="3"
                      ></textarea>
                    </div>

                    <div class="row">
                      <div class="col-md-4 mb-3">
                        <label class="form-label">Primary Color</label>
                        <div class="input-group">
                          <input
                            v-model="platformSettings.primary_color"
                            type="color"
                            class="form-control form-control-color"
                          />
                          <span class="input-group-text">{{ platformSettings.primary_color }}</span>
                        </div>
                      </div>

                      <div class="col-md-4 mb-3">
                        <label class="form-label">Secondary Color</label>
                        <div class="input-group">
                          <input
                            v-model="platformSettings.secondary_color"
                            type="color"
                            class="form-control form-control-color"
                          />
                          <span class="input-group-text">{{
                            platformSettings.secondary_color
                          }}</span>
                        </div>
                      </div>

                      <div class="col-md-4 mb-3">
                        <label class="form-label">Accent Color</label>
                        <div class="input-group">
                          <input
                            v-model="platformSettings.accent_color"
                            type="color"
                            class="form-control form-control-color"
                          />
                          <span class="input-group-text">{{ platformSettings.accent_color }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Support Email</label>
                      <input
                        v-model="platformSettings.support_email"
                        type="email"
                        class="form-control"
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Footer Text</label>
                      <textarea
                        v-model="platformSettings.footer_text"
                        class="form-control"
                        rows="2"
                      ></textarea>
                    </div>

                    <div class="mb-3">
                      <div class="form-check">
                        <input
                          type="checkbox"
                          id="enablePaystack"
                          v-model="platformSettings.enable_paystack"
                          class="form-check-input"
                        />
                        <label class="form-check-label" for="enablePaystack">
                          Enable Paystack Payments
                        </label>
                      </div>
                    </div>

                    <div class="mb-3">
                      <div class="form-check">
                        <input
                          type="checkbox"
                          id="enableAI"
                          v-model="platformSettings.enable_ai_features"
                          class="form-check-input"
                        />
                        <label class="form-check-label" for="enableAI"> Enable AI Features </label>
                      </div>
                    </div>

                    <button type="submit" class="btn btn-primary" :disabled="isSaving">
                      Save Settings
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-show="activeTab === 'users'" class="tab-content">
          <h3 class="mb-4">Registered Users</h3>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Function</th>
                  <th>Joined</th>
                  <th>Verified</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.email }}</td>
                  <td>{{ user.profile?.phone || 'N/A' }}</td>
                  <td>{{ user.profile?.business_function || 'N/A' }}</td>
                  <td>{{ formatDate(user.date_joined) }}</td>
                  <td>
                    <span v-if="user.profile?.is_verified" class="badge badge-success">
                      <i class="fas fa-check"></i>
                    </span>
                    <span v-else class="badge badge-warning">Pending</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCourseStore } from '../stores/store'
import { useSettingsStore } from '../stores/store'
import { useUIStore } from '../stores/store'
import apiClient from '../utils/api_client'

const courseStore = useCourseStore()
const settingsStore = useSettingsStore()
const uiStore = useUIStore()

const activeTab = ref('tracks')
const showTrackForm = ref(false)
const showLessonForm = ref(false)
const isSaving = ref(false)
const users = ref([])

const tracks = computed(() => courseStore.tracks)
const lessons = computed(() => courseStore.lessons)
const platformSettings = computed(() => settingsStore.platformSettings)

const getLessonCount = (trackId) => {
  return lessons.value.filter((l) => l.track === trackId).length
}

const getTrackName = (trackId) => {
  const track = tracks.value.find((t) => t.id === trackId)
  return track?.name || 'Unknown'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const editTrack = (track) => {
  // Open track edit form
  showTrackForm.value = true
}

const deleteTrack = (trackId) => {
  if (confirm('Are you sure you want to delete this track?')) {
    // Call delete API
  }
}

const editLesson = (lesson) => {
  // Open lesson edit form
  showLessonForm.value = true
}

const deleteLesson = async (lessonId) => {
  if (!confirm('Are you sure you want to delete this lesson?')) return
  const lesson = lessons.value.find((item) => item.id === lessonId)
  if (!lesson) return
  try {
    await apiClient.deleteLesson(lesson.track, lessonId)
    courseStore.setLessons(lessons.value.filter((item) => item.id !== lessonId))
    uiStore.setSuccess('Lesson deleted successfully')
  } catch (error) {
    uiStore.setError('Failed to delete lesson')
  }
}

const updateSettings = async () => {
  isSaving.value = true
  try {
    await apiClient.updatePlatformSettings(platformSettings.value)
    settingsStore.setPlatformSettings(platformSettings.value)
    uiStore.setSuccess('Settings updated successfully!')
  } catch (error) {
    uiStore.setError('Failed to update settings')
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  try {
    const [tracksResponse, lessonsResponse, settingsResponse] = await Promise.all([
      apiClient.getTracks(),
      apiClient.getLessons(),
      apiClient.getPlatformSettings(),
    ])
    courseStore.setTracks(tracksResponse.data)
    courseStore.setLessons(lessonsResponse.data)
    settingsStore.setPlatformSettings(settingsResponse.data)
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>

<style scoped>
.admin-panel {
  background: var(--lav);
  padding-top: 0px;
  padding-bottom: 4rem;
}

.admin-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 3rem 0;
  margin-bottom: 3rem;
}

.admin-header h1 {
  font-family: var(--font-poppins);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.nav-tabs {
  border-bottom: 2px solid var(--border-color);
}

.nav-link {
  color: var(--text-secondary);
  border: none;
  border-bottom: 3px solid transparent;
  border-radius: 0;
  padding: 1rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--navy);
  border-bottom-color: var(--secondary-color);
}

.nav-link.active {
  color: var(--secondary-color);
  border-bottom-color: var(--secondary-color);
  background: transparent;
}

.table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.table thead {
  background: var(--lav);
}

.table tbody tr:hover {
  background: rgba(233, 0, 255, 0.05);
}

.card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.form-control-color {
  height: 38px;
}

.input-group .form-control-color {
  border-radius: 8px 0 0 8px;
}

.input-group-text {
  border-radius: 0 8px 8px 0;
  background: var(--lav);
  border: 1px solid var(--border-color);
}
</style>
