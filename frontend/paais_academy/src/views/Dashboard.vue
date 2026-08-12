<template>
  <div class="dashboard-page">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <div class="container-fluid dashboard-toolbar">
        <span class="eyebrow">Your learning overview</span>
        <div class="export-actions">
          <button class="btn btn-outline-light btn-sm" type="button" @click="exportDashboard('csv')">Export CSV</button>
          <button class="btn btn-outline-light btn-sm" type="button" @click="exportDashboard('json')">Export JSON</button>
          <button class="btn btn-outline-light btn-sm" type="button" @click="printDashboard">Print</button>
        </div>
      </div>
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-lg-8">
            <h1>Welcome, {{ userProfile?.user?.first_name || userProfile?.user?.username || 'Learner' }}!</h1>
            <p class="subtitle">Continue mastering AI tools for your everyday work</p>
          </div>
          <div class="col-lg-4">
            <div class="stats-card">
              <div class="stat">
                <div class="stat-value">{{ completedLessons }}</div>
                <div class="stat-label">Lessons Completed</div>
              </div>
              <div class="stat">
                <div class="stat-value">{{ certificateCount }}</div>
                <div class="stat-label">Certificates</div>
              </div>
              <div class="stat">
                <div class="stat-value">{{ tracks.length }}</div>
                <div class="stat-label">Available Tracks</div>
              </div>
              <div class="stat">
                <div class="stat-value stat-value-text">{{ dashboardAchievement }}</div>
                <div class="stat-label">Achievement</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Personalized next action -->
    <section v-if="continueLesson" class="continue-section">
      <div class="container">
        <div class="continue-card">
          <div class="continue-icon"><i class="bi bi-play-fill"></i></div>
          <div class="continue-copy">
            <span class="eyebrow">Your next step</span>
            <h2>{{ hasStartedLearning ? 'Continue where you left off' : 'Start your learning journey' }}</h2>
            <p>{{ continueLesson.title }} · {{ continueLesson.duration_minutes }} minutes</p>
            <small v-if="continueLesson.track_name">{{ continueLesson.track_name }}</small>
          </div>
          <router-link
            :to="`/track/${continueLesson.track}/lesson/${continueLesson.id}`"
            class="btn btn-primary"
          >
            {{ hasStartedLearning ? 'Continue Lesson' : 'Start Lesson' }}
            <i class="bi bi-arrow-right ms-2"></i>
          </router-link>
        </div>
        <div v-if="assessmentSummary.total_attempts" class="assessment-summary">
          <span><strong>{{ assessmentSummary.total_attempts }}</strong> assessment attempts</span>
          <span><strong>{{ assessmentSummary.passed_attempts }}</strong> passed</span>
          <span><strong>{{ assessmentSummary.average_score }}%</strong> average score</span>
          <router-link to="/tracks" class="summary-link">Practice more <i class="bi bi-arrow-right"></i></router-link>
        </div>
      </div>
    </section>

    <!-- Progress Charts -->
    <section class="analytics-section">
      <div class="container">
        <div class="row g-4">
          <div class="col-lg-8">
            <div class="analytics-card">
              <div class="analytics-card-header">
                <h3>Track progress</h3>
                <span>{{ tracks.length }} tracks</span>
              </div>
              <div v-if="trackProgressChart.length" class="bar-chart">
                <div v-for="track in trackProgressChart" :key="track.name" class="bar-row">
                  <span class="bar-label">{{ track.name }}</span>
                  <div class="bar-track"><div class="bar-fill" :style="{ width: `${track.progress}%`, backgroundColor: primaryColor }"></div></div>
                  <strong>{{ track.progress }}%</strong>
                </div>
              </div>
              <p v-else class="no-data-message">Track progress will appear as you learn.</p>
            </div>
          </div>
          <div class="col-lg-4">
            <div class="analytics-card">
              <div class="analytics-card-header"><h3>Achievements</h3><i class="bi bi-trophy-fill"></i></div>
              <div class="donut-chart" :style="{ '--primary-chart-color': primaryColor }">
                <div class="donut-total">{{ certificateCount }}<small>certificates</small></div>
              </div>
              <div class="legend-list">
                <span v-for="item in certificateChart" :key="item.level"><i :class="`legend-dot ${item.level}`"></i>{{ formatLevel(item.level) }}: {{ item.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Gamification and recommendations -->
    <section class="gamification-section">
      <div class="container">
        <div class="row g-4">
          <div class="col-lg-4"><div class="analytics-card streak-card"><span class="eyebrow">Consistency</span><strong class="streak-number">{{ gamification?.streak?.current_count || 0 }}</strong><h3>day streak</h3><p>Longest streak: {{ gamification?.streak?.longest_count || 0 }} days</p></div></div>
          <div class="col-lg-8"><div class="analytics-card"><div class="analytics-card-header"><h3>Milestones</h3><span>{{ completedMilestones }} completed</span></div><div class="milestone-grid"><div v-for="milestone in (gamification?.milestones || [])" :key="milestone.code" class="milestone"><i :class="`bi ${milestone.icon}`"></i><div><strong>{{ milestone.name }}</strong><small>{{ milestone.current_value }}/{{ milestone.target_value }}</small><div class="mini-progress"><span :style="{ width: `${milestone.progress_percentage}%` }"></span></div></div></div></div></div></div>
        </div>
        <div v-if="analytics?.recommendations?.length" class="analytics-card recommendations-card mt-4"><div class="analytics-card-header"><h3>Recommended next lessons</h3><span>Based on your progress</span></div><div class="recommendations-list"><router-link v-for="lesson in analytics.recommendations" :key="lesson.id" :to="`/track/${lesson.track}/lesson/${lesson.id}`">{{ lesson.title }} <i class="bi bi-arrow-right"></i></router-link></div></div>
      </div>
    </section>

    <!-- In Progress Courses -->
    <section class="in-progress-section">
      <div class="container">
        <h2 class="section-title">Continue Learning</h2>
        <div v-if="inProgressTracks.length === 0" class="no-data-message">
          <p>No courses in progress. Start by exploring available tracks below!</p>
          <router-link to="/tracks" class="btn btn-link btn-primary btn-outline-light">
            <i class="bi bi-collection-play-fill"></i><span> Available Tracks</span>
          </router-link>
        </div>
        <div v-else class="row g-4">
          <div v-for="track in inProgressTracks" :key="track.id" class="col-lg-6">
            <div class="course-card in-progress">
              <div class="course-header">
                <h4>{{ track.name }}</h4>
                <span class="badge badge-primary">In Progress</span>
              </div>
              <p class="course-description">{{ track.description }}</p>
              <div class="progress-bar-container">
                <div class="progress">
                  <div
                    class="progress-bar"
                    :style="{ width: `${getTrackProgress(track.id)}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ getTrackProgress(track.id) }}% complete</span>
              </div>
              <router-link :to="`/track/${track.id}`" class="btn btn-primary btn-sm mt-3">
                Continue Learning
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/store'
import { useCourseStore, useSettingsStore, useUIStore } from '@/stores/store'
import apiClient from '@/utils/api_client'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

const userStore = useUserStore()
const courseStore = useCourseStore()
const settingsStore = useSettingsStore()
const uiStore = useUIStore()

const dashboardData = ref(null)
const gamification = ref(null)
const analytics = ref(null)
const userProfile = computed(() => userStore.profile)
const completedMilestones = computed(() => (gamification.value?.milestones || []).filter((milestone) => milestone.completed).length)
const continueLesson = computed(() => dashboardData.value?.continue_lesson || null)
const assessmentSummary = computed(() => dashboardData.value?.assessment_summary || {
  total_attempts: 0,
  passed_attempts: 0,
  average_score: 0,
})
const hasStartedLearning = computed(() => (dashboardData.value?.recent_lessons || []).length > 0)
const primaryColor = computed(() => settingsStore.platformSettings.primary_color || 'var(--navy)')

const tracks = computed(() => {
  if (Array.isArray(courseStore.tracks)) return courseStore.tracks
  return courseStore.tracks?.results || []
})

const lessons = computed(() => {
  if (Array.isArray(courseStore.lessons)) return courseStore.lessons
  return courseStore.lessons?.results || []
})

const certificates = computed(() => {
  if (Array.isArray(courseStore.certificates)) return courseStore.certificates
  return courseStore.certificates?.results || []
})

const inProgressTracks = computed(() => {
  return (Array.isArray(tracks.value) ? tracks.value : []).filter((t) => {
    const progress = getTrackProgress(t.id)
    return progress > 0 && progress < 100
  })
})

const getTrackProgress = (trackId) => {
  const trackLessons = (lessons.value || []).filter(
    l => l.track === trackId
  )
  if (trackLessons.length === 0) return 0

  const completedCount = trackLessons.filter((lesson) => {
    const progress = courseStore.getProgressByLesson(lesson.id)
    return progress?.status === 'completed'
  }).length

  return Math.round((completedCount / trackLessons.length) * 100)
}

const exportDashboard = (format) => {
  const report = {
    generated_at: new Date().toISOString(),
    lessons_completed: completedLessons.value,
    certificates: certificateCount.value,
    available_tracks: tracks.value.length,
    achievement: dashboardAchievement.value,
    track_progress: trackProgressChart.value,
  }
  const content = format === 'json'
    ? JSON.stringify(report, null, 2)
    : [
        ['Metric', 'Value'],
        ['Lessons completed', report.lessons_completed],
        ['Certificates', report.certificates],
        ['Available tracks', report.available_tracks],
        ['Achievement', report.achievement],
        [],
        ['Track', 'Progress'],
        ...report.track_progress.map((track) => [track.name, `${track.progress}%`]),
      ].map((row) => row.join(',')).join('\n')
  const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `paais-dashboard.${format === 'json' ? 'json' : 'csv'}`
  link.click()
  URL.revokeObjectURL(url)
  uiStore.setSuccess(`Dashboard exported as ${format.toUpperCase()}`)
}

const printDashboard = () => window.print()

const formatLevel = (level) => ({
  starter: 'AI Starter',
  practitioner: 'AI Practitioner',
  champion: 'AI Champion',
}[level] || level)

const getUserCertificatesByLevel = (level) => {
  return certificates.value.filter((certificate) => certificate.credential_type === level)
}

const completedLessons = computed(() => dashboardData.value?.stats?.total_lessons_completed || 0)
const certificateCount = computed(() => dashboardData.value?.stats?.total_certificates || certificates.value.length)
const dashboardAchievement = computed(() => {
  if (certificates.value.some((certificate) => certificate.credential_type === 'champion')) return 'AI Champion'
  if (certificates.value.some((certificate) => certificate.credential_type === 'practitioner')) return 'AI Practitioner'
  if (certificates.value.some((certificate) => certificate.credential_type === 'starter')) return 'AI Starter'
  return 'Getting started'
})
const trackProgressChart = computed(() => tracks.value.slice(0, 6).map((track) => ({
  name: track.name,
  progress: getTrackProgress(track.id),
})))
const certificateChart = computed(() => ['starter', 'practitioner', 'champion'].map((level) => ({
  level,
  count: getUserCertificatesByLevel(level).length,
})))

onMounted(async () => {
  try {
    // Load tracks
    const tracksResponse = await apiClient.getTracks()
    courseStore.setTracks( tracksResponse.data.results ?? tracksResponse.data)

    // Load lessons
    const lessonsResponse = await apiClient.getLessons()
    courseStore.setLessons(lessonsResponse.data.results ?? lessonsResponse.data)

    // Load certificates
    const certificatesResponse = await apiClient.getCertificates()
    courseStore.setCertificates(certificatesResponse.data.results ?? certificatesResponse.data)

    // Load dashboard data
    const dashboardResponse = await apiClient.getDashboard()
    dashboardData.value = dashboardResponse.data
    const [gamificationResponse, analyticsResponse] = await Promise.all([
      apiClient.getGamification(),
      apiClient.getAnalytics(),
    ])
    gamification.value = gamificationResponse.data
    analytics.value = analyticsResponse.data
    ;(dashboardData.value.recent_lessons || []).forEach((progress) => {
      courseStore.setLessonProgress(progress.lesson, progress)
    })
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
})
</script>

<style scoped>
.dashboard-page {
  background: var(--lav);
  padding-top: 0px;
  padding-bottom: 4rem;
}

/* Welcome Section */
.welcome-section {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 3rem 0;
  margin-top: 0px; /* Account for fixed navbar */
}

.welcome-section h1 {
  font-family: var(--font-poppins);
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.welcome-section .subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0;
}

.stats-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-value {
  font-family: var(--font-poppins);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--cyan);
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-top: 0.5rem;
}

/* Sections */
.in-progress-section,
.analytics-section,
.available-tracks-link-section,
.continue-section {
  padding: 3rem 0;
}

.continue-section {
  padding-top: 2rem;
  padding-bottom: 1rem;
}

.continue-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem 1.75rem;
  background: linear-gradient(135deg, var(--navy), var(--navy-deep));
  color: white;
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(10, 10, 51, 0.18);
}

.continue-icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  flex: 0 0 52px;
  border-radius: 50%;
  background: var(--cyan);
  color: var(--navy);
  font-size: 1.75rem;
}

