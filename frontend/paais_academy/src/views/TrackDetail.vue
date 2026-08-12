<template>
  <div class="track-detail-page" v-if="track">
    <section class="track-hero" :style="{ backgroundColor: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%)' }">
      <div class="container-fluid">
        <div class="row">
          <div class="col-lg-8">
            <h1>{{ track.name }}</h1>
            <p class="lead">{{ track.description }}</p>
            <p class="track-meta">
              <i class="fas fa-book"></i> {{ lessons.length }} Lessons <i class="fas fa-clock"></i>
              {{ totalDuration }} minutes
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="track-content">
      <div class="container-fluid">
        <div class="row">
          <!-- Lessons List -->
          <div class="col-lg-8">
            <div class="lessons-section">
              <h2 class="mb-4">Course Content</h2>
              <div v-for="lesson in lessons" :key="lesson.id" class="lesson-item">
                <div class="lesson-header">
                  <div class="lesson-number">{{ lessons.indexOf(lesson) + 1 }}</div>
                  <div class="lesson-info flex-grow-1">
                    <h5>{{ lesson.title }}</h5>
                    <p class="lesson-meta">
                      <span><i class="fas fa-clock"></i> {{ lesson.duration_minutes }} min</span>
                      <span><i class="fas fa-layer-group"></i> {{ lesson.level }}</span>
                    </p>
                  </div>
                  <div class="lesson-actions">
                    <router-link
                      :to="`/track/${trackId}/lesson/${lesson.id}`"
                      class="btn btn-primary btn-sm"
                    >
                      Start
                    </router-link>
                  </div>
                </div>
                <p class="lesson-description">{{ lesson.description }}</p>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="col-lg-4">
            <div class="sidebar-widget progress-widget">
              <h5>Your Progress</h5>
              <div class="progress-circle">
                <svg viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="90" class="circle-bg"></circle>
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    class="circle-progress"
                    :style="{ strokeDashoffset: 565 - getTrackProgress() * 5.65 }"
                  ></circle>
                </svg>
                <div class="progress-text">
                  <span class="progress-value">{{ getTrackProgress() }}%</span>
                  <span class="progress-label">Complete</span>
                </div>
              </div>
            </div>

            <div class="sidebar-widget certificate-widget mt-4">
              <h5>Certificates Available</h5>
              <div class="certificate-item">
                <i class="fas fa-star"></i>
                <div>
                  <p class="mb-0"><strong>AI Starter</strong></p>
                  <small>Complete first lesson</small>
                </div>
              </div>
              <div class="certificate-item">
                <i class="fas fa-rocket"></i>
                <div>
                  <p class="mb-0"><strong>AI Practitioner</strong></p>
                  <small>Complete 50% of lessons</small>
                </div>
              </div>
              <div class="certificate-item">
                <i class="fas fa-crown"></i>
                <div>
                  <p class="mb-0"><strong>AI Champion</strong></p>
                  <small>Complete all lessons</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
  <div v-else class="loading-page">
    <div class="spinner-border text-primary"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCourseStore } from '../stores/store'
import apiClient from '../utils/api_client'

const props = defineProps({
  trackId: String,
})

const courseStore = useCourseStore()
const track = ref(null)

const lessons = computed(() => courseStore.getLessonsByTrack(props.trackId))

const totalDuration = computed(() => {
  return lessons.value.reduce((sum, l) => sum + (l.duration_minutes || 0), 0)
})

const getTrackProgress = () => {
  if (lessons.value.length === 0) return 0
  const completed = lessons.value.filter((l) => {
    const progress = courseStore.getProgressByLesson(l.id)
    return progress?.status === 'completed'
  }).length
  return Math.round((completed / lessons.value.length) * 100)
}

onMounted(async () => {
  try {
    const [trackResponse, lessonsResponse] = await Promise.all([
      apiClient.getTrackDetail(props.trackId),
      apiClient.getTrackLessons(props.trackId),
    ])
    track.value = trackResponse.data
    courseStore.setCurrentTrack(track.value)
    courseStore.setLessons(lessonsResponse.data)
  } catch (error) {
    console.error('Failed to load track:', error)
  }
})
</script>

<style scoped>
.track-detail-page {
  background: var(--lav);
  padding-top: 0px;
}

.track-hero {
  color: white;
  padding: 3rem 0;
}

.track-hero h1 {
  font-family: var(--font-poppins);
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.track-hero .lead {
  font-size: 1.1rem;
  opacity: 0.9;
}

.track-meta {
  display: flex;
  gap: 2rem;
  opacity: 0.8;
  margin: 0;
}

.track-content {
  padding: 3rem 0;
}

.lessons-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
}

.lesson-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.lesson-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.lesson-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.lesson-number {
  width: 40px;
  height: 40px;
  background: var(--secondary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.lesson-info h5 {
  margin: 0 0 0.5rem 0;
  color: var(--navy);
}

.lesson-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}

.lesson-meta span {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.lesson-description {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.95rem;
}

/* Sidebar */
.sidebar-widget {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.sidebar-widget h5 {
  color: var(--navy);
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.progress-circle {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.progress-circle svg {
  width: 100%;
  height: 100%;
}

.circle-bg {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 8;
}

.circle-progress {
  fill: none;
  stroke: var(--secondary-color);
  stroke-width: 8;
  stroke-dasharray: 565;
  stroke-dashoffset: 0;
  transform: rotate(-90deg);
  transform-origin: 100px 100px;
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-value {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.progress-label {
  display: block;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.certificate-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.certificate-item:last-child {
  border-bottom: none;
}

.certificate-item i {
  font-size: 1.5rem;
  color: var(--secondary-color);
}

.certificate-item p {
  margin: 0;
}

.loading-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
}
</style>
