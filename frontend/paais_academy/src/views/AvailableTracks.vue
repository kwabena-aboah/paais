<template>
  <div class="available-tracks-page">
    <section class="tracks-hero">
      <div class="container">
        <span class="eyebrow">Learning library</span>
        <h1>Available Tracks</h1>
        <p>Choose a practical AI learning path for your role and keep building useful skills.</p>
      </div>
    </section>

    <section class="tracks-content">
      <div class="container">
        <div class="tracks-toolbar">
          <div>
            <h2>Explore every track</h2>
            <p>{{ filteredTracks.length }} track{{ filteredTracks.length === 1 ? '' : 's' }} available</p>
          </div>
          <input v-model="searchQuery" class="form-control" type="search" placeholder="Search tracks..." aria-label="Search tracks" />
        </div>
        <div v-if="filteredTracks.length" class="row g-4">
          <div v-for="track in filteredTracks" :key="track.id" class="col-lg-4 col-md-6">
            <article class="track-card">
              <div class="track-header" :style="{ backgroundColor: primaryColor }">
                <h3>{{ track.name }}</h3>
              </div>
              <div class="track-body">
                <p class="track-description">{{ track.description }}</p>
                <div class="track-meta">
                  <span class="badge badge-info">{{ getLessonCount(track.id) }} Lessons</span>
                  <span v-if="track.price > 0" class="badge badge-success">GHS {{ track.price }}</span>
                  <span v-else class="badge badge-secondary">Free</span>
                </div>
                <router-link :to="`/track/${track.id}`" class="btn btn-primary w-100 mt-3">View Track</router-link>
              </div>
            </article>
          </div>
        </div>
        <div v-else class="empty-state"><i class="bi bi-search"></i><h3>No tracks found</h3><p>Try a different search term.</p></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useCourseStore, useSettingsStore } from '@/stores/store'
import apiClient from '@/utils/api_client'

const courseStore = useCourseStore()
const settingsStore = useSettingsStore()
const searchQuery = ref('')
const primaryColor = computed(() => settingsStore.platformSettings.primary_color || 'var(--navy)')
const tracks = computed(() => Array.isArray(courseStore.tracks) ? courseStore.tracks : courseStore.tracks?.results || [])
const lessons = computed(() => Array.isArray(courseStore.lessons) ? courseStore.lessons : courseStore.lessons?.results || [])
const filteredTracks = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return tracks.value
  return tracks.value.filter((track) => `${track.name || ''} ${track.description || ''}`.toLowerCase().includes(query))
})
const getLessonCount = (trackId) => lessons.value.filter((lesson) => String(lesson.track) === String(trackId)).length

onMounted(async () => {
  try {
    const [tracksResponse, lessonsResponse] = await Promise.all([apiClient.getTracks(), apiClient.getLessons()])
    courseStore.setTracks(tracksResponse.data)
    courseStore.setLessons(lessonsResponse.data)
  } catch (error) {
    console.error('Failed to load available tracks:', error)
  }
})
</script>

<style scoped>
.available-tracks-page { min-height: 100vh; background: var(--lav); }
.tracks-hero { padding: 3rem 0; color: white; background: linear-gradient(135deg, var(--navy), var(--navy-deep)); }
.tracks-hero h1 { margin: 0 0 .5rem; font-size: 2.5rem; }
.tracks-hero p { max-width: 620px; margin: 0; color: rgba(255,255,255,.78); }
.tracks-content { padding: 3rem 0 5rem; }
.tracks-toolbar { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 2rem; }
.tracks-toolbar h2 { margin: 0; color: var(--navy); }
.tracks-toolbar p { margin: .35rem 0 0; color: var(--text-secondary); }
.tracks-toolbar .form-control { max-width: 320px; }
.track-card { height: 100%; overflow: hidden; background: white; border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.08); }
.track-header { min-height: 84px; padding: 1.5rem; color: white; }
.track-header h3 { margin: 0; color: white; font-size: 1.15rem; }
.track-body { display: flex; flex-direction: column; height: calc(100% - 84px); padding: 1.5rem; }
.track-description { flex: 1; color: var(--text-secondary); }
.track-meta { display: flex; flex-wrap: wrap; gap: .5rem; }
.empty-state { padding: 4rem 1rem; text-align: center; color: var(--text-secondary); }
.empty-state i { font-size: 3rem; color: var(--primary-color); }
@media (max-width: 700px) { .tracks-toolbar { align-items: stretch; flex-direction: column; } .tracks-toolbar .form-control { max-width: none; } }
</style>