.continue-copy { flex: 1; }
.continue-copy .eyebrow { color: var(--cyan); }
.continue-copy h2 { margin: 0.25rem 0; font-size: 1.35rem; }
.continue-copy p { margin: 0; opacity: 0.9; }
.continue-copy small { opacity: 0.7; }

.assessment-summary {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1rem 1.25rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}
.assessment-summary strong { color: var(--navy); }
.summary-link { margin-left: auto; color: var(--secondary-color); font-weight: 600; text-decoration: none; }

.dashboard-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.5rem;
}

.section-link-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

@media (max-width: 700px) {
  .section-link-card {
    align-items: stretch;
    flex-direction: column;
  }

  .continue-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .continue-card .btn {
    width: 100%;
  }

  .summary-link {
    margin-left: 0;
  }
}

.dashboard-toolbar .eyebrow {
  color: var(--cyan);
  background: rgba(46, 230, 214, 0.12);
}

.export-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.analytics-card {
  height: 100%;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.analytics-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.analytics-card-header h3 {
  margin: 0;
  color: var(--navy);
  font-size: 1.15rem;
}

.analytics-card-header span {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.bar-chart { display: grid; gap: 1rem; }
.bar-row { display: grid; grid-template-columns: minmax(120px, 1fr) 2fr 48px; gap: 0.75rem; align-items: center; }
.bar-label { overflow: hidden; color: var(--text-secondary); font-size: 0.85rem; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { height: 10px; overflow: hidden; border-radius: 999px; background: var(--lav); }
.bar-fill { height: 100%; min-width: 2px; border-radius: inherit; transition: width 0.3s ease; }
.bar-row strong { color: var(--navy); font-size: 0.8rem; text-align: right; }

.donut-chart {
  display: grid;
  place-items: center;
  width: 150px;
  height: 150px;
  margin: 0 auto 1.25rem;
  border-radius: 50%;
  background: conic-gradient(var(--primary-chart-color) 0 65%, var(--accent-color) 65% 85%, var(--purple) 85% 100%);
}
.donut-chart::before { content: ''; position: absolute; width: 108px; height: 108px; border-radius: 50%; background: white; }
.donut-total { position: relative; z-index: 1; color: var(--navy); font-size: 1.7rem; font-weight: 800; text-align: center; }
.donut-total small { display: block; color: var(--text-secondary); font-size: 0.65rem; font-weight: 500; }
.legend-list { display: grid; gap: 0.45rem; color: var(--text-secondary); font-size: 0.8rem; }
.legend-dot { display: inline-block; width: 9px; height: 9px; margin-right: 0.4rem; border-radius: 50%; background: var(--primary-color); }
.legend-dot.practitioner { background: var(--accent-color); }
.legend-dot.champion { background: var(--purple); }

.stat-value-text { font-size: 1rem; line-height: 1.2; }

@media print {
  .global-sidebar, nav, .export-actions, footer { display: none !important; }
  main.with-sidebar { margin-left: 0; }
}

.section-title {
  font-family: var(--font-poppins);
  font-size: 2rem;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 2rem;
}

.no-data-message {
  text-align: center;
  padding: 3rem 0;
  color: var(--text-secondary);
}

/* Course Cards */
.course-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid var(--secondary-color);
  transition: all 0.3s ease;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.course-header h4 {
  margin: 0;
  color: var(--navy);
}

.course-description {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.progress-bar-container {
  margin-bottom: 1rem;
}

.progress {
  height: 6px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  background: linear-gradient(90deg, var(--secondary-color), var(--accent-color));
  height: 100%;
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 600;
}

/* Track Cards */
.track-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.track-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.track-header {
  padding: 1.5rem;
  color: white;
  min-height: 70px;
  display: flex;
  align-items: center;
}

.track-header h5 {
  color: white;
  margin: 0;
}

.track-body {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.track-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  flex: 1;
}

.track-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Achievement Cards */
.achievement-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.achievement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.achievement-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.ai-starter {
  background: var(--secondary-color);
}

.ai-practitioner {
  background: var(--accent-color);
}

.ai-champion {
  background: #fbbf24;
}

.view-all {
  background: var(--navy);
}

.achievement-card h5 {
  color: var(--navy);
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .welcome-section h1 {
    font-size: 1.75rem;
  }

  .stats-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .filters-bar .form-control {
    max-width: 100% !important;
  }
}
</style>

/* Gamification */
.gamification-section { padding: 0 0 3rem; }
.streak-card { display: flex; flex-direction: column; justify-content: center; min-height: 190px; background: linear-gradient(135deg, var(--navy), var(--navy-deep)); color: white; }
.streak-card .eyebrow { color: var(--cyan); }
.streak-number { margin-top: .5rem; color: var(--cyan); font-size: 3rem; line-height: 1; }
.streak-card h3 { margin: .25rem 0; }
.streak-card p { margin: 0; opacity: .7; }
.milestone-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.milestone { display: flex; gap: .65rem; align-items: flex-start; color: var(--secondary-color); }
.milestone > div { flex: 1; }
.milestone strong, .milestone small { display: block; color: var(--navy); }
.milestone small { margin-top: .2rem; color: var(--text-secondary); font-size: .75rem; }
.mini-progress { height: 6px; margin-top: .5rem; border-radius: 99px; background: var(--lav); overflow: hidden; }
.mini-progress span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--secondary-color), var(--accent-color)); }
.recommendations-list { display: grid; gap: .65rem; }
.recommendations-list a { display: flex; justify-content: space-between; padding: .75rem 1rem; color: var(--navy); background: var(--lav); border-radius: 8px; text-decoration: none; }
.recommendations-list a:hover { color: var(--secondary-color); }
@media (max-width: 700px) { .milestone-grid { grid-template-columns: 1fr; } }
